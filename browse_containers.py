
import os
import sys
import tty
import termios
import subprocess
import datetime as dt
from time import sleep
from pathlib import Path
from threading import Thread


class ANSICODES:
    LIGHT_GRAY_BG = '\033[48;5;250m'
    DARK_GRAY_BG = '\033[48;5;240m'
    BLUE_FG = '\033[38;5;21m'
    BLACK_FG = '\033[30m'
    RED_FG = '\033[31m'
    YELLOW_FG = '\033[33m'
    RESET = '\033[0m'
    CLEAR_SCREEN = '\033[2J\033[H'


def _get_keypress():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key


class Container:
    @staticmethod
    def from_id(cid: str):
        result = subprocess.run(["docker", "inspect", "--format={{.Name}}", cid], capture_output=True, text=True)
        name = result.stdout.strip().lstrip('/')
        return Container(cid, name)

    def __init__(self, cid: str, name: str):
        self.cid = cid
        self.name = name


class Browser:
    def __init__(self):
        self._start_time = dt.datetime.now()
        ps_output = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
        self._containers = [Container.from_id(cid) for cid in ps_output.stdout.strip().splitlines()]
        if len(self._containers) == 0:
            print("No running containers found.")
            exit()
        self._current_index = 0
        self._log_stream_process = None

    @property
    def _current_container(self): return self._containers[self._current_index]

    def _stream_process_output(self):
        while self._log_stream_process is not None and self._log_stream_process.stdout is not None:
            for line in self._log_stream_process.stdout:
                if ("fatal" in line.lower() or "error" in line.lower() or "can't" in line.lower()
                        or "failed" in line.lower() or "no such" in line.lower() or "denied" in line.lower()):
                    print(ANSICODES.RED_FG + line.strip() + ANSICODES.RESET, end='\n\r')
                elif "warn" in line.lower():
                    print(ANSICODES.YELLOW_FG + line.strip() + ANSICODES.RESET, end='\n\r')
                elif "info" in line.lower():
                    print(ANSICODES.BLUE_FG + line.strip() + ANSICODES.RESET, end='\n\r')
                else:
                    print(line, end='\r')

    def _rotate(self, backwards: bool = False):
        self._current_index = (self._current_index + (-1 if backwards else 1)) % len(self._containers)

    def _start_log_stream(self):
        yml = Path(__file__).parent / 'src/docker-compose.yml'
        terminal_height = os.get_terminal_size().lines - 5

        self._log_stream_process = subprocess.Popen(["docker", "compose", "-f", str(yml), "logs", "-f",
                                                     self._current_container.name, "--no-log-prefix", "-n",
                                                     str(terminal_height - 5)],
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        thread = Thread(target=self._stream_process_output, daemon=True)
        thread.start()

    def _open_shell(self):
        subprocess.run(["make", "shell", "SERVICE=" + self._current_container.name])

    def start(self):
        while True:
            print(ANSICODES.CLEAR_SCREEN + ANSICODES.LIGHT_GRAY_BG + ANSICODES.BLACK_FG, end='')
            print(f"=== Showing logs for: {self._current_container.name} ===")
            print(ANSICODES.RESET + ANSICODES.DARK_GRAY_BG, end='')
            print(f"Press [Enter] to open shell in {self._current_container.name}.")
            print("Press [A] and [D] to rotate through logs, [q] to quit.")
            print(ANSICODES.RESET)
            self._start_log_stream()
            key = _get_keypress()
            if key == "q":
                print("Exiting...")
                if self._log_stream_process is not None:
                    self._log_stream_process.terminate()
                    self._log_stream_process = None
                break
            elif key == "a":
                self._rotate(backwards=True)
                print("Rotating to previous container...")
            elif key == "d":
                self._rotate()
                print("Rotating to next container...")
            elif key == "\r":  # Enter key
                if self._log_stream_process is not None:
                    self._log_stream_process.terminate()
                    self._log_stream_process = None
                subprocess.run(["make", "shell", "SERVICE=" + self._current_container.name])  # Blocking call
            else:
                print(f"Unrecognized key: {key}")
            sleep(1)  # Give time for the user to see the exit message


if __name__ == "__main__":
    browser = Browser()
    browser.start()
