import json
import weakref
from typing import Dict, Optional
from rich.console import Console

class Logger:
    _instances = weakref.WeakSet()
    _console: Optional[Console] = None
    _log_file: Optional[Console] = None

    top_left = '╭──'
    top_right = '─╮'
    bottom_left = '╰──'
    bottom_right = '──╯'

    def __init__(self, namespace: str, debug: bool = True):
        self.namespace = namespace
        self.debug = debug
        self._instances.add(self)
        if Logger._console is None:
            Logger._console = Console()

    @classmethod
    def set_log_file(cls, log_file_name: str) -> None:
        log_file_fn = open(log_file_name, "wt")
        cls._log_file = Console(file=log_file_fn, width=1000, force_terminal=True)
        cls.print(f"Logging to: {log_file_name}")

    @classmethod
    def print(cls, message: str) -> None:
        cls._console.print(message, soft_wrap=True, overflow="ellipsis")
        if cls._log_file:
            cls._log_file.print(message, soft_wrap=True, overflow="ellipsis")

    def ts(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("[%H:%M:%S.%f]")[:-3] + "]"

    def _format_step(self) -> str:
        return f"[green]{self.namespace:>10}::[/][white]│ [/]"

    def _format_head(self) -> str:
        return f"{self._format_step()}[green]│ [/]"

    def start_step(self, step):
        self.print(f"{self.ts()}{self._format_step()}[green]{self.top_left}{'─' * 80}[/]")

    def stop_step(self, step):
        self.print(f"{self.ts()}{self._format_step()}[green]{self.bottom_left}{'─' * 80}[/]")

    def umsg(self, step, msg: dict):
        color = 'medium_orchid'
        role = 'user'
        if msg['role'] == 'system':
            role = 'system'
            color = 'yellow'
        content = msg['content'].replace('\n', '\\n')
        self.print(f"{self.ts()}{self._format_head()}[{color}]{role:>14}[/] [green]{content}[/]")

    # def smsg(self, step, msg: dict):
    #     content = msg['content'].replace('\n', '\\n')
    #     self.print(f"{self.ts()}{self._format_head()}[yellow]{'system':>14}[/] [green]{content}[/]")

    def ai_msg(self, step, content: str, stop_reason: str = ''):
        txt = content.replace('\n', '\\n')
        self.print(f"{self.ts()}{self._format_head()}[deep_sky_blue1]{'AI ('+stop_reason+')':>14}[/] [green][{txt}][/]")

    def ai_tool_call(self, step, func_name: str, arg_str: str):
        args = json.loads(arg_str) if isinstance(arg_str, str) else arg_str
        fn = f"[deep_sky_blue1]{func_name:>14}[/]"

        func_actions = {
            'read_file': lambda: f"({args['name']})",
            'write_file': lambda: f"({args['name']}, ...)[green]{[arg_str]}[/]",
            'replace': lambda: f"({args['name']}, ...)[green]{[arg_str]}[/]",
            'patch': lambda: f"({args['patch_commands'][:50]}...)",
            'exec': lambda: f"({args['command'][:50]}...)",
            'query_db': lambda: f"({args['sql'][:50]}...)",
            'ask_user': lambda: f"({args['question'][:50]}...)"
        }

        action_result = func_actions.get(func_name, lambda: f"({args.get('filename', '')}, ...)[green]{[arg_str]}[/]")()
        self.print(f"{self.ts()}{self._format_head()}{fn} {action_result}")

    def ret_msg(self, step, result: Dict[str, str]):
        txt = result['content'].replace('\n', '\\n')
        self.print(f"{self.ts()}{self._format_head()}[medium_orchid]{'return':>14}[/] [green]{result['name']}:: {txt}[/]")

    def error(self, msg: str, err: Optional[Exception] = None):
        trace_back_msg = self._format_traceback(err) if err else ''
        self.print(f"{self.ts()}[on red]{self.namespace:>10}[/on red]::{msg}{trace_back_msg}")

    def warn(self, msg: str):
        self.print(f"{self.ts()}[bold orange]{self.namespace:>10}::{msg}[/bold orange]")

    def info(self, msg: str):
        if self.debug:
            self.print(f"{self.ts()}{self.namespace:>10}::{msg}")

    def ai_asks(self, msg: str) -> str:
        return self._console.input(f"{self.ts()}{self._format_head()}[medium_orchid]{'Input':>14}[/] [green]")

    @classmethod
    def set_namespace_debug(cls, namespace: str, value: bool) -> None:
        for instance in cls._instances:
            if instance.namespace == namespace:
                instance.debug = value
                return

    @staticmethod
    def _format_traceback(err: Exception) -> str:
        trace_back_msg = '\n'
        tb = err.__traceback__
        while tb is not None:
            trace_back_msg += f" in {tb.tb_frame.f_code.co_filename}, at line {tb.tb_lineno}\n"
            tb = tb.tb_next
        return trace_back_msg