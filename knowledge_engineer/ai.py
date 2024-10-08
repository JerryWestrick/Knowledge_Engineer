import asyncio
import json
import os
import platform
import pprint
import subprocess
import sys
from abc import abstractmethod

import anthropic
import httpx
from groq import AsyncGroq

from anthropic import AsyncAnthropic

from dotenv import load_dotenv
from httpx import ReadTimeout
# from litellm import max_tokens
from mistralai import Mistral as AsyncMistral
from openai import AsyncOpenAI
from rich.panel import Panel
from rich.text import Text
# from rich.console import Console
from rich import print
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
# from sqlalchemy import false

from .AI_API_Costs import AI_API_Costs
from .db import DB
from .logger import Logger
from databases import Database

import traceback

load_dotenv()
load_dotenv('ke_process_config.env')


async def succeed(d: dict):
    return d


os_descriptor = platform.platform()


def make_error_msg(err: Exception):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    filename = traceback.extract_tb(exc_traceback, limit=1)[0][0]  # Gets filename
    line_number = traceback.extract_tb(exc_traceback, limit=1)[0][1]  # Gets line number
    return f'{err} At {filename}::{line_number}'


class AIException(Exception):
    pass


class AI:
    log = Logger(namespace='AI', debug=True)

    memory = DB()

    ai_log_filename: str = None

    def log_ai(self, txt: str, obj ):
        if type(obj) is str:
            obj = json.loads(obj)

        t = {"Action": txt, "Object": obj }
        try:
            t_str = json.dumps(t, indent=4, sort_keys=True, default=str)

            with open(self.ai_log_filename, 'a') as file:
                file.write(f",{t_str}\n")

        except Exception as e:
            print(f"An error occurred while appending text to the file: {e}")


    def __init__(self, llm_name: str, model: str = "gpt-3.5-turbo-1106",
                 temperature: float = 0, max_tokens: int = 4000,
                 mode: str = 'complete', response_format=None, debug: bool = False):
        self.answer: str = ''
        self.llm_name: str = llm_name
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        self.model: str = model
        self.mode: str = mode
        self.messages = []
        self.response_format = response_format
        self.files = {}
        self.e_stats = {
            'prompt_tokens': 0.0,
            'completion_tokens': 0.0,
            'total_tokens': 0.0,
            'sp_cost': 0.0,
            'sc_cost': 0.0,
            's_total': 0.0,
            'elapsed_time': 0.0,
        }
        self.db: Database | None = None
        self.client = None
        self.debug: bool = debug

    @abstractmethod
    def function_role(self) -> str:
        pass

    # @abstractmethod
    # def function_result(self, name: str, content: str):
    #     pass

    async def query_db_ai(self, sql: str, process_name: str):

        if self.db is None:
            self.db = Database(os.getenv('KE_PROC_DB_URL'))
            await self.db.connect()

        # self.log.info(f"About to Query Database: {sql}")
        if sql.lower().startswith('select'):
            try:
                result = await self.db.fetch_all(query=sql)
            except Exception as err:
                self.log.error(f"{err}", err)
                result = [{'error': err}]
                raise err
            result_as_dict = [dict(row) for row in result]
            return await succeed({'role': self.function_role(), 'name': 'query_db', 'content': str(result_as_dict)})

        result = await self.db.execute(query=sql)
        # self.log.info(f"Database Update Result: {result}")
        return await succeed({'role': self.function_role(), 'name': 'execute_db', 'content': str(result)})

    async def readfile(self, filename: str, process_name: str):

        try:
            file_contents = self.memory.read(filename, process_name=process_name)

        except Exception as err:
            self.log.error(f"Error while reading file for AI... ", err)
            result = await succeed({'role': self.function_role(),
                                    'name': 'read_file',
                                    'content': f'ERROR file not found: {filename}'
                                    })
            return result

        return await succeed({'name': 'read_file', 'content': file_contents})

    async def get_webpage_content(self, url: str) -> str:
        # Command to fetch the content and convert it to text
        command = f"wget2 --content-on-error -O - {url} | html2text"
        # .\wget2.exe - O - "https://openai.com/api/pricing/" | html2text.exe

        # Create a subprocess
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for the subprocess to finish and get output
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            # If there was an error, raise an exception with the error message
            raise Exception(f"Error fetching URL: {stderr.decode()}")

        # Return the output as a string
        return stdout.decode()



    async def www_get(self, url: str, process_name: str):

        try:
            page_contents = await self.get_webpage_content(url)
        except Exception as err:
            self.log.error(f"Error while retrieving url for AI... ", err)
            result = {'role': self.function_role(),
                    'name': 'www_get',
                    'content': f'ERROR url not returned: {url}'
                    }
            return result

        return await succeed({'name': 'www_get', 'content': page_contents})

    async def readfile(self, filename: str, process_name: str):

        try:
            file_contents = self.memory.read(filename, process_name=process_name)

        except Exception as err:
            self.log.error(f"Error while reading file for AI... ", err)
            result = await succeed({'role': self.function_role(),
                                    'name': 'read_file',
                                    'content': f'ERROR file not found: {filename}'
                                    })
            return result

        return await succeed({'name': 'read_file', 'content': file_contents})

    async def writefile(self, filename: str, content: str, process_name: str):
        full_name = filename
        try:
            self.memory[full_name] = content
        except Exception as err:
            err_msg = f"Error while writing file for AI... "
            self.log.error(err_msg, err)
            raise err

        return await succeed({'role': self.function_role(), 'name': 'writefile', 'content': 'Done.'})

    def exec_subprocess(self, command: str) -> str:
        """Execute a local command and return its output in a message structure"""

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        txt = ''
        if output:
            txt = f"{txt}{output.decode('utf-8')}"
        if error:
            txt = f"{txt}Error: {error.decode('utf-8')}"

        return txt

    async def execute_cmd_prompt(self, command: str, process_name: str) -> dict[str, str]:
        """Execute a command that was defined in a prompt file (.kepf)"""

        function_name, args = command.split('(', maxsplit=1)
        args = args[:-1]
        args_list = args.split(",")
        function_args = {}
        for arg in args_list:
            name, value = arg.split("=", maxsplit=1)
            function_args[name] = value

        self.log.cmd_tool_call(0, function_name, function_args)  # Display with last message
        try:
            new_msg = await self.available_functions[function_name](
                self,
                **function_args,
                process_name=process_name
            )
        except Exception as err:
            err_msg = make_error_msg(err)
            self.log.error(err_msg, err)
            raise err

        return {'role': 'user', 'content': f"```result of {function_name}({function_args})\n{new_msg['content']}\n```"}

    async def execute_cmd_ai(self, command: str, process_name: str) -> dict[str, str]:
        """Execute a local command by LLM request"""

        txt = self.exec_subprocess(command)
        msg = {'name': 'exec', 'role': self.function_role(), 'content': f'AI exec {txt}'}
        return await succeed(msg)

    async def ask_user(self, question: str, process_name: str) -> dict[str, str]:
        """The LLM asks the local user for clarification with improved formatting and advanced line editing."""

        console = self.log._console
        # console = Console()

        # Create a styled question
        styled_question = Text(question, style="bold cyan")

        # Create a panel for the question
        question_panel = Panel(
            styled_question,
            title=f"[bold green]{process_name}[/bold green]",
            subtitle="[italic]Enter your response (Ctrl-D to finish)[/italic]",
            border_style="green",
            expand=False
        )

        # Display the question panel
        console.print(question_panel)

        # Set up key bindings
        kb = KeyBindings()

        @kb.add('c-d')
        def _(event):
            event.app.exit(result=event.app.current_buffer.text)

        # Set up prompt_toolkit session with styling
        style = Style.from_dict({
            'prompt': 'ansiyellow bold',
            'input': 'ansiwhite',
        })
        session = PromptSession(
            history=InMemoryHistory(),
            style=style,
            multiline=True,
            prompt_continuation=lambda width, line_number, is_soft_wrap: '▶ ' if not is_soft_wrap else '  ',
            key_bindings=kb
        )

        # Collect user input asynchronously
        try:
            user_response = await session.prompt_async("Your response: ", )
        except EOFError:
            user_response = session.app.current_buffer.text

        # Display the user's response in a panel
        response_panel = Panel(
            Text(user_response, style="yellow"),
            title="[bold blue]Your Response[/bold blue]",
            border_style="blue",
            expand=False
        )
        console.print(response_panel)

        msg = {
            'name': 'exec',
            'role': self.function_role(),
            'content': f'User Answer: {user_response}'
        }
        return msg

    async def load_files(self, filenames: str, process_name: str) -> dict[str, str]:
        """The LLM asks to receive files from the local machine."""

        try:
            file_contents = self.memory.read(filenames, process_name=process_name)

        except Exception as err:
            self.log.error(f"Error while reading file for AI... ", err)
            result = await succeed({'role': self.function_role(),
                                    'name': 'read_file',
                                    'content': f'ERROR file not found: {filenames}'
                                    })
            return result

        return await succeed({'name': 'read_file', 'content': file_contents})
        msg = {
            'name': 'exec',
            'role': self.function_role(),
            'content': f'User Answer: {user_response}'
        }
        return msg

    functions = [
        {
            "name": "readfile",
            "description": "Read the contents of a named file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to read",
                    },
                },
                "required": ["filename"],
            },
        },
        {
            "name": "www_get",
            "description": "Read a webpage url and return the contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The url of the web page to read",
                    },
                },
                "required": ["url"],
            },
        },
        {
            "name": "writefile",
            "description": "Write the contents to a named file on the local file system",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "The contents of the file",
                    },
                },
                "required": ["filename", "content"],
            },
        },
        {
            "name": "exec",
            "description": f"Execute a command on the local {os_descriptor} system",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "command to be executed",
                    },
                },
                "required": ["command"],
            },
        },
        {
            "name": "query_db",
            "description": f"Execute an SQL against psql (PostgreSQL) 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1) database",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL command to be executed",
                    },
                },
                "required": ["sql"],
            },
        },
        {
            "name": "ask_user",
            "description": f"Get Clarification by Asking the user a question",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question to ask the user",
                    },
                },
                "required": ["question"],
            },
        }
    ]
    available_functions = {
        "readfile": readfile,
        "www_get": www_get,
        "writefile": writefile,
        "exec": execute_cmd_ai,
        "query_db": query_db_ai,
        "ask_user": ask_user,
    }

    @abstractmethod
    def make_msg(self, msg: dict[str, str]) -> dict[str, str]:
        pass

    async def generate(self, step, user_messages: list[dict[str, str]], process_name: str):

        self.answer = f'Log of Step: {step.name} : {step.prompt_name}\n'
        pricing = AI_API_Costs[self.model]

        if self.client is None:
            if self.llm_name.lower() == 'openai':
                self.client = AsyncOpenAI()
                self.client.api_key = os.getenv('OPENAI_API_KEY')

            elif self.llm_name.lower() == 'mistral':
                api_key = os.getenv('MISTRAL_API_KEY')
                self.client = AsyncMistral(api_key=api_key)

            elif self.llm_name.lower() == 'anthropic':
                api_key = os.getenv('ANTHROPIC_API_KEY')
                self.client = AsyncAnthropic(api_key=api_key)

            elif self.llm_name.lower() == 'ollama':
                self.client = Ollama(llm_name='ollama')

            elif self.llm_name.lower() == 'groq':
                self.client = AsyncGroq()

            else:
                raise ValueError(f"Unknown LLM: {self.llm_name}")

        box_open = False

        while user_messages:
            if box_open:
                self.log.stop_step(step)
                box_open = False
            self.log.start_step(step)
            box_open = True

            msg = user_messages.pop(0)
            while msg['role'] != 'exec':
                if msg['role'] == 'cmd':
                    answer = await self.execute_cmd_prompt(msg['content'], process_name)
                    self.messages.append(answer)
                    # self.log.umsg(step, answer)
                else:
                    self.messages.append(self.make_msg(msg))
                    self.log.umsg(step, msg)
                msg = user_messages.pop(0)
                continue

            repeat = True
            while repeat:
                step.interaction_no += 1
                repeat = False

                step.update_gui()

                # Join multiple role=user messages
                msgs = []
                for msg in self.messages:
                    # user is never first msg so edge case msg(role) and msgs empty cannot happen
                    if msgs:
                        if msg['role'] == 'user' and msgs[-1]['role'] == 'user':
                            msgs[-1]['content'] = msgs[-1]['content'] + "\n" + msg['content']
                        else:
                            msgs.append(msg)
                    else:
                        msgs.append(msg)
                self.messages = msgs

                repeat = await self.chat(self.messages, step, process_name)

        self.e_stats['sp_cost'] = pricing['input'] * (self.e_stats['prompt_tokens'] )
        self.e_stats['sc_cost'] = pricing['output'] * (self.e_stats['completion_tokens'] )
        self.e_stats['s_total'] = self.e_stats['sp_cost'] + self.e_stats['sc_cost']
        self.log.stop_step(step)

        # Close DB Pool
        if self.db:
            await self.db.disconnect()
            self.db = None

        return self.answer

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], step, process_name: str):
        pass

    def to_json(self) -> dict:
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'mode': self.mode,
            'messages': self.messages,
            'answer': self.answer,
            'files': self.files,
            'e_stats': self.e_stats
        }

    @classmethod
    def from_json(cls, param):
        return cls(**param)


