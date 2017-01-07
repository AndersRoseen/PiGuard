#!/usr/bin/env python3

import os, inspect
#Getting the directory where PiGuard is stored
piguard_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#Changing the working directory to the one where the program is stored
os.chdir(piguard_dir)

from piguardsystem import System


if __name__ == "__main__":
    system = System()

    while system.get_and_execute_command():
        pass

    system.shutdown_servers()
    print("PiGuard Terminated")
