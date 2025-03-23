"""
Module to provide API for the communication with Agilent HPLC systems.

HPLCController sends commands to Chemstation software via a command file.
Answers are received via reply file. On the Chemstation side, a custom
Macro monitors the command file, executes commands and writes to the reply file.
Each command is given a number (cmd_no) to keep track of which commands have
been processed.

Authors: Alexander Hammer, Hessam Mehr, Lucy Hao
"""

import os
import time

from result import Result, Ok, Err
from ..utils.macro import *
from ..utils.method_types import *


class CommunicationController:
    """
    Class that communicates with Agilent using Macros
    """

    # maximum command number
    MAX_CMD_NO = 255

    def __init__(
            self,
            comm_dir: str,
            cmd_file: str = "cmd",
            reply_file: str = "reply",
    ):
        """
        :param comm_dir:
        :param cmd_file: Name of command file
        :param reply_file: Name of reply file
        """
        if os.path.isdir(comm_dir):
            self.cmd_file = os.path.join(comm_dir, cmd_file)
            self.reply_file = os.path.join(comm_dir, reply_file)
            self.cmd_no = 0
        else:
            raise FileNotFoundError(f"comm_dir: {comm_dir} not found.")
        self._most_recent_hplc_status = None

        # Create files for Chemstation to communicate with Python
        open(self.cmd_file, "a").close()
        open(self.reply_file, "a").close()

        self.reset_cmd_counter()

    def get_num_val(self, cmd: str) -> Union[int, float, Err]:
        self.send(Command.GET_NUM_VAL_CMD.value.format(cmd=cmd))
        res = self.receive()
        if res.is_ok():
            return res.ok_value.num_response
        else:
            raise RuntimeError("Failed to get number.")

    def get_text_val(self, cmd: str) -> str:
        self.send(Command.GET_TEXT_VAL_CMD.value.format(cmd=cmd))
        res = self.receive()
        if res.is_ok():
            return res.ok_value.string_response
        else:
            raise RuntimeError("Failed to get string")

    def get_status(self) -> Union[HPLCRunningStatus, HPLCAvailStatus, HPLCErrorStatus]:
        """Get device status(es).

        :return: list of ChemStation's current status
        """
        self.send(Command.GET_STATUS_CMD)
        time.sleep(1)

        try:
            parsed_response = self.receive().value.string_response
            self._most_recent_hplc_status = str_to_status(parsed_response)
            return self._most_recent_hplc_status
        except IOError:
            return HPLCErrorStatus.NORESPONSE
        except IndexError:
            return HPLCErrorStatus.MALFORMED

    def set_status(self):
        """Updates current status of HPLC machine"""
        self._most_recent_hplc_status = self.get_status()

    def check_if_running(self) -> bool:
        """Checks if HPLC machine is in an available state, meaning a state that data is not being written.

        :return: whether the HPLC machine is in a safe state to retrieve data back."""
        self.set_status()
        hplc_avail = isinstance(self._most_recent_hplc_status, HPLCAvailStatus)
        time.sleep(30)
        self.set_status()
        hplc_actually_avail = isinstance(self._most_recent_hplc_status, HPLCAvailStatus)
        return hplc_avail and hplc_actually_avail

    def _send(self, cmd: str, cmd_no: int, num_attempts=5) -> None:
        """Low-level execution primitive. Sends a command string to HPLC.

        :param cmd: string to be sent to HPLC
        :param cmd_no: Command number
        :param num_attempts: Number of attempts to send the command before raising exception.
        :raises IOError: Could not write to command file.
        """
        err = None
        for _ in range(num_attempts):
            time.sleep(1)
            try:
                with open(self.cmd_file, "w", encoding="utf8") as cmd_file:
                    cmd_file.write(f"{cmd_no} {cmd}")
            except IOError as e:
                err = e
                continue
            else:
                return
        else:
            raise IOError(f"Failed to send command #{cmd_no}: {cmd}.") from err

    def _receive(self, cmd_no: int, num_attempts=100) -> Result[str, str]:
        """Low-level execution primitive. Recives a response from HPLC.

        :param cmd_no: Command number
        :param num_attempts: Number of retries to open reply file
        :raises IOError: Could not read reply file.
        :return: Potential ChemStation response
        """
        err = None
        for _ in range(num_attempts):
            time.sleep(1)

            try:
                with open(self.reply_file, "r", encoding="utf_16") as reply_file:
                    response = reply_file.read()
            except OSError as e:
                err = e
                continue

            try:
                first_line = response.splitlines()[0]
                response_no = int(first_line.split()[0])
            except IndexError as e:
                err = e
                continue

            # check that response corresponds to sent command
            if response_no == cmd_no:
                return Ok(response)
            else:
                continue
        else:
            return Err(f"Failed to receive reply to command #{cmd_no} due to {err}.")

    def sleepy_send(self, cmd: Union[Command, str]):
        self.send("Sleep 0.1")
        self.send(cmd)
        self.send("Sleep 0.1")

    def send(self, cmd: Union[Command, str]):
        """Sends a command to Chemstation.

        :param cmd: Command to be sent to HPLC
        """
        if self.cmd_no == self.MAX_CMD_NO:
            self.reset_cmd_counter()

        cmd_to_send: str = cmd.value if isinstance(cmd, Command) else cmd
        self.cmd_no += 1
        self._send(cmd_to_send, self.cmd_no)
        f = open("out.txt", "a")
        f.write(cmd_to_send + "\n")
        f.close()

    def receive(self) -> Result[Response, str]:
        """Returns messages received in reply file.

        :return: ChemStation response 
        """
        num_response_prefix = "Numerical Responses:"
        str_response_prefix = "String Responses:"
        possible_response = self._receive(self.cmd_no)
        if Ok(possible_response):
            lines = possible_response.value.splitlines()
            for line in lines:
                if str_response_prefix in line and num_response_prefix in line:
                    string_responses_dirty, _, numerical_responses = line.partition(num_response_prefix)
                    _, _, string_responses = string_responses_dirty.partition(str_response_prefix)
                    return Ok(Response(string_response=string_responses.strip(),
                                       num_response=float(numerical_responses.strip())))
            return Err(f"Could not retrieve HPLC response")
        else:
            return Err(f"Could not establish response to HPLC: {possible_response}")

    def reset_cmd_counter(self):
        """Resets the command counter."""
        self._send(Command.RESET_COUNTER_CMD.value, cmd_no=self.MAX_CMD_NO + 1)
        self._receive(cmd_no=self.MAX_CMD_NO + 1)
        self.cmd_no = 0

    def stop_macro(self):
        """Stops Macro execution. Connection will be lost."""
        self.send(Command.STOP_MACRO_CMD)