class OpenAI(AI):

    def __init__(self, llm_name: str, model: str = "gpt-3.5-turbo-1106",
                 temperature: float = 0, max_tokens: int = 4000,
                 mode: str = 'complete', response_format=None, debug:bool = False):
        super().__init__(llm_name, model, temperature, max_tokens, mode, response_format)
        self.tools = None
        self.debug = debug
        # additional initialization goes here

    # Add or override methods for the AI_OpenAI class as required

    def function_role(self) -> str:
        return 'function'

    def make_msg(self, msg: dict[str, str]) -> dict[str, str]:
        return msg

    async def chat(self, messages: list[dict[str, str]], step, process_name):

        if not self.tools:
            self.tools = []
            for func in self.functions:
                self.tools.append({'type': 'function', 'function': func})
        repeat = True
        interaction_no = 0
        while repeat:
            interaction_no += 1
            try:
                self.log_ai(f"Call {interaction_no} OpenAI",
                    {
                        "messages": messages,
                        "model": self.model,
                        "temperature": self.temperature,
                        "tools": self.tools,
                        "tool_choice": "auto",
                        "response_format": self.response_format}
                )

                response = await self.client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    temperature=self.temperature,
                    tools=self.tools,
                    tool_choice="auto",
                    response_format=self.response_format)
            except Exception as err:
                err_msg = f"OpenAI return error {err}"
                self.log.error(err_msg, err)
                raise err

            self.log_ai(f"OpenAI {interaction_no} Response", response.json())

            repeat = False

            msg = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            content = response.choices[0].message.content
            role = response.choices[0].message.role
            function_name = None
            function_args = None

            response_message = {'content': content, 'role': role, 'finish_reason': finish_reason}
            if finish_reason != 'tool_calls':
                self.answer = f"{self.answer}\n\n - {content}"
                self.log.ai_msg(step, content, finish_reason)  # Display with last message=
                self.messages.append(response_message)

            else:
                tool_calls = []
                for call in msg.tool_calls:
                    tool_calls.append({'type': 'function', 'id': call.id,
                                       'function': {'name': call.function.name, 'arguments': call.function.arguments}
                                       })
                self.messages.append({'role': msg.role, 'content': None, 'tool_calls': tool_calls})

                for call in msg.tool_calls:
                    function_call = call.function
                    function_name = function_call.name
                    try:
                        function_args = json.loads(function_call.arguments)
                    except Exception as err:
                        err_msg = make_error_msg(err)
                        self.log.error(f"Function call arguments are not valid json, {err_msg}")
                        raise err

                    # response_message['function_call'] = {'name': call.name, 'arguments': call.arguments}
                    self.log.ai_tool_call(0, function_name, function_args)  # Display with last message
                    try:
                        new_msg = await self.available_functions[function_name](
                            self,
                            **function_args,
                            process_name=process_name
                        )
                    except Exception as err:
                        err_msg = make_error_msg(err)
                        self.log.error(err_msg, err)
                        raise err

                    self.messages.append(
                        {"tool_call_id": call.id,
                         "role": "tool",
                         "name": function_name,
                         "content": new_msg['content']}
                    )
                    self.log.ret_msg(0, new_msg)
                    repeat = True

        # Gather Answer
        self.e_stats['prompt_tokens'] = \
            self.e_stats['prompt_tokens'] + response.usage.prompt_tokens
        self.e_stats['completion_tokens'] = \
            self.e_stats['completion_tokens'] + response.usage.completion_tokens

        return repeat


