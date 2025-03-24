from . import ClangReplKernel, update_platform_system, is_installed_clang_exist, install_bundles, \
    ClangReplConfig
import platform
import threading
import time


class ClangReplInterface:
    def __init__(self):
        ClangReplKernel.interactive = True
        if not is_installed_clang_exist():
            install_bundles(platform.system())
        ClangReplKernel.ClangReplKernel_InTest = True
        self.kernel = ClangReplKernel()
        self.shell = None
        self.shell = self.kernel.my_shell
        self.kernel.my_shell.run()
        self.execution_count = 0

    def do_execute_sync(self, code):
        return self.kernel.do_execute_sync(code)

    def run_verify(self, codes):
        lines = codes.splitlines()
        last_output = ""
        for line in lines:
            line = line.strip()
            if line.startswith(">>>"):
                line = line[3:].strip()
                if len(line) == 0:
                    continue
                result = self.do_execute_sync(line)
                if result['status'] != 'ok':
                    return result['status'], "Current Output:" + last_output.strip()
                last_output += result['output']
            else:
                if line == 'true' and last_output.strip() == '1':
                    pass
                elif line == 'false' and last_output.strip() == '0':
                    pass
                elif last_output.strip() != line.strip():
                    return "fail", "Expected Output: " + line.strip() + ", Actual Output: " + last_output.strip()
                last_output = ""
        if last_output.strip() == "":
            return 'ok', ''
        else:
            return "fail", "Expected Output: nothing, Actual Output: " + last_output.strip()



