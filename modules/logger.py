"""
logger.py

An util script to enable easy color logging and formatting for other file's code simplicity.

Author: DniGamer <dnigamerofficial@gmail.com>

"""

from datetime import datetime
from colorama import Fore

class Logger:
    """
    Logger class

    Used by any file that wants to print colourful messages to the console.
    Each invoked function inside this class has different colors but equal headers.

    """
    def __init__(self, headerEnabled: bool = True):
        self.headerEnabled: bool = headerEnabled
        pass

    def header(self):
        """
        Creates the header for the log lines.
        """
        if self.headerEnabled:
            return str(
                Fore.LIGHTWHITE_EX + f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] ' + Fore.RESET)
        else:
            return ""

    def blue(self, title, message):
        """
        info() returns an blue log message.

        Parameters
        ----------
        title : str
            The title of the log line.
        message : str
            Message to display after the log line
        """
        return print(
            self.header() + Fore.BLUE + f"[{str(title).upper()}] " + Fore.RESET + message)

    def cyan(self, title, message):
        """
        cyan() returns an cyan log message.

        Parameters
        ----------
        title : str
            The title of the log line.
        message : str
            Message to display after the log line
        """
        return print(
            self.header() + Fore.CYAN + f"[{str(title).upper()}] " + Fore.RESET + message)

    def light_green(self, title, message):
        """
        green() returns an light green log line

        Parameters
        ----------
        title : str
            The title of the log line.
        message : str
            Message to display after the log line
        """
        return print(
            self.header() + Fore.LIGHTGREEN_EX + f"[{str(title).upper()}] " + Fore.RESET + message)

    def red(self, title, message):
        """
        error() returns an red log line

        Parameters
        ----------
        title : str
            The title of the log line.
        message : str
            Message to display after the log line
        """
        return print(
            self.header() + Fore.RED + f"[{str(title).upper()}] " + Fore.RESET + message)

    def green(self, title, message):
        """
        success() returns an green log line

        Parameters
        ----------
        title : str
            The title of the log line.
        message : str
            Message to display after the log line
        """
        return print(
            self.header() + Fore.GREEN + f"[{str(title).upper()}] " + Fore.RESET + message)

    def yellow(self, title, message):
        """
        warning() returns an yellow log line

        Parameters
        ----------
        title : str
            The title of the log line.
        message : str
            Message to display after the log line
        """
        return print(
            self.header() + Fore.YELLOW + f"[{str(title).upper()}] " + Fore.RESET + message)
