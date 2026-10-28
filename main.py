from src.interface import Cli

if __name__ == "__main__":
    command = Cli.parse()
    command.start()
