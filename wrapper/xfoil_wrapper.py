import subprocess as sp
import pandas as pd
import numpy as np
from time import sleep
from pathlib import Path
from helpers.paths import PATHS
from wrapper.data_classes import OperatingConditions
# from pydantic import BaseModel
# from typing import Optional
import os

# TODO: Have the 'base' functions like start, send_command, load, etc. in their own class
# This would neccesitate anothrer class that builds standard processes off of the base methods

class XfoilOperator:

    def __init__(self , print_comms: bool = False, display_graphics: bool = False):

        # Xfoil Options
        self.display_graphics = display_graphics
        self.print_commands = print_comms
        self.iteration_limit: int = 1000
        self.output_file_number: int = 0

        # Paths
        self.wrapper_airfoil_file: Path = PATHS.outputs() / 'wrapper_airfoil.dat'
        self.relative_airfoil_path: Path = os.path.relpath(self.wrapper_airfoil_file, PATHS.ROOT_DIR)

        # Process states
        self.process = None
        self.is_pacc = False
        self.is_oper = False
        self.operating_conds_set = False
        self.graphics_on = True

        # Operating conditions
        self.operating_conditions: OperatingConditions = OperatingConditions()

        # Other
        self.output_directory_cleared = False


class XfoilOperatorText(XfoilOperator):

    def __init__(self, print_comms = False, display_graphics = False):

        super().__init__(print_comms, display_graphics)

        # Add the file that will be written to:
        self.input_commands: str = ""



    def run_xfoil(self) -> None:
        """Builds a text file based on user input, then runs XFOIL as a process. Then post processes the output"""

        # delete log file first
        if not self.output_directory_cleared:
            self.clear_outputs_dir()
            self.output_directory_cleared = True

        if self.display_graphics:
            creation_flag = sp.CREATE_NEW_CONSOLE
        else:
            creation_flag = 0

        if self.process is None or self.process.returncode != 0:
            xfoil_path = PATHS.wrapper() / 'xfoil.exe'
            self.process = sp.run(
                [xfoil_path],
                input = self.input_commands,
                stdout=sp.DEVNULL,
                stderr=sp.DEVNULL,
                text = True,
                creationflags=creation_flag
            )

        # Check if the process executed succesfully
        if self.process.returncode != 0:
            raise RuntimeError("XFOIL process did not run as expected.")


        return

    def write_command(self, command: str):
        """Writes a command to the input file"""



        # Append the command to the input command file:
        if command.endswith('\n'):
            self.input_commands += command
        else:
            self. input_commands += command + "\n"

        if self.print_commands:
            if command.endswith('\n'):
                print(f"\nWriting command: {command}\\n")
            else:
                print(f"\nWriting command: {command}")  # Debugging

        return

    def disable_graphics(self) -> None:
        """Sends a command to disable the graphics output of xfoil"""
        if self.graphics_on:
            self.write_command('PLOP')
            self.write_command('G')
            self.write_command('\n')
            self.graphics_on = False
            return
        else:
            return

    def load_airfoil(self) -> None:
        """Loads an airfoil `.dat` file into XFOIL."""
        relative_airfoil_path = os.path.relpath(self.wrapper_airfoil_file, PATHS.ROOT_DIR)
        # TODO: Convert this to numpy readtext
        dat_file_info = pd.read_csv(self.wrapper_airfoil_file, skiprows=[0], delimiter='\t', skipinitialspace=True, header=None).iloc[:, 1:]
        # Load the airfoil
        self.write_command(f"LOAD {relative_airfoil_path}")
        # If airfoil has more than 150 points, apply paneling
        if len(dat_file_info) > 150:
            self.write_command("PANE")

        return

    def set_oper(self) -> None:
        """Enters operating mode in XFOIL."""

        operating_conditions = self.operating_conditions
        Re = operating_conditions.reynolds_number

        if self.is_oper:
            if self.operating_conds_set:
                return
            else:
                if Re != np.nan:
                    self.write_command(f"v {Re}")  # Set Reynolds number
                else:
                    print("Operating conditions not set, using inviscid analysis")

                self.write_command("iter 1000")
                self.operating_conds_set = True
        else:
            self.write_command("OPER")
            self.write_command("iter 200")   # Set iteration limit
            if not self.operating_conds_set:
                if Re != np.nan:
                    self.write_command(f"v {Re}")  # Set Reynolds number
                else:
                    print("Operating conditions not set, using inviscid analysis")
                self.operating_conds_set = True

        return

    def set_pacc(self) -> None:
        """Enables polar accumulation output to a file."""

        output_file = PATHS.outputs() / ("xfoil_output_" + str(self.output_file_number) + ".txt")
        relative_output_path = os.path.relpath(output_file, PATHS.ROOT_DIR)

        if os.path.exists(output_file):
            if self.print_commands:
                print('removing old pacc file')
            os.remove(output_file)

        self.write_command("PACC")
        self.write_command(str(relative_output_path))
        self.write_command('\n')
        self.is_pacc = True

        self.output_file_number += 1

        return

    def unset_pacc(self) -> None:
        """Disables polar accumulation."""
        if self.is_pacc:
            self.write_command("PACC")
            self.is_pacc = False
        return

    def return_to_xfoil_start(self) -> None:
        """Sends command to quit Xfoil"""
        self.write_command("\n" * 5)
        return

    def quit_xfoil(self) -> None:
        self.write_command("QUIT")
        # reset process state
        self.is_pacc = False
        self.is_oper = False
        self.operating_conds_set = False
        self.graphics_on = True
        self.process = None
        # This pause allows for file writing to complete for some stupid reason
        return

    def clear_outputs_dir(self):
        """Deletes the log file if it exists."""
        target_dir = PATHS.outputs()
        for filename in os.listdir(target_dir):
            if 'output' in filename.split("_"):
                file_path = os.path.join(target_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return

    pass


class StandardOperations(XfoilOperatorText):
    "Class for compacting standard processes into one method"

    def __init__(self, print_comms: bool = False, display_graphics: bool = False):
        super().__init__(print_comms=print_comms, display_graphics=display_graphics)
        return


    def get_LD(self) -> None:
        """
        Gets the lift to drag ratio of the input ariroil at the given operating conditions

        Assumtions:
            - Xfoil has been started and the airfoil has been loaded
            - The operating conditions have been set in Oper menu
            - PACC has been enabled
        """

        conditions = self.operating_conditions

        self.load_airfoil()
        self.disable_graphics()
        self.set_oper()
        self.set_pacc()
        # TODO: have the inc option be set in the optimizer settings
        self.write_command(f"as -1 {conditions.alpha} 0.25")
        self.unset_pacc()
        self.return_to_xfoil_start()
        self.quit_xfoil()
        self.run_xfoil()

        # Reset the input commands for next run:
        self.input_commands = ""

        return


if __name__ == "__main__":

    process = StandardOperations(print_comms=True, display_graphics=False)
    process.operating_conditions.reynolds_number = 5e5
    process.operating_conditions.mach = 0.3
    process.operating_conditions.alpha = 3.0
    process.get_LD()
