
import sys
import tty
import termios
import subprocess
import datetime as dt
from time import sleep
from pathlib import Path
from threading import Thread


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
                print(repr(line))
                # print(':: ', line.strip().replace('\r', ''))

    def _rotate(self, backwards: bool = False):
        self._current_index = (self._current_index + (-1 if backwards else 1)) % len(self._containers)

    def _start_log_stream(self):
        yml = Path(__file__).parent / 'src/docker-compose.yml'
        self._log_stream_process = subprocess.Popen(["docker", "compose", "-f", str(yml), "logs", "-f",
                                                     self._current_container.name, "--no-log-prefix"],
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        thread = Thread(target=self._stream_process_output)
        thread.start()

    def _open_shell(self):
        subprocess.run(["make", "shell", "SERVICE=" + self._current_container.name])

    def start(self):
        while True:
            print(f"\033[48;5;250m\033[38;5;0m\n=== Showing logs for: {self._current_container.name} ===\033[0m")
            print(f"\033[48;5;240mPress [Enter] to open shell in {self._current_container.name}.\033[0m")
            print("\033[48;5;240mPress [A] and [D] to rotate through logs, [q] to quit.\033[0m\n")
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
