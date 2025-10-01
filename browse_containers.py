
import os
import sys
import tty
import termios
import subprocess
import datetime as dt
from pathlib import Path
from threading import Thread
from time import sleep


class ANSICODES:
    LIGHT_GRAY_BG = '\033[48;5;250m'
    DARK_GRAY_BG = '\033[48;5;240m'
    GRAY_FG = '\033[38;5;245m'
    BLUE_FG = '\033[38;5;81m'
    BLACK_FG = '\033[30m'
    RED_FG = '\033[31m'
    YELLOW_FG = '\033[33m'
    GREEN_FG = '\033[32m'
    RESET = '\033[0m'
    CLEAR_SCREEN = '\033[2J\033[H'
    NOTBOLD = '\033[22m'


def _get_keypress():
    # - Get the file descriptor for standard input
    fd = sys.stdin.fileno()
    # - Save original terminal settings
    old_settings = termios.tcgetattr(fd)
    try:
        # - Set terminal to raw mode to capture keypresses immediately
        tty.setraw(fd)
        # - Read a single character
        key = sys.stdin.read(1)
    finally:
        # - Restore original terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key


class Container:
    @staticmethod
    def _fine_color(line: str):
        line_lower = line.lower()
        if any(kw in line_lower for kw in ("info", "notice", "starting", "started", "listening", "listened")):
            return ANSICODES.BLUE_FG
        elif any(kw in line_lower for kw in ("warn", "retrying", "retry", "slow", "slowly")):
            return ANSICODES.YELLOW_FG
        elif any(kw in line_lower for kw in ("error", "fail", "fatal", "panic", "exception", "traceback", "can't",
                                             "denied", "unavailable", "unreachable", "not found", "no such")):
            return ANSICODES.RED_FG
        elif any(kw in line_lower for kw in ("success", "ready", "connected", "completed", "done")):
            return ANSICODES.GREEN_FG
        elif any(kw in line_lower for kw in ("debug", "verbos", "trace", "http", "https", "delete", "request",
                                             "response", "sql", "select", "insert", "inject", "update", "query")):
            return ANSICODES.GRAY_FG

    @staticmethod
    def from_id(cid: str):
        result = subprocess.run(["docker", "inspect", "--format={{.Name}}", cid], capture_output=True, text=True)
        name = result.stdout.strip().lstrip('/')
        return Container(cid, name)

    def __init__(self, cid: str, name: str):
        self._cid = cid
        self._name = name
        self._logging_process: subprocess.Popen = NotImplemented  # Process pulling logs
        self._log_polling_thread: Thread = NotImplemented  # Thread processing log lines
        self._log_lines_raw = []  # All log lines collected so far
        self._log_colors = []  # Color codes for log lines
        self._log_shown_until = 0  # Index of the last log line shown

    @property
    def cid(self): return self._cid
    @property
    def name(self): return self._name
    @property
    def num_unseen_lines(self): return len(self._log_lines_raw) - self._log_shown_until

    def get_log_tail(self, n: int):
        start = max(0, len(self._log_lines_raw) - n)
        for i, (line, color) in enumerate(zip(self._log_lines_raw[start:], self._log_colors[start:])):
            if color is None:
                yield line
            else:
                yield color + line + ANSICODES.RESET
            self._log_shown_until = start + i + 1

    @property
    def most_urgent_unseen_color(self):
        color_order = [ANSICODES.RED_FG, ANSICODES.YELLOW_FG, ANSICODES.BLUE_FG, ANSICODES.GREEN_FG,
                       ANSICODES.GRAY_FG, None]
        unseen_colors = self._log_colors[self._log_shown_until:]
        for color in color_order:
            if color in unseen_colors:
                return color

    def _poll_logs(self):
        while isinstance(self._logging_process, subprocess.Popen) and self._logging_process.stdout is not None:
            for line in self._logging_process.stdout:
                self._log_lines_raw.append(line.strip())
                self._log_colors.append(self._fine_color(line))

    def start_collecting_logs(self):
        if isinstance(self._logging_process, subprocess.Popen):
            raise RuntimeError("Logging already started.")
        yml = Path(__file__).parent / 'src/docker-compose.yml'
        self._logging_process = subprocess.Popen(["docker", "compose", "-f", str(yml), "logs", "-f",
                                                  self.name, "--no-log-prefix"],
                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self._log_polling_thread = Thread(target=self._poll_logs, daemon=True)
        self._log_polling_thread.start()

    def stop_collectng_logs(self):
        if isinstance(self._logging_process, subprocess.Popen):
            self._logging_process.terminate()
            self._logging_process = NotImplemented
        if isinstance(self._log_polling_thread, Thread):
            self._log_polling_thread.join(timeout=1.0)
            self._log_polling_thread = NotImplemented


class Browser:
    def __init__(self):
        self._start_time = dt.datetime.now()
        ps_output = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
        self._containers = [Container.from_id(cid) for cid in ps_output.stdout.strip().splitlines()]
        if len(self._containers) == 0:
            print("No running containers found.")
            exit()
        self._active_tab_id = 0
        self._instruction_lines = [' Instructions: [A] ↔ [D]  - Switch tabs (containers)',
                                   '               [Space]    - Execute a command this container',
                                   '               [Enter]    - Open a shell in this container',
                                   '               [I]        - Minimize these instructions',
                                   '               [Q]        - Quit this browser']
        self._max_log_lines = os.get_terminal_size().lines - 12  # Leave space for tabs, instructions and some buffer
        self._is_instructions_minimized = False
        self._printer_thread: Thread = Thread(target=self._printer_loop, daemon=True)
        self._last_updated_tabs_bar: dt.datetime = dt.datetime.fromtimestamp(0)

        class PrintPause:
            IS_PAUSED = False
            def __init__(self, is_in_print_function: bool = False): self._is_in_print_function = is_in_print_function
            def __enter__(slf): slf.IS_PAUSED = True

            def __exit__(slf, exc_type, exc_val, exc_tb):
                slf.IS_PAUSED = False
                if not slf._is_in_print_function:  # Avoid recursive calls to _print
                    self._print()

        self._print_pause = PrintPause


    @property
    def active_tab_container(self): return self._containers[self._active_tab_id]

    @property
    def tabs_bar(self):
        tab_names = [container.name for container in self._containers]
        terminal_width = os.get_terminal_size().columns
        clipping_needed = sum(len(tab_name) + 4 for tab_name in tab_names) > terminal_width  # +4 for badge and padding
        if clipping_needed:
            available_width = terminal_width - 3 * len(tab_names)  # -3 for padding and ellipsis
            base_width = available_width // len(tab_names)
            tab_names = [tab_name if len(tab_name) <= base_width
                         else tab_name[:max(0, base_width - 1)] + '…'
                         for tab_name in tab_names]
        badges = [(f'{container.most_urgent_unseen_color}'
                   f'{container.num_unseen_lines if container.num_unseen_lines < 10 else "*"}'
                   f'{ANSICODES.RESET}')
                  if container.num_unseen_lines > 0 else ' ' for container in self._containers]
        tabs = [(f' {badge}{ANSICODES.BLACK_FG + ANSICODES.LIGHT_GRAY_BG if i == self._active_tab_id else ""} {name} '
                 f'{ANSICODES.RESET}') for i, (name, badge) in enumerate(zip(tab_names, badges))]
        return ''.join(tabs)

    def _print(self):
        with self._print_pause(is_in_print_function=True):
            terminal_width = os.get_terminal_size().columns
            print(ANSICODES.CLEAR_SCREEN, end='')
            print(self.tabs_bar, end='\n\r')
            if self._is_instructions_minimized:
                instructions = f' [I] to expand instructions...'
            else:
                instructions = '\n\r'.join([line.ljust(terminal_width) for line in self._instruction_lines])
            started_line = f' Started at {self._start_time.strftime("%Y-%m-%d %H:%M:%S")}'.ljust(terminal_width)
            print(ANSICODES.LIGHT_GRAY_BG + ANSICODES.BLACK_FG + started_line + ANSICODES.RESET, end='\n\r')
            print(ANSICODES.DARK_GRAY_BG + instructions + ANSICODES.RESET, end='\n\r')
            for line in self.active_tab_container.get_log_tail(self._max_log_lines):
                print(line, end='\n\r')
            self._last_updated_tabs_bar = dt.datetime.now()

    def _printer_loop(self):
        while isinstance(self._printer_thread, Thread):
            if not self._print_pause.IS_PAUSED:
                # - Update screen if there are new lines in the active tab or if more than 1s passed since last update
                if (self.active_tab_container.num_unseen_lines > 0
                        or (dt.datetime.now() - self._last_updated_tabs_bar).total_seconds() > 1):
                    self._print()
            # Sleep a bit to avoid busy loop
            sleep(0.2)

    def switch_tab(self, backwards: bool = False):
        self._active_tab_id = (self._active_tab_id + (-1 if backwards else 1)) % len(self._containers)

    def prompt_user_in_active_tab(self):
        with self._print_pause():
            inp = input(f'\n{ANSICODES.GRAY_FG}Command to execute -$: ')
            print(ANSICODES.RESET)
            subprocess.run(["docker", "exec", "-it", self.active_tab_container.cid, "sh", "-c", inp])

    def open_shell_in_active_tab(self):
        with self._print_pause():
            subprocess.run(["make", "shell", "SERVICE=" + self.active_tab_container.name])

    def start(self):
        for container in self._containers:
            container.start_collecting_logs()
        self._printer_thread.start()  # Start log updating thread after initial screen print
        while True:
            key = _get_keypress()
            match key:
                case 'q':
                    print(f"\n{ANSICODES.GRAY_FG}Exiting...{ANSICODES.RESET}")
                    break
                case 'a':
                    self.switch_tab(backwards=True)
                    self._print()
                case 'd':
                    self.switch_tab()
                    self._print()
                case 'i':
                    self._is_instructions_minimized = not self._is_instructions_minimized
                    self._print()
                case ' ':  # Space
                    self.prompt_user_in_active_tab()
                    self._print()
                case '\r':  # Enter
                    self.open_shell_in_active_tab()  # Blocking call
                    self._print()
                case _: pass  # Ignore other keys
        for container in self._containers:
            container.stop_collectng_logs()
        thread = self._printer_thread
        self._printer_thread = None
        thread.join(timeout=1.)

if __name__ == "__main__":
    browser = Browser()
    browser.start()