class Mistral(AI):

    def __init__(self, llm_name: str, model: str = "gpt-3.5-turbo-1106",
                 temperature: float = 0, max_tokens: int = 4000,
                 mode: str = 'complete', response_format=None, debug:bool = False):
        super().__init__(llm_name, model, temperature, max_tokens, mode, response_format)
        # additional initialization goes here
        self.mistral_tools = None
        self.debug = debug

    # Add or override methods for the AI_OpenAI class as required

    def function_role(self) -> str:
        return 'tool'

    # def function_result(self, name: str, content: str, tool_id: str):
    #     return {'role': "tool", "name": name, 'content': content, 'tool_call_id': tool_id}

    def make_msg(self, msg: dict[str, str]) -> dict[str, str]:
        return msg

    async def chat(self, messages: list[dict[str, str]], step, process_name):
        if self.mistral_tools is None:
            self.mistral_tools = [{"type": "function", "function": x} for x in self.functions]

        repeat = True
        interaction_no = 0
        while repeat:
            repeat = False
            interaction_no += 1

            # Call Mistral
            try:
                self.log_ai(f"Call {interaction_no} Mistral",
                    {"model": self.model, "messages":messages, "tools":self.mistral_tools, "tool_choice":"auto",}
                )

                response = await self.client.chat.complete_async(
                    model=self.model,
                    messages=messages,
                    tools=self.mistral_tools,
                    tool_choice="auto",
                )
            except Exception as err:
                err_msg = f"Call to Mistral returned error: {err}"
                self.log.error(err_msg, err)
                response = {'role': 'system', 'error': err_msg}
                raise err

            self.log_ai(f"Mistral {interaction_no} Response", response.json())

            response_message = response.choices[0].message
            # self.messages.append(response_message)
            function_name = None
            function_args = None
            text = response_message.content
            finish_reason = response.choices[0].finish_reason

            if finish_reason == 'tool_calls':
                t = json.loads(response_message.json())
                self.messages.append(t)
                for tool_call in response_message.tool_calls:
                    function_call = tool_call.function
                    function_name = function_call.name
                    function_args = json.loads(function_call.arguments)
                    self.log.ai_tool_call(0, function_name, function_args)
                    rtn = self.available_functions[function_name]
                    rtn_msg = await rtn(self, **function_args, process_name=process_name)
                    new_msg = {'role': 'tool', 'name': function_name, 'content': rtn_msg['content'], 'tool_call_id': tool_call.id,}
                    self.messages.append(new_msg)
                    self.log.ret_msg(0, new_msg)
                repeat = True
            else:
                self.log.ai_msg(step, text, finish_reason)
                self.answer = f"{self.answer}\n\n - {text}"
                if text and text.lower().endswith("if you want to proceed?"):
                    repeat = True
                    msg = {'role': 'user', 'content': 'Proceed.'}
                    self.messages.append(msg)
                    self.log.umsg(step, msg)

            # Gather Answer
            self.e_stats['prompt_tokens'] = \
                self.e_stats['prompt_tokens'] + response.usage.prompt_tokens
            self.e_stats['completion_tokens'] = \
                self.e_stats['completion_tokens'] + response.usage.completion_tokens

        return False


class Anthropic(AI):

    def __init__(self, llm_name: str, model: str = "gpt-3.5-turbo-1106",
                 temperature: float = 0, max_tokens: int = 4000,
                 mode: str = 'complete', response_format=None, debug:bool = False):
        super().__init__(llm_name, model, temperature, max_tokens, mode, response_format)
        # additional initialization goes here
        self.anthropic_tools = None
        self.debug = debug

    # Add or override methods for the AI_OpenAI class as required

    def function_role(self) -> str:
        return 'tool_result'

    # def function_result(self, name: str, content: str):
    #     return {"role": "user", "content": [{'type': "tool_result", "tool_use_id": tool_id, "content": content}]}
    #
    def make_msg(self, msg: dict[str, str]) -> dict[str, str]:
        return msg

    async def chat(self, messages: list[dict[str, str]], step, process_name):
        if self.anthropic_tools is None:
            self.anthropic_tools = []
            for func in self.functions:
                new_func = {"name": func["name"],
                            "description": func["description"],
                            "input_schema": func["parameters"],
                            }
                self.anthropic_tools.append(new_func)

        system_msg = ''
        for mno, msg in enumerate(messages):
            if msg['role'] == 'system':
                system_msg = messages.pop(mno)['content']
            elif 'name' in msg and msg['name'] == 'cmd':
                del msg['name']

        repeat = True
        interaction_no = 0
        while repeat:
            interaction_no += 1
            repeat = False

            # Call Anthropic
            try:
                self.log_ai(f"Call {interaction_no} Anthropic",
                    {
                        "model": self.model,
                        "system": system_msg,
                        "messages":messages,
                        "tools":self.anthropic_tools,
                        "tool_choice":{"type": "auto"},
                        "max_tokens":self.max_tokens,}
                            )

                response = await self.client.messages.create(
                    model=self.model,
                    system=system_msg,
                    messages=messages,
                    tools=self.anthropic_tools,
                    tool_choice={"type": "auto"},
                    max_tokens=self.max_tokens,
                )

            except anthropic.APIConnectionError as err:
                err_msg = f"The server could not be reached"
                self.log.error(err_msg, err)
                response = {'role': 'system', 'error': err_msg}
                raise err

            except anthropic.RateLimitError as err:
                err_msg = (f"A 429 status code (RateLimitError) was received; we should back off a bit.\n"
                           f" Call to Anthropic returned error: {err.__cause__}"
                           )
                self.log.error(err_msg, err)
                response = {'role': 'system', 'error': err_msg}
                raise err

            except anthropic.APIStatusError as err:
                err_msg = (f"Received status code {err.status_code} from Anthropic\n"
                           f" Call to Anthropic returned error: {err}\n"
                           )
                self.log.error(err_msg, err)
                response = {'role': 'system', 'error': err_msg}
                self.log.print(f"List of messages:\n\n")
                with open("messages.json", "w") as file:
                    json.dump(messages, file, indent=4)
                raise err

            # Build AI response and add it to messages
            self.log_ai(f"Anthropic {interaction_no} Response", response.json())

            content_blocks = []
            stop_reason = response.stop_reason
            for block in response.content:
                typ = block.type
                if typ == "text":
                    content_blocks.append({"type": "text", "text": block.text})
                    self.log.ai_msg(step, block.text, stop_reason)
                    self.answer += f"\n{block.text}"
                elif typ == "tool_use":
                    content_blocks.append(
                        {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input})
                    self.log.ai_tool_call(block.id, block.name, block.input)
            self.messages.append({"role": "assistant", "content": content_blocks})

            response_blocks = []
            for block in response.content:
                if block.type == 'tool_use':
                    function_name = block.name
                    function_args = block.input
                    rtn = self.available_functions[function_name]
                    result = await rtn(self, **function_args, process_name=process_name)
                    response_blocks.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result['content']}
                    )
                    self.log.ret_msg(block.id, result)
                    repeat = True
            if response.stop_reason != 'end_turn':
                self.messages.append({"role": "user", "content": response_blocks})

            # Gather Answer
            self.e_stats['prompt_tokens'] = \
                self.e_stats['prompt_tokens'] + response.usage.input_tokens
            self.e_stats['completion_tokens'] = \
                self.e_stats['completion_tokens'] + response.usage.output_tokens

        return False


