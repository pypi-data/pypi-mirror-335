import subprocess
import shlex
import os
from typing import List, Union


class CommandExecutor:
    @staticmethod
    def _parse_command(command: str) -> List[str]:
        return shlex.split(command)

    @staticmethod
    def _execute_command(command: str) -> subprocess.CompletedProcess:
        """
        Execute command

        :param command: command to execute
        :return:
        """
        command = CommandExecutor._parse_command(command)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        return result

    @staticmethod
    def execute(command: str, return_statuscode: bool = False) -> Union[int, subprocess.CompletedProcess]:
        result = CommandExecutor._execute_command(command)

        if return_statuscode:
            return result.returncode
        else:
            return result

    @staticmethod
    def change_directory(path: str):
        os.chdir(path)
