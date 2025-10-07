
import os
import sys
import tty
import termios
import subprocess
import datetime as dt
from argparse import ArgumentParser
from functools import cached_property
from pathlib import Path
from threading import Thread
from time import sleep


YML = Path(__file__).parent / 'src/services/docker-compose.yml'


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


class LogLine:
    def __init__(self, timestamp: dt.datetime, text: str):
        self._timestamp = timestamp
        self._text = text

    @property
    def timestamp(self): return self._timestamp
    @property
    def raw(self): return self._text
    @property
    def colorized(self): return self.color + self.raw + ANSICODES.RESET

    @cached_property
    def color(self):
        line_lower = self.raw.lower()
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
        else:
            return ''


class StoppedLogLine(LogLine):
    def __init__(self, timestamp: dt.datetime):
        super().__init__(timestamp, 'stopped')

    @property
    def color(self): return ANSICODES.RED_FG

    @property
    def raw(self):
        terminal_width = os.get_terminal_size().columns
        return f' {self._text} '.center(terminal_width - 10, '-')


class Container:
    @staticmethod
    def from_id(cid: str):
        result = subprocess.run(["docker", "inspect", "--format={{.Name}}", cid], capture_output=True, text=True)
        name = result.stdout.strip().lstrip('/')
        return Container(cid, name)

    @staticmethod
    def from_name(name: str):
        result = subprocess.run(["docker", "inspect", "--format={{.Id}}", name], capture_output=True, text=True)
        cid = result.stdout.strip()
        return Container(cid, name)

    def __init__(self, cid: str, name: str):
        self._cid = cid
        self._name = name
        self._is_running = True
        self._logging_process: subprocess.Popen = NotImplemented  # Process pulling logs
        self._log_polling_thread: Thread = NotImplemented  # Thread processing log lines
        self._log_lines: list[LogLine] = []
        self._log_shown_until = 0  # Index of the last log line shown

    @property
    def cid(self): return self._cid
    @property
    def name(self): return self._name
    @property
    def num_unseen_lines(self): return len(self._log_lines) - self._log_shown_until
    @property
    def is_running(self): return self._is_running

    @property
    def most_urgent_unseen_color(self):
        color_order = [ANSICODES.RED_FG, ANSICODES.YELLOW_FG, ANSICODES.BLUE_FG, ANSICODES.GREEN_FG,
                       ANSICODES.GRAY_FG, '']
        unseen_colors = [ll.color for ll in self._log_lines[self._log_shown_until:]]
        for color in color_order:
            if color in unseen_colors:
                return color
        return ''  # No unseen lines

    def _poll_logs(self):
        last_ps_call = dt.datetime.fromtimestamp(0)
        while isinstance(self._logging_process, subprocess.Popen) and self._logging_process.stdout is not None:
            for line in self._logging_process.stdout:
                self._log_lines.append(LogLine(dt.datetime.now(), line.strip()))
            # - Break if container is not running anymore
            if (dt.datetime.now() - last_ps_call).total_seconds() > 2:
                ps_output = subprocess.run(["docker", "ps", "-q", "-f", f"id={self.cid}"],
                                           capture_output=True, text=True)
                if ps_output.stdout.strip() == '':
                    self._is_running = False
                    self._log_lines.append(StoppedLogLine(dt.datetime.now()))
                    break
                else:
                    last_ps_call = dt.datetime.now()

    def get_log_tail(self, n: int) -> list[LogLine]:
        start = max(0, len(self._log_lines) - n)
        for i, (line, color) in enumerate(zip(self._log_lines[start:], self._log_lines[start:])):
            yield line
            self._log_shown_until = start + i + 1

    def start_collecting_logs(self):
        if isinstance(self._logging_process, subprocess.Popen):
            raise RuntimeError("Logging already started.")
        self._logging_process = subprocess.Popen(["docker", "compose", "-f", str(YML), "logs", "-f",
                                                  self.name, "--no-log-prefix"],
                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self._log_polling_thread = Thread(target=self._poll_logs, daemon=True)
        self._log_polling_thread.start()

    def stop_collecting_logs(self):
        if isinstance(self._logging_process, subprocess.Popen):
            self._logging_process.terminate()
            self._logging_process = NotImplemented
        if isinstance(self._log_polling_thread, Thread):
            self._log_polling_thread.join(timeout=1.0)
            self._log_polling_thread = NotImplemented


class Browser:
    @staticmethod
    def from_running_containers(select_by_names: list[str] = None, update_interval: float = 0.3):
        ps_output = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
        containers = [Container.from_id(cid) for cid in ps_output.stdout.strip().splitlines()]
        if select_by_names is not None:
            containers = [c for c in containers if c.name in select_by_names]
        if len(containers) == 0:
            print("No running containers found.")
            exit()
        return Browser(containers, update_interval)

    @staticmethod
    def from_yml_listed_containers(select_by_names: list[str] = None, update_interval: float = 0.3):
        yml_text = YML.read_text()
        services_text = yml_text.split('services:')[1]
        container_names = [line.removesuffix(':').strip() for line in services_text.splitlines()
                           if line.removeprefix('  ') == line.strip()  # Second level indent only
                           and line.endswith(':') and not line.strip().startswith('#')]
        if select_by_names is not None:
            container_names = [cn for cn in container_names if cn in select_by_names]
        containers = [Container.from_name(name) for name in container_names]
        if len(containers) == 0:
            print("No containers found in docker-compose.yml.")
            exit()
        return Browser(containers, update_interval)

    def __init__(self, containers: list[Container], update_interval: float = 0.3):
        assert len(containers) > 0, "At least one container must be provided."
        self._containers = containers
        self._update_interval = update_interval
        self._start_time = dt.datetime.now()
        self._active_tab_id = 0
        self._instruction_lines = [' Instructions: [A] ↔ [D]  - Switch tabs (containers)',
                                   '               [Space]    - Execute a command this container',
                                   '               [Enter]    - Open a shell in this container',
                                   '               [I]        - Minimize these instructions',
                                   '               [Q]        - Quit this browser']
        self._is_instructions_minimized = True
        self._printer_thread: Thread = Thread(target=self._printer_loop, daemon=True)
        self._last_updated_tabs_bar: dt.datetime = dt.datetime.fromtimestamp(0)
        self._is_printing_paused = False

        class PrintPause:
            def __init__(self, is_in_print_function: bool = False): self._is_in_print_function = is_in_print_function
            def __enter__(slf): self._is_printing_paused = True

            def __exit__(slf, exc_type, exc_val, exc_tb):
                self._is_printing_paused = False
                if not slf._is_in_print_function:  # Avoid recursive calls to _print
                    self._print()

        self._print_pause = PrintPause

    @property
    def _max_log_lines(self): return os.get_terminal_size().lines - 20 + (5 if self._is_instructions_minimized else 0)

    @property
    def active_tab_container(self): return self._containers[self._active_tab_id]

    @property
    def tabs_bar(self):
        tab_names = [container.name for container in self._containers]
        terminal_width = os.get_terminal_size().columns
        # - A Tab will look like this: " 3 container-name " (with colors)  -> 4 extra chars
        if sum(len(tab_name) + 4 for tab_name in tab_names) > terminal_width:
            width_per_tab = terminal_width // len(tab_names)
            container_name_width = width_per_tab - 4
            tab_names = []
            for container in self._containers:
                if len(container.name) <= container_name_width:
                    tab_names.append(container.name)
                else:
                    tab_names.append(container.name[:container_name_width - 1] + '…')
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
            started_line = (f' {self.active_tab_container.name} - Capturing logs since '
                            f'{self._start_time.strftime("%Y-%m-%d %H:%M:%S")}').ljust(terminal_width)
            print(ANSICODES.LIGHT_GRAY_BG + ANSICODES.BLACK_FG + started_line + ANSICODES.RESET, end='\n\r')
            print(ANSICODES.DARK_GRAY_BG + instructions + ANSICODES.RESET, end='\n\r')
            log_lines = self.active_tab_container.get_log_tail(self._max_log_lines)
            current_timestamp: dt.datetime = NotImplemented
            for log_line in log_lines:
                appendix = ''
                if current_timestamp is NotImplemented or (current_timestamp.date() != log_line.timestamp.date()
                                                           and current_timestamp.hour != log_line.timestamp.hour
                                                           and current_timestamp.minute != log_line.timestamp.minute):
                    if current_timestamp is NotImplemented or current_timestamp.date() != log_line.timestamp.date():
                        time_string = log_line.timestamp.strftime("%H:%M")
                    else:
                        time_string = log_line.timestamp.strftime("%Y-%m-%d %H:%M")
                    time_string = f' {time_string} '
                    padding_size = terminal_width - len(time_string) - len(log_line.raw)
                    if padding_size < 0:  # Just give it its own line before the log line
                        print(ANSICODES.LIGHT_GRAY_BG + ANSICODES.BLACK_FG + time_string.rjust(terminal_width)
                              + ANSICODES.RESET, end='\n\r')
                        appendix = ''
                    else:
                        appendix = (' ' * padding_size
                                    + ANSICODES.LIGHT_GRAY_BG + ANSICODES.BLACK_FG + time_string + ANSICODES.RESET)
                print(log_line.colorized + appendix, end='\n\r')
                current_timestamp = log_line.timestamp
            self._last_updated_tabs_bar = dt.datetime.now()

    def _printer_loop(self):
        while isinstance(self._printer_thread, Thread):
            if not self._is_printing_paused:
                # - Update screen if there are new lines in the active tab or if more than 1s passed since last update
                if (self.active_tab_container.num_unseen_lines > 0
                        or (dt.datetime.now() - self._last_updated_tabs_bar).total_seconds() > self._update_interval):
                    self._print()
            # Sleep a bit to avoid busy loop
            sleep(self._update_interval / 5)

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
            with self._print_pause():
                input(f'Got {repr(key)} [acknowledge with Enter]')
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
            container.stop_collecting_logs()
        thread = self._printer_thread
        self._printer_thread = None
        thread.join(timeout=1.)


if __name__ == "__main__":
    parser = ArgumentParser(description='Browse Docker container logs.')
    # A list of container names as first positional arguments, might be empty
    parser.add_argument('containers', nargs='*',
                        help='Names of containers to show (default: all in docker-compose.yml).')
    parser.add_argument('-r', '--running', action='store_true',
                        help='Only show containers if running (default: false).')
    args = parser.parse_args()

    select_by_names = args.containers if len(args.containers) > 0 else None
    if args.running:
        browser = Browser.from_running_containers(select_by_names=select_by_names)
    else:
        browser = Browser.from_yml_listed_containers(select_by_names=select_by_names)
    browser.start()
