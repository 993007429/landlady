# encoding: utf-8
import builtins
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def displayhook(value):
    if value is None:
        return
    builtins._ = None  # Set '_' to None to avoid recursion
    builtins._ = value

sys.displayhook = displayhook
del builtins

# Colorize the prompts if possible, Ubuntu tested
sys.ps1 = '\033[1;32m>>>\033[0m '
sys.ps2 = '\033[1;32m...\033[0m '  # for long line break


if __name__ == '__main__':
    try:
        from IPython.terminal.interactiveshell import TerminalInteractiveShell
        shell = TerminalInteractiveShell(user_ns=locals())
        shell.mainloop()
    except ImportError:
        print('WARNING: Loading InteractiveShell failed fall into default shell')
        import code
        shell = code.InteractiveConsole(locals=locals())
        shell.interact()