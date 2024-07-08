import json
import weakref
from typing import Dict

import anthropic.types
from mistralai.models.chat_completion import ChatMessage
# from typing import Optional

# from pydantic_core import from_json
# from textual.widgets import RichLog
from rich.console import Console, OverflowMethod

# Initialization of Console objects
console: Console = Console()
log_file: Console | None = None


class Logger:
    _instances = weakref.WeakSet()
    global console

    # console: Console = Console()
    # log_file: Console | None = None

    top_left = '╭──'
    top_right = '─╮'
    bottom_left = '╰──'
    bottom_right = '──╯'

    @classmethod
    def log_file(cls, file_name: str) -> None:
        global log_file
        log_file_fn = open(file_name, "wt")
        log_file = Console(file=log_file_fn, width=1000)
        cls.p(f"Logging to: {file_name}")

    @classmethod
    def p(cls, message: str) -> None:
        global console
        global log_file
        console.print(message, soft_wrap=True, overflow="ellipsis")

        if log_file:
            log_file.print(message)

    def ts(self) -> str:

        from datetime import datetime
        ats = datetime.now().strftime("[%H:%M:%S.%f]")
        return f"{ats[:-4]}]"

    def start_step(self, step):
        head = f"[green]{self.namespace:>10}::[/][white]│ [/]"
        self.p(f"{self.ts()}{head}[green]{self.top_left}{'─' * 80}[/]", )

    def stop_step(self, step):
        head = f"{self.ts()}[green]{self.namespace:>10}::[/][white]│ [/]"
        self.p(f"{head}[green]{self.bottom_left}{'─' * 80}[/]")

    def umsg(self, step, msg: dict):
        content = [f"{msg['content']}"]
        head = f"[green]{self.namespace:>10}::[/][white]│ [/][green]│ [/]"
        self.p(f"{self.ts()}{head}[medium_orchid]{msg['role']:>14}[/] [green]{content}[/]")

    def ai_msg(self, step, content: str, stop_reason: str = ''):

        head = f"[green]{self.namespace:>10}::[/][white]│ [/][green]│ [/]"
        txt = content.replace('\n', '\\n')
        self.p(f"{self.ts()}{head}[deep_sky_blue1]{'AI ('+stop_reason+')':>14}[/] [green][{txt}][/]")

    def ai_tool_call(self, step, func_name: str, arg_str: str):

        head = f"[green]{self.namespace:>10}::[/][white]│ [/][green]│ [/]"

        if isinstance(arg_str, str):
            args = json.loads(arg_str)
        else:
            args = arg_str

        fn = f"[deep_sky_blue1]{func_name:>14}[/]"

        func_name_actions = {
            'read_file': lambda: self.p(f"{self.ts()}{head}{fn} ({args['name']})"),
            'write_file': lambda: self.p(f"{self.ts()}{head}{fn} ({args['name']}, ...)[green]{[arg_str]}[/]"),
            'replace': lambda: self.p(f"{self.ts()}{head}{fn} ({args['name']}, ...)[green]{[arg_str]}[/]"),
            'patch': lambda: [self.p(f"{self.ts()}{head}{fn} ({line}, ...)[green]{line[:2]}[/]") for line in
                              args['patch_commands'].split('\n')],
            'exec': lambda: [self.p(f"{self.ts()}{head}{fn} ({line}, ...)[green]{line[:2]}[/]") for line in
                             args['command'].split('\n')],
            'query_db': lambda: [self.p(f"{self.ts()}{head}{fn} ({line}, ...)[green]{line[:2]}[/]") for line in
                                 args['sql'].split('\n')]
        }

        func_name_actions.get(func_name,
                              lambda: self.p(f"{self.ts()}{head}{fn} ({args['filename']}, ...)[green]{[arg_str]}[/]"))()

    def ret_msg(self, step, result: Dict[str, str]):
        head = f"[green]{self.namespace:>10}::[/][white]│ [/][green]│ [/]"
        txt = result['content'].replace('\n', '\\n')
        self.p(f"{self.ts()}{head}[medium_orchid]{'return':>14}[/] [green]{result['name']}:: {txt}[/]")

    def __init__(self, namespace: str, debug: bool = True):
        self.namespace = namespace
        self.debug = debug
        self._instances.add(self)

    def error(self, msg: str, err: Exception):
        trace_back_msg = '\n'
        if err:
            tb = err.__traceback__
            while tb is not None:
                trace_back_msg = f"{trace_back_msg} in {tb.tb_frame.f_code.co_filename}, at line {tb.tb_lineno}\n"
                tb = tb.tb_next
        self.p(f"{self.ts()}[on red]{self.namespace:>10}[/on red]::{msg}{trace_back_msg}")

    def warn(self, msg: str):
        self.p(f"{self.ts()}[bold orange]{self.namespace:>10}::{msg}[/bold orange]")

    def info(self, msg: str):
        if self.debug:
            self.p(f"{self.ts()}{self.namespace:>10}::{msg}")

    @classmethod
    def get_instances(cls):
        return list(cls._instances)

    @classmethod
    def set_namespace(cls, namespace: str, value: str) -> None:
        for instance in cls.get_instances():
            if instance.namespace == namespace:
                instance.debug = (value == 'On')
                return
