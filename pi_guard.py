from piguardsystem import System


if __name__ == "__main__":
    system = System()

    while system.get_and_execute_command():
        pass

    system.shutdown_console_server()
    print("PiGuard Terminated")
