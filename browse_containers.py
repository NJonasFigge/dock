
import os
import sys
import tty
import termios
import subprocess
import datetime as dt
from pathlib import Path
from threading import Thread


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
    BOLD = '\033[1m'
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
        elif any(kw in line_lower for kw in ("debug", "verbose", "trace", "http", "https", "get", "post", "put",
                                             "delete", "request", "response", "sql", "select", "insert", "update",
                                             "query")):
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

    @property
    def all_seen_log_lines(self):
        for line, color in zip(self._log_lines_raw[:self._log_shown_until], self._log_colors[:self._log_shown_until]):
            if color is None:
                yield line
            else:
                yield color + line + ANSICODES.RESET

    @property
    def new_log_lines(self):
        for line, color in zip(self._log_lines_raw[self._log_shown_until:], self._log_colors[self._log_shown_until:]):
            self._log_shown_until += 1
            if color is None:
                yield line
            else:
                yield color + line + ANSICODES.RESET

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

    def start_collecting_logs(self, terminal_height_buffer: int = 5):
        if isinstance(self._logging_process, subprocess.Popen):
            raise RuntimeError("Logging already started.")
        yml = Path(__file__).parent / 'src/docker-compose.yml'
        tail_n = os.get_terminal_size().lines - terminal_height_buffer
        self._logging_process = subprocess.Popen(["docker", "compose", "-f", str(yml), "logs", "-f",
                                                  self.name, "--no-log-prefix", "-n", str(tail_n)],
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
        self._log_printer_thread: Thread = Thread(target=self._print_log, daemon=True)
        self._is_log_printing_paused = False

    @property
    def active_tab_container(self): return self._containers[self._active_tab_id]

    @property
    def tabs_bar(self):
        tabs = []
        for i, container in enumerate(self._containers):
            if i == self._active_tab_id:
                tabs.append(f"{ANSICODES.DARK_GRAY_BG}{ANSICODES.BOLD} ╔ {container.name} ╗ {ANSICODES.RESET}")
            else:
                if self.active_tab_container.num_unseen_lines > 0:
                    badge_color = self.active_tab_container.most_urgent_unseen_color
                    if badge_color is None:
                        badge = f"{ANSICODES.LIGHT_GRAY_BG}{ANSICODES.BLACK_FG}●{ANSICODES.RESET}"
                    else:
                        badge = f"{badge_color}●{ANSICODES.RESET}"
                else:
                    badge = ' '
                tabs.append(f"{ANSICODES.LIGHT_GRAY_BG}{ANSICODES.BLACK_FG}  {container.name} {badge}  "
                            f"{ANSICODES.RESET}")
        return ''.join(tabs)

    def _print_log(self):
        while self._log_printer_thread is not None:
            if not self._is_log_printing_paused:
                line = next(self.active_tab_container.new_log_lines, None)
                if line is not None:
                    print(line)

    def _print_new_screen(self):
        self._is_log_printing_paused = True
        terminal_width = os.get_terminal_size().columns
        print(ANSICODES.CLEAR_SCREEN, end='')
        print(self.tabs_bar)
        print(ANSICODES.DARK_GRAY_BG + '\n'.join([line.ljust(terminal_width) for line in self._instruction_lines])
              + ANSICODES.RESET)
        print(f'{ANSICODES.GRAY_FG}Started at {self._start_time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        print('\n'.join(self.active_tab_container.all_seen_log_lines))
        self._is_log_printing_paused = False

    def switch_tab(self, backwards: bool = False):
        self._active_tab_id = (self._active_tab_id + (-1 if backwards else 1)) % len(self._containers)

    def prompt_user_in_active_tab(self):
        inp = input(f'\n{ANSICODES.GRAY_FG}Command to execute -$: ')
        print(ANSICODES.RESET)
        subprocess.run(["docker", "exec", "-it", self.active_tab_container.cid, "sh", "-c", inp])

    def open_shell_in_active_tab(self):
        subprocess.run(["make", "shell", "SERVICE=" + self.active_tab_container.name])

    def start(self):
        for container in self._containers:
            container.start_collecting_logs()
        self._print_new_screen()
        self._log_printer_thread.start()  # Start log updating thread after initial screen print
        while True:
            key = _get_keypress()
            match key:
                case 'q':
                    print(f"\n{ANSICODES.GRAY_FG}Exiting...{ANSICODES.RESET}")
                    break
                case 'a':
                    self.switch_tab(backwards=True)
                    self._print_new_screen()
                case 'd':
                    self.switch_tab()
                    self._print_new_screen()
                case ' ':  # Space
                    self.prompt_user_in_active_tab()
                case '\r':  # Enter
                    subprocess.run(["make", "shell", "SERVICE=" + self.active_tab_container.name])  # Blocking call
                    self._print_new_screen()
                case _: pass  # Ignore other keys
        for container in self._containers:
            container.stop_collectng_logs()
        thread = self._log_printer_thread
        self._log_printer_thread = None
        thread.join(timeout=1.0)

if __name__ == "__main__":
    browser = Browser()
    browser.start()
