import json
import os
import platform
import subprocess

from dotenv import load_dotenv
from mistralai.async_client import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage
from openai import AsyncOpenAI

from .AI_API_Costs import AI_API_Costs
from .db import DB
from .logger import Logger
from databases import Database

load_dotenv()
load_dotenv('ke_process_config.env')


async def succeed(d: dict):
    return d


os_descriptor = platform.platform()


class AI:
    log = Logger(namespace='AI', debug=True)
    log_a = Logger(namespace="Assistant", debug=True)
    memory = DB()

    def __init__(self, llm_name: str, model: str = "gpt-3.5-turbo-1106",
                 temperature: float = 0, max_tokens: int = 4000,
                 mode: str = 'complete', response_format=None):
        self.tools = None
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

    def function_role(self) -> str:
        if self.llm_name.lower() == 'mistral':
            return 'tool'
        return 'function'

    async def query_db_ai(self, sql: str, process_name: str):

        if self.db is None:
            self.db = Database(os.getenv('KE_PROC_DB_URL'))
            await self.db.connect()

        # self.log.info(f"About to Query Database: {sql}")
        try:
            result = await self.db.fetch_all(query=sql)
        except Exception as err:
            self.log.error(f"{err}")
            result = [{'error': err}]
        result_as_dict = [dict(row) for row in result]
        # self.log.info(f"Query Database Result: {result_as_dict}")
        return await succeed({'role': self.function_role(), 'name': 'query_db', 'content': str(result_as_dict)})

    async def read_file(self, name: str, process_name: str):

        try:
            file_contents = self.memory.read(name, process_name=process_name)

        except Exception as err:
            self.log.error(f"Error while reading file for AI... {err}")
            result = await succeed({'role': self.function_role(),
                                    'name': 'read_file',
                                    'content': f'ERROR file not found: {name}'
                                    })
            return result

        return await succeed({'role': self.function_role(), 'name': 'read_file', 'content': file_contents})

    async def write_file(self, name: str, contents: str, process_name: str):
        full_name = name
        try:
            self.memory[full_name] = contents
        except Exception as err:
            self.log.error(f"Error while writing file for AI... {err}")
            raise

        return await succeed({'role': self.function_role(), 'name': 'write_file', 'content': 'Done.'})

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

    async def execute_cmd_prompt(self, command: str) -> dict[str, str]:
        """Execute a command that was defined in a prompt file (.kepf)"""

        answer = self.exec_subprocess(command)
        msg = {'name': 'cmd', 'role': 'user', 'content': f'.cmd {answer}'}
        return await succeed(msg)

    async def execute_cmd_ai(self, command: str, process_name: str) -> dict[str, str]:
        """Execute a local command by LLM request"""

        txt = self.exec_subprocess(command)
        msg = {'name': 'exec', 'role': self.function_role(), 'content': f'AI exec {txt}'}
        return await succeed(msg)

    functions = [
        {
            "name": "read_file",
            "description": "Read the contents of a named file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to read",
                    },
                },
                "required": ["name"],
            },
        },
        {
            "name": "write_file",
            "description": "Write the contents to a named file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to write",
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents of the file",
                    },
                },
                "required": ["name", "contents"],
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
        }
    ]
    available_functions = {
        "read_file": read_file,
        "write_file": write_file,
        "exec": execute_cmd_ai,
        "query_db": query_db_ai,
    }

    def make_msg(self, msg: dict[str, str]) -> dict[str, str] | ChatMessage:
        if self.llm_name.lower() == 'openai':
            return msg

        if self.llm_name.lower() == 'mistral':
            return ChatMessage(**msg)

        raise ValueError(f"Unknown LLM: {self.llm_name}")

    async def generate(self, step, user_messages: list[dict[str, str]], process_name: str):

        self.answer = f'Log of Step: {step.name} : {step.prompt_name}\n'
        pricing = AI_API_Costs[self.model]

        if self.client is None:
            if self.llm_name.lower() == 'openai':
                self.client = AsyncOpenAI()
                self.client.api_key = os.getenv('OPENAI_API_KEY')

            elif self.llm_name.lower() == 'mistral':
                api_key = os.getenv('MISTRAL_API_KEY')
                self.client = MistralAsyncClient(api_key=api_key)

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
                    answer = await self.execute_cmd_prompt(msg['content'])
                    self.messages.append(self.make_msg(answer))
                    self.log.umsg(step, answer)
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
                repeat = await self.chat(self.messages, step, process_name)

        self.e_stats['sp_cost'] = pricing['input'] * (self.e_stats['prompt_tokens'] / 1000.0)
        self.e_stats['sc_cost'] = pricing['output'] * (self.e_stats['completion_tokens'] / 1000.0)
        self.e_stats['s_total'] = self.e_stats['sp_cost'] + self.e_stats['sc_cost']
        self.log.stop_step(step)

        # Close DB Pool
        if self.db:
            await self.db.disconnect()
            self.db = None

        return self.answer

    async def chat(self, messages: list[dict[str, str]], step, process_name: str):

        if self.llm_name.lower() == 'openai':
            return await self.chat_openai(messages, step, process_name)
        elif self.llm_name.lower() == 'mistral':
            return await self.chat_mistral(messages, step, process_name)
        else:
            raise ValueError(f"Unknown LLM: {self.llm_name}")

        # self.log.info(f"Calling {self.model} chat with messages: ")
        # self.log.info(messages)

    async def chat_openai(self, messages: list[dict[str, str]], step, process_name):
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                functions=self.functions,
                function_call="auto",
                response_format=self.response_format)
        except Exception as err:
            err_msg = f"Call to ChatGpt returned error: {err}"
            self.log.error(err_msg)
            response = {'role': 'system', 'error': err_msg}
            # raise
        repeat = False
        response_message = {'role': response.choices[0].message.role,
                            'content': response.choices[0].message.content
                            }

        function_name = None
        function_args = None
        if response.choices[0].finish_reason == 'function_call':
            function_call = response.choices[0].message.function_call
            function_name = function_call.name
            function_args = json.loads(function_call.arguments)
            response_message['function_call'] = {'name': function_name, 'arguments': function_call.arguments}
        else:
            self.answer = f"{self.answer}\n\n - {response_message['content']}"

        self.messages.append(response_message)
        self.log.ai_msg(step, response_message)  # Display with last message
        if function_name:
            new_msg = await self.available_functions[function_name](self, **function_args,
                                                                    process_name=process_name)
            self.messages.append(self.make_msg(new_msg))
            self.log.ret_msg(step, new_msg)
            repeat = True
        else:
            if response_message['content'] and response_message['content'].lower().endswith("continue?"):
                repeat = True
                msg = {'role': 'user', 'content': 'Continue.'}
                self.messages.append(self.make_msg(msg))
                self.log.umsg(step, msg)

        # Gather Answer
        self.e_stats['prompt_tokens'] = \
            self.e_stats['prompt_tokens'] + response.usage.prompt_tokens
        self.e_stats['completion_tokens'] = \
            self.e_stats['completion_tokens'] + response.usage.completion_tokens

        return repeat

    async def chat_mistral(self, messages: list[dict[str, str]], step, process_name):
        if self.tools is None:
            self.tools = [{"type": "function", "function": x} for x in self.functions]
        repeat = True
        while repeat:
            repeat = False
            # Call Mistral
            try:
                response = await self.client.chat(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    response_format=self.response_format,
                )
            except Exception as err:
                err_msg = f"Call to Mistral returned error: {err} ai.py line: {err.__traceback__.tb_lineno}"
                self.log.error(err_msg)
                response = {'role': 'system', 'error': err_msg}
                raise Exception(err_msg)

            response_message = response.choices[0].message
            self.messages.append(response_message)
            function_name = None
            function_args = None
            if response.choices[0].finish_reason == 'tool_calls':
                for tool_call in response_message.tool_calls:
                    function_call = tool_call.function
                    function_name = function_call.name
                    function_args = json.loads(function_call.arguments)
                    self.log.ai_tool_call(step, tool_call)
                    rtn = self.available_functions[function_name]
                    new_msg = await rtn(self, **function_args, process_name=process_name)
                    self.messages.append(ChatMessage(**new_msg))
                    self.log.ret_msg(step, new_msg)
                repeat = True
            else:
                self.log.ai_msg(step, response_message)
                self.answer = f"{self.answer}\n\n - {response_message.content}"
                if response_message.content and response_message.content.lower().endswith("if you want to proceed?"):
                    repeat = True
                    msg = {'role': 'user', 'content': 'Proceed.'}
                    self.messages.append(ChatMessage(**msg))
                    self.log.umsg(step, msg)

            # Gather Answer
            self.e_stats['prompt_tokens'] = \
                self.e_stats['prompt_tokens'] + response.usage.prompt_tokens
            self.e_stats['completion_tokens'] = \
                self.e_stats['completion_tokens'] + response.usage.completion_tokens

        return False


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

    def append_message(self, msg: dict[str, str], step):
        if self.llm_name == 'openai':
            self.messages.append(msg)
        elif self.llm_name == 'mistral':
            self.messages.append(ChatMessage(role=msg['role'], content=msg['content']))
        self.log.umsg(step, msg)


if __name__ == "__main__":
    print(f"Models: {len(AI_API_Costs)}")
    for m in sorted(AI_API_Costs):
        print(f'\t{AI_API_Costs[m]}')
