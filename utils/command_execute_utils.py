# -*- coding: utf-8 -*-

import os
import subprocess

from utils.string_utils import StringUtils


class CommandExecuteUtils:
    @staticmethod
    def execute_command(command:str):
        os.system("chcp 65001")
        result = os.system(command)
        return result

    @staticmethod
    def execute_script(script_path:str, script_params:tuple):
        os.system("chcp 65001")
        script_path = StringUtils.replaceBackSlash(script_path)
        if script_params is None or len(script_params) <= 0:
            command_params = [script_path]
        else:
            command_params = [script_path] + list(script_params)
        final_result = True
        try:
            subprocess.run(
                command_params,
                check=True,
                text=True,
                encoding='utf-8',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            print(e)
            final_result = False
        finally:
            return final_result