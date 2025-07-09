import wexpect
import pandas as pd
import os
import pprint
from time import sleep


class XfoilWrapper:
    def __init__(self):
        self.output_file = "xfoil_output.txt"
        self.wrapper_airfoil_file = "wrapper_airfoil.dat"
        self.process = None  # Persistent Xfoil process
        self.is_pacc = False

    def start_xfoil(self):
        """Starts Xfoil as a persistent process."""
        if self.process is None or not self.process.isalive():
            self.process = wexpect.spawn("xfoil.exe", encoding="utf-8", timeout=10)
            self.process.expect("XFOIL Version 6.99")  # Wait for XFOIL to start
            print("XFOIL started successfully.")


    def send_command(self, command: str, expect_output=True):
        """Sends a command to XFOIL while ensuring the process is still alive."""
        if self.process and self.process.isalive():
            self.process.sendline(command)
            if expect_output:
                self.process.expect("\n")  # Wait for a newline (basic expectation)
            if command.find('A ') != -1:
                self.process.expect(".OPERv   c>")
            sleep(0.1)
        else:
            raise RuntimeError("XFOIL process has unexpectedly terminated.")

    def read_output(self):
        output = []
        while True:
            try:
                # Wait for either the XFOIL prompt, EOF, or a newline
                index = self.process.expect([".OPERv   c>", wexpect.EOF, "\r\n"], timeout=10)

                if index == 0:  # Matched ".OPERv   c>"
                    print("Reached XFOIL prompt.")
                    break
                elif index == 1:  # Matched EOF
                    print("XFOIL process ended.")
                    break
                else:  # Matched a newline, so read the next line
                    line = self.process.readline().strip()
                    output.append(line)
                    print(line)  # Debugging: Print output in real-time

            except wexpect.TIMEOUT:
                print("Timeout: XFOIL did not respond in time.")
                break

        return output




    def stop_xfoil(self):
        """Stops Xfoil gracefully."""
        if self.process and self.process.isalive():
            self.send_command("quit", expect_output=False)  # Exit XFOIL
            self.process.close()
            print("XFOIL process stopped.")

    def load_airfoil(self):
        """Loads an airfoil `.dat` file into XFOIL."""
        self.start_xfoil()
        dat_file_info = pd.read_csv(
            self.wrapper_airfoil_file, skiprows=[0], delimiter="\t", skipinitialspace=True, header=None
        ).iloc[:, 1:]

        # Load the airfoil
        self.send_command(f"load {self.wrapper_airfoil_file}")


        # If airfoil has more than 150 points, apply paneling
        if len(dat_file_info) > 150:
            self.process.expect("Try executing PANE at Top Level instead.")  # Wait for prompt to confirm load
            self.send_command("PANE")

        self.process.expect('Bottom side refined')

    def set_oper(self, Re: float):
        """Enters operating mode in XFOIL."""
        self.send_command("OPER")
        self.send_command(f"v {Re}")  # Set Reynolds number
        self.send_command("iter 100")  # Set iteration limit

    def set_pacc(self):
        """Enables polar accumulation output to a file."""
        if os.path.exists(self.output_file):
            os.remove(self.output_file)  # Remove existing file if it exists
        self.send_command("PACC")
        self.send_command(self.output_file)  # File name for polar data
        self.send_command("")  # Empty line to confirm
        self.is_pacc = True

    def get_airfoil_polar_data(self):
        """Finds maximum lift coefficient (Cl_max)."""
        alpha = 0
        ainc = 0.5  # Alpha increment
        cl_max_found = False

        # Dictionary to store polar data
        polar_data = {
            "alpha": [],
            "cl": [],
            "cd": [],
            "cm": [],
            "xtr_top": None,
            "xtr_bot": None,
        }

        while not cl_max_found:
            self.send_command(f"A {alpha}")  # Set angle of attack
            self.process.expect("\n")  # Wait for response
            output = self.read_output()
            for line in output:
                print(line)
            # self.process.terminate()

        #     # Find Cl value from output
        #     found_index = False
        #     line_to_read = -1
        #     cl_old = -0.1

        #     while not found_index:
        #         if "free  transition at x/c" in lines[line_to_read]:
        #             found_index = True
        #             line_to_read -= 1
        #             break
        #         line_to_read -= 1

        #     cl = float(lines[line_to_read + 4].split()[-1])
        #     polar_data["alpha"].append(alpha)
        #     polar_data["cl"].append(cl)
        #     polar_data["cd"].append(float(lines[line_to_read + 5].split()[5]))
        #     polar_data["cm"].append(float(lines[line_to_read + 5].split()[2]))

        #     if cl < cl_old and cl_old > 0:
        #         cl_max_found = True
        #         polar_data["xtr_top"] = float(lines[line_to_read].split()[-2])
        #         polar_data["xtr_bot"] = float(lines[line_to_read + 1].split()[-2])

        #     cl_old = cl
        #     alpha += ainc

        #     pprint.pprint(polar_data)

        # return polar_data
