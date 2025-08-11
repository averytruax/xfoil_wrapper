import subprocess as sp
import pandas as pd
from time import sleep
from helpers.paths import PATHS
from wrapper.data_classes import OperatingConditions
import os

# TODO: Have the 'base' functions like start, send_command, load, etc. in their own class
# This would neccesitate anothrer class that builds standard processes off of the base methods

class XfoilOperator:

    def __init__(self , print_comms: bool = False):

        # Options
        self.print_commands = print_comms

        # Paths

        self.output_file = PATHS.outputs() / "xfoil_output.txt"
        self.wrapper_airfoil_file = PATHS.outputs() / 'wrapper_airfoil.dat'
        self.relative_airfoil_path = os.path.relpath(self.wrapper_airfoil_file, PATHS.ROOT_DIR)
        self.relative_outut_path = os.path.relpath(self.output_file, PATHS.ROOT_DIR)

        # Process states
        self.process = None
        self.is_pacc = False
        self.first_pacc = True
        self.operating_conds_set = False
        self.first_iter_done = False

        # Operating conditions
        self.operating_conditions: OperatingConditions = OperatingConditions()


    def start_xfoil(self) -> None:
        """Starts Xfoil as a persistent process."""

        # delete log file first
        self.delete_log_file()

        if self.process is None or self.process.poll() is not None:
            xfoil_path = PATHS.wrapper() / 'xfoil.exe'
            self.process = sp.Popen(
                [xfoil_path],
                stdin=sp.PIPE,
                # stdout=sp.PIPE,
                stderr=sp.DEVNULL,
                text=True,
                creationflags=0,
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
        self.send_command('PLOP')
        self.send_command('G\n')
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

    def set_oper(self, Re: float, M: float) -> None:
        """Enters operating mode in XFOIL."""
        self.send_command("OPER")
        self.send_command("iter 1000")   # Set iteration limit
        if self.first_iter_done:
            self.send_command('v\n')
        if not self.operating_conds_set:
            self.send_command(f"v {Re}")  # Set Reynolds number
            self.send_command("iter 1000")   # Set iteration limit
        self.operating_conds_set = True

        return

    def set_pacc(self) -> None:
        """Enables polar accumulation output to a file."""
        if os.path.exists('outputs' / self.output_file) and self.first_pacc:
            if self.print_commands:
                print('removing old pacc file')
            os.remove('outputs' / self.output_file)
        self.first_pacc = False  # Only remove the file on the first call

        if self.first_iter_done:
            self.send_command(f"PACC\n{self.relative_outut_path}\ny\n")
            self.is_pacc = True
        else:
            self.send_command(f"PACC\n{self.relative_outut_path}\n")
            self.is_pacc = True

        return

    def unset_pacc(self) -> None:
        """Disables polar accumulation."""
        if self.is_pacc:
            self.send_command("PACC")
            self.is_pacc = False
        return

    def quit_xfoil(self) -> None:
        """Sends command to quit Xfoil"""
        self.send_command("\n\n\nquit")
        # reset process state
        self.process = None
        self.is_pacc = False
        self.first_pacc = True
        self.operating_conds_set = False
        self.first_iter_done = False
        # This pause allows for file writing to complete for some stupid reason
        sleep(0.05)
        return

    def delete_log_file(self):
        """Deletes the log file if it exists."""
        log_file_path = PATHS.outputs() / "xfoil_commands.log"
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
        return

    def get_airfoil_polar_data(self, Re: float, M: float):
        """Finds maximum lift coefficient (Cl_max)."""
        alpha : float = 0
        alpha_step: float = 0.5
        ainc : float = alpha_step / 10  # Alpha increment
        cl_max_found = False
        alpha_old : float = -1
        sleep_time : float = 2

        # Initialize dictionary where data will be stored
        polar_data = {
            'alpha': [],
            'cl': [],
            'cd': [],
            'cm': [],
            'xtr_top': None,
            'xtr_bot': None
        }

        cl_max_found = False
        cl_peak = -float('inf')
        alpha_peak = None

        while not cl_max_found:
            file_updated = False
            time_slept = 0
            self.load_airfoil()
            self.disable_graphics()
            self.set_oper(Re, M)
            self.set_pacc()
            self.send_command("AS")  # Set angle of attack
            self.send_command(f'{alpha}')
            self.send_command(f'{alpha + alpha_step - ainc}')
            self.send_command(f'{ainc}')
            sleep(sleep_time)
            self.unset_pacc()
            self.quit_xfoil()

            if not self.first_iter_done:
                sleep(0.15)

            while not file_updated:
                with open('outputs/'+self.output_file, 'r') as file:
                    output = file.readlines()
                    line_info = output[-1].split()
                    try:
                        float(line_info[0])
                        if float(line_info[0]) == alpha_old:
                            print('The file has not been updated yet, sleeping...')
                            sleep_time += 1
                            break
                        elif sleep_time > 10:
                            raise RuntimeError("Check the convergence of XFOIL")
                        else:
                            print('File updated')
                            file_updated = True
                            sleep_time = 2
                    except:
                        break

            if file_updated:
                polar_data['alpha'].append(alpha)
                polar_data['cl'].append(float(line_info[1]))
                polar_data['cd'].append(float(line_info[2]))
                polar_data['cm'].append(float(line_info[4]))



                # Track the highest CL value and its corresponding alpha
                if alpha > 5 and self.first_iter_done == True:
                    num_inst_found = 0
                    tick = -1
                    for i in range(int(alpha_step/ainc)):
                        if polar_data['cl'][tick-1] > polar_data['cl'][-1]:
                            num_inst_found += 1
                            tick -= 1
                        else:
                            num_inst_found = 1
                            tick = -1

                        if num_inst_found == 3:
                            cl_max_found = True
                            polar_data['cl_max'] = max(polar_data['cl'])
                            polar_data['alpha_max'] = polar_data['alpha'].index(max(polar_data['cl']))
                            polar_data['xtr_top'] = float(line_info[4])
                            polar_data['xtr_bot'] = float(line_info[5])
                            break


                alpha_old = float(line_info[0])
                alpha += alpha_step
                self.first_iter_done = True

        return polar_data


class StandardOperations(XfoilOperator):
    "Class for compacting standard processes into one method"

    def __init__(self, print_comms: bool = False):
        super().__init__(print_comms=print_comms)
        return

    def setup_run_state(self):
        """
        Runs the following process:
            -Load airfoil and repanels if needed
            -Sets the operating conditions for the run
            -Sets polar accumulation mode

        """

        conditions = self.operating_conditions

        self.start_xfoil()
        self.load_airfoil()
        self.disable_graphics()
        self.set_oper(conditions.reynolds_number, conditions.mach)
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

        self.send_command(f"a {conditions.alpha}")
        self.unset_pacc()
        self.quit_xfoil()