class Ollama(AI):

    def __init__(self, llm_name: str, model: str = "llama3",
                 temperature: float = 0, max_tokens: int = 4000,
                 mode: str = 'complete', response_format=None, debug: bool = False):
        super().__init__(llm_name, model, temperature, max_tokens, mode, response_format)
        # additional initialization goes here
        self.ollama_tools = None
        self.debug = debug

    # Add or override methods for the AI_OpenAI class as required

    def function_role(self) -> str:
        return 'tool_result'

    def make_msg(self, msg: dict[str, str]) -> dict[str, str]:
        return msg

    async def chat(self, messages: list[dict[str, str]], step, process_name):
        if self.ollama_tools is None:
            self.ollama_tools = []
            for func in self.functions:
                new_func = {"name": func["name"],
                            "description": func["description"],
                            "input_schema": func["parameters"],
                            }
                self.ollama_tools.append(new_func)

        system_msg = ''
        if messages[0]['role'] == 'system':
            system_msg = messages.pop(0)['content']

        url_generate = "http://localhost:11434/api/chat"
        headers = {"Content-Type": "application/json"}  # Depending on server you might need to include headers
        data = {
            "model": "llama3",
            "messages": self.messages,
            "stream": False,
            "format": "json"
        }

        repeat = True
        interaction_no = 0
        async with httpx.AsyncClient(timeout=600.0) as client:
            while repeat:
                repeat = False
                interaction_no += 1
                try:
                    self.log_ai(f"Call {interaction_no} Ollama", {'url': url_generate, 'json': data, 'headers': headers})

                    response = await client.post(url_generate, json=data, headers=headers)
                except ReadTimeout as err:
                    self.log.error(f"Read Time Out Error while accessing Ollama.", err)
                    raise err
                except Exception as err:
                    self.log.error(f"Error while accessing Ollama: {err.__cause__}", err)
                    raise err

                self.log_ai(f"Ollama {interaction_no} Response", response)

                if response.status_code != 200:
                    err_msg = f"{response.status}::{text}"
                    err = ValueError(err_msg)
                    self.log.error(err_msg, err)
                    raise err
                status = response.status_code
                text = response.text
                response_message = json.loads(text)
                # stop_reason = response_message['done_reason']
                msg = response_message["message"]
                self.log.ai_msg(step, f"{status}::{text}")
                if msg['content'].startswith('{"call_function": '):
                    function_call = json.loads(msg['content'])
                    self.log.info(f"Ollama Function Call: {function_call}")
                    rtn = self.available_functions[function_call['call_function']]
                    del function_call['call_function']
                    result = await rtn(self, **function_call, process_name=process_name)
                    new_msg = {"role": "user", "content": result['content']}
                    self.messages.append(new_msg)
                    self.log.ret_msg(0, result)
                    repeat = True
                else:
                    self.answer += f"\n{msg['content']}"

        return False


