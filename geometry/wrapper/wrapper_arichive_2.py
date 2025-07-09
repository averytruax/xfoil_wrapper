import pandas as pd
import subprocess
from typing import Self
from time import sleep

class xfoil_actions:
    def __init__(self):
        pass

    def xf_command(self, argument : str):
        process = subprocess.Popen(
            ['xfoil.exe'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
            text=True
        )

        process.stdin.write(argument)
        process.stdin.close()

        # Wait for the process to complete and capture the output
        stdout, stderr = process.communicate()

        # Optionally, print the output for debugging
        print(stdout)
        print(stderr)

        return process

class xfoil_wrapper:

    def __init__(self):
        self.output_file = 'xfoil_output'
        self.wrapper_airfoil_file = 'wrapper_airfoil.dat'
        self.execute = xfoil_actions()
        self.close_process_str = '\n\n\nquit'

    def load_airfoil(self) -> None:
        """
        Loads an airfoil `.dat` file into XFOIL and applies necessary repairs if needed.
        
        Parameters:
            None
        Returns:
            None
        """
        # Read the airfoil data file into a DataFrame
        dat_file_info = pd.read_csv('wrapper_airfoil.dat', skiprows=[0], delimiter='\t', skipinitialspace=True, header=None).iloc[:, 1:]
        
        # Prepare the commands to be sent to XFOIL
        commands = f"load\n{self.wrapper_airfoil_file}\n"
        if len(dat_file_info) > 150:
            commands += "PANE\n"
        
        # Send commands to XFOIL
        self.execute.xf_command(commands)
        
        return None
    
    def set_oper(self) -> None:
        """
        Enters operating mode in XFOIL.

        Parameters:
            None
        Returns:
            None
        """
        self.execute.xf_command('oper\n')
        return None
    
    def set_pacc(self) -> None:
        """
        Sets the output file for XFOIL results.
        
        Parameters:
            fid (file object): File descriptor for communication with XFOIL.
        
        Returns:
            None
        """
        commands = f"pacc\n{self.output_file}\n\na 0\n{self.close_process_str}"
        self.execute.xf_command(commands)
        return None
    
    def get_airfoil_polar_data(self, Re: float) -> None:
        """
        Retrieves the maximum lift coefficient (Cl) from the XFOIL output.
        
        Parameters:
            fid (file object): File descriptor for communication with XFOIL.
        
        Returns:
            tuple: (Max alpha , Cl_max).
        # """
        alpha = 0
        ainc = 0.1
        cl_max_found = False
        self.input_file.write(f'v\n{str(Re)}\niter\n100\n')
        self.input_file.write(f'a\n{str(alpha)}\na\n{str(alpha+ainc)}')
        xfoil_actions.run_xfoil(self.input_file)
        while not cl_max_found:
            sleep(1)
            xfoil_actions.run_xfoil(self.input_file)
            with open(self.output_file, 'r') as file:
                lines = file.readlines()
                for idx , line in enumerate(lines):
                    if line.find('alpha') != -1:
                        start_idx = idx
                        break
                cl_prev = float(lines[start_idx+2].split()[1])
                for idx , line in enumerate(lines[start_idx+2:]):
                    cl_dif = float(line.split()[1]) - cl_prev
                    if cl_dif < 0 and cl_prev > 0:
                        cl_max_found = True
                        return (float(line.split()[0]),float(line.split()[1]))
            alpha += ainc
            self.input_file.write(f'a\n{str(alpha)}')
                

    

                    
        
