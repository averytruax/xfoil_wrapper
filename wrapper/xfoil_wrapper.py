import subprocess as sp
import pandas as pd
import numpy as np
from time import sleep
from pathlib import Path
from helpers.paths import PATHS
from wrapper.data_classes import OperatingConditions
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


    def start_xfoil(self) -> None:
        """Starts Xfoil as a persistent process."""

        # delete log file first
        self.clear_outputs_dir()

        if self.display_graphics:
            creation_flag = sp.CREATE_NEW_CONSOLE
        else:
            creation_flag = 0

        if self.process is None or self.process.poll() is not None:
            xfoil_path = PATHS.wrapper() / 'xfoil.exe'
            self.process = sp.Popen(
                [xfoil_path],
                stdin=sp.PIPE,
                stdout=None,
                stderr=None,
                text=True,
                creationflags=creation_flag,
            )

        sleep(0.05)

        return

    def send_command(self, command: str):
        """Sends a command to XFOIL while ensuring the process is still alive."""

        outputs_path = PATHS.outputs()
        if self.process and self.process.poll() is None:  # Ensure XFOIL is running
            if self.print_commands:
                print(f"\nSending command: {command}")  # Debugging
            with open(outputs_path / "xfoil_commands.log", "a") as log_file:
                log_file.write(command + "\n")  # Log the command
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

        else:
            raise RuntimeError("XFOIL process has unexpectedly terminated.")

        return

    def disable_graphics(self) -> None:
        """Sends a command to disable the graphics output of xfoil"""
        if self.graphics_on:
            self.send_command('PLOP')
            self.send_command('G\n')
            self.graphics_on = False
            return
        else:
            return

    def read_output(self):
        """Stops the subprocess and reads the output"""
        output, stderr = self.process.communicate()
        self.process = None
        return output , stderr

    def load_airfoil(self) -> None:
        """Loads an airfoil `.dat` file into XFOIL."""
        relative_airfoil_path = os.path.relpath(self.wrapper_airfoil_file, PATHS.ROOT_DIR)
        # TODO: Convert this to numpy readtext
        dat_file_info = pd.read_csv(self.wrapper_airfoil_file, skiprows=[0], delimiter='\t', skipinitialspace=True, header=None).iloc[:, 1:]
        # Load the airfoil
        self.send_command(f"LOAD {relative_airfoil_path}")
        # If airfoil has more than 150 points, apply paneling
        if len(dat_file_info) > 150:
            self.send_command("PANE")

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
                    self.send_command(f"v {Re}")  # Set Reynolds number
                else:
                    print("Operating conditions not set, using inviscid analysis")

                self.send_command("iter 1000")
                self.operating_conds_set = True
        else:
            self.send_command("OPER")
            self.send_command("iter 1000")   # Set iteration limit
            if not self.operating_conds_set:
                self.send_command('v\n')
                if Re != np.nan:
                    self.send_command(f"v {Re}")  # Set Reynolds number
                else:
                    print("Operating conditions not set, using inviscid analysis")
                self.send_command("iter 1000")   # Set iteration limit
                self.operating_conds_set = True

        return

    def set_pacc(self) -> None:
        """Enables polar accumulation output to a file."""

        output_file = PATHS.outputs() / ("xfoil_output_" + str(self.output_file_number) + ".txt")
        relative_output_path = os.path.relpath(output_file, PATHS.ROOT_DIR)

        if os.path.exists(output_file):
            if self.print_commands:
                print('removing old pacc file')
            os.remove(self.output_file)

        self.send_command(f"PACC\n{relative_output_path}\n")
        self.is_pacc = True

        self.output_file_number += 1

        return

    def unset_pacc(self) -> None:
        """Disables polar accumulation."""
        if self.is_pacc:
            self.send_command("PACC")
            self.is_pacc = False
        return

    def return_to_xfoil_start(self) -> None:
        """Sends command to quit Xfoil"""
        self.send_command("\n" * 5)
        self.send_command("QUIT")
        # reset process state
        self.is_pacc = False
        self.is_oper = False
        self.operating_conds_set = False
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


class StandardOperations(XfoilOperator):
    "Class for compacting standard processes into one method"

    def __init__(self, print_comms: bool = False, display_graphics: bool = True):
        super().__init__(print_comms=print_comms, display_graphics=display_graphics)
        return


    def setup_run_state(self):
        """
        Runs the following process:
            -Load airfoil and repanels if needed
            -Sets the operating conditions for the run
            -Sets polar accumulation mode

        """


        self.load_airfoil()
        self.disable_graphics()
        self.set_oper()
        self.set_pacc()

        return

    def run_condition(self):

        process = self.process

        process.send_command()


    def get_LD(self) -> None:
        """
        Gets the lift to drag ratio of the input ariroil at the given operating conditions

        Assumtions:
            - Xfoil has been started and the airfoil has been loaded
            - The operating conditions have been set in Oper menu
            - PACC has been enabled
        """

        conditions = self.operating_conditions

        self.send_command(f"as 0 {conditions.alpha} 0.5")
        self.unset_pacc()
        self.return_to_xfoil_start()