class GroqAI(AI):

    def __init__(self, llm_name: str, model: str = "gpt-3.5-turbo-1106",
                 temperature: float = 0, max_tokens: int = 4000,
                 mode: str = 'complete', response_format=None, debug: bool = False):
        super().__init__(llm_name, model, temperature, max_tokens, mode, response_format)
        # additional initialization goes here
        self.groq_tools = None
        self.debug = debug

    # Add or override methods for the AI_OpenAI class as required

    def function_role(self) -> str:
        return 'tool_result'

    # def function_result(self, name: str, content: str):
    #     return {"role": "user", "content": [{'type': "tool_result", "tool_use_id": tool_id, "content": content}]}
    #
    def make_msg(self, msg: dict[str, str]) -> dict[str, str]:
        return msg

    async def chat(self, messages: list[dict[str, str]], step, process_name):
        if self.groq_tools is None:
            self.groq_tools = []
            for func in self.functions:
                new_func = {"type": "function",
                            "function": {
                                "name": func["name"],
                                "description": func["description"],
                                "parameters": func["parameters"],
                            }}
                self.groq_tools.append(new_func)

        # Groq uses system message as normal message with role=system
        # system_msg = ''
        # if messages[0]['role'] == 'system':
        #     system_msg = messages.pop(0)['content']

        repeat = True
        interaction_no = 0
        while repeat:
            interaction_no += 1
            repeat = False
            # Call Groq
            try:
                self.log_ai(f"GroqAI {interaction_no} Call",
                            {"model": self.model,
                                "messages": self.messages,
                                "tools": self.groq_tools,
                                "tool_choice": "auto",
                                "max_tokens": self.max_tokens,
                                }
                            )

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.groq_tools,
                    tool_choice="auto",
                    max_tokens=self.max_tokens
                )

            except Exception as err:
                err_msg = f"Error during call of GROQ: {err}"
                self.log.error(err_msg, err)
                response = {'role': 'system', 'error': err_msg}
                raise AIException(err_msg)

            self.log_ai(f"GroqAI {interaction_no} Response", response.json())

            # Build AI response and add it to messages
            stop_reason = response.choices[0].finish_reason
            message = response.choices[0].message

            if message.tool_calls:
                tool_calls = [{"id": tool_call.id,
                               "function": {"name": tool_call.function.name,"arguments": tool_call.function.arguments,},
                               "type": tool_call.type,
                                } for tool_call in message.tool_calls]

                self.messages.append({
                    "role": "assistant",
                    "tool_calls": tool_calls,
                })

                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    call_args = json.loads(tool_call.function.arguments)
                    call_id = tool_call.id
                    self.log.ai_tool_call(0, function_name, call_args)
                    rtn = self.available_functions[function_name]
                    result = await rtn(self, **call_args, process_name=process_name)
                    new_msg = {"role": "tool",
                               "tool_call_id": tool_call.id,
                               "name": tool_call.function.name,
                               "content": str(result['content'])
                               }
                    self.messages.append(new_msg)
                    ret_msg = {""}
                    self.log.ret_msg(0, result)
                    repeat = True
            else:
                content = {"type": "text", "text": message.content, "role": "Assistant"}
                self.log.ai_msg(step, message.content, stop_reason)
                self.answer += f"\n{message.content}"
                self.messages.append(message)

            # Gather Answer
            self.e_stats['prompt_tokens'] = \
                self.e_stats['prompt_tokens'] + response.usage.prompt_tokens
            self.e_stats['completion_tokens'] = \
                self.e_stats['completion_tokens'] + response.usage.completion_tokens

        return False


if __name__ == "__main__":
    print(f"Models: {len(AI_API_Costs)}")
    for m in sorted(AI_API_Costs):
        print(f'\t{AI_API_Costs[m]}')
