import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .OpenAI_API_Costs import OpenAI_API_Costs
from .db import DB
from .logger import Logger

load_dotenv()


async def succeed(d: dict):
    return d


class AI:
    log = Logger(namespace='AI', debug=True)
    log_a = Logger(namespace="Assistant", debug=True)
    memory = DB()
    client = None

    def __init__(self,
                 model: str = "gpt-3.5-turbo-1106",
                 temperature: float = 0,
                 max_tokens: int = 2000,
                 mode: str = 'complete',
                 messages: [dict[str, str]] = None,
                 answer: str = None,
                 files: dict[str, str] = None,
                 e_stats: dict[str, float] = None
                 ):
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        self.model: str = model
        self.mode: str = mode
        self.messages: [dict[str, str]] = messages
        if messages is None:
            self.messages = []
        self.answer: str = answer
        if answer is None:
            self.messages = []

        self.files: dict[str, str] = files
        if files is None:
            self.files = {}

        self.e_stats: dict[str, float] = e_stats
        if e_stats is None:
            self.e_stats = {
                'prompt_tokens': 0.0,
                'completion_tokens': 0.0,
                'total_tokens': 0.0,
                'sp_cost': 0.0,
                'sc_cost': 0.0,
                's_total': 0.0,
                'elapsed_time': 0.0,
            }
        if self.client is not None:
            try:
                AI.client.models.retrieve(model)
            except Exception as e:
                AI.log.error(f"Error: {e}")
                AI.log.warn(
                    f"Model {model} not available for provided API key. Reverting "
                    "to gpt-3.5-turbo. Sign up for the GPT-4 wait list here: "
                    "https://openai.com/waitlist/gpt-4-api"
                )
                self.model = "gpt-3.5-turbo"

        # GptLogger.log('SYSTEM', f"Using model {self.model} in mode {self.mode}")

    async def read_file(self, name: str, process_name: str):

        try:
            file_msgs = self.memory.read_msgs(name, process_name=process_name)

        except Exception as err:
            self.log.error(f"Error while reading file for AI... {err}")
            result = await succeed({'role': 'function',
                                    'name': 'read_file',
                                    'content': f'ERROR file not found: {name}'
                                    })
            return result

        file_msg = file_msgs[0]
        file_contents = file_msg['content']
        result = await succeed({'role': 'function', 'name': 'read_file', 'content': file_contents})
        return result

    async def write_file(self, name: str, contents: str, process_name: str):
        full_name = name
        try:
            self.memory[full_name] = contents
        except Exception as err:
            self.log.error(f"Error while writing file for AI... {err}")
            raise
        result = await succeed({'role': 'function', 'name': 'write_file', 'content': 'Done.'})
        return result

    async def replace(self, name: str, old_code: str, new_code: str, process_name: str) -> dict:
        full_name = name
        try:
            # Reading the entire file content
            file_contents = self.memory.read(full_name)

            # Replacing old code with new code
            updated_contents = file_contents.replace(old_code, new_code)

            # Writing the updated content back to the file
            self.memory[full_name] = updated_contents

            result = await succeed({'role': 'function',
                                    'name': 'replace_function',
                                    'content': 'Function Successfully replaced'
                                    })
            return result

        except Exception as e:
            result = await succeed({'role': 'function',
                                    'name': 'replace_function',
                                    'content': f"An error occurred: {e}"
                                    })
            return result

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
            "name": "replace",
            "description": "In the file named name,"
                           "search for text 'old_code', "
                           "and replace it with 'new_code'",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to be modified",
                    },
                    "old_code": {
                        "type": "string",
                        "description": "the lines of code of the old function definition",
                    },
                    "new_code": {
                        "type": "string",
                        "description": "the lines of code of the new function definition",
                    },
                },
                "required": ["name", "old_code", "new_code"],
            },
        }
    ]
    available_functions = {
        "read_file": read_file,
        "write_file": write_file,
        "replace": replace,
    }

    async def generate(self, step, user_messages: list[dict[str, str]], process_name: str):

        self.answer = f'Log of Step: {step.name} : {step.prompt_name}\n'
        pricing = OpenAI_API_Costs[self.model]

        if AI.client is None:
            AI.client = AsyncOpenAI()
            AI.client.api_key = os.getenv('OPENAI_API_KEY')

        box_open = False

        while user_messages:
            if box_open:
                self.log.stop_step(step)
                box_open = False
            self.log.start_step(step)
            box_open = True

            msg = user_messages.pop(0)
            while msg['role'] != 'exec':
                self.messages.append(msg)
                self.log.umsg(step, msg)
                msg = user_messages.pop(0)
                continue

            repeat = True
            while repeat:
                step.interaction_no += 1
                repeat = False

                step.update_gui()
                ai_response = await self.chat(self.messages)

                if 'error' in ai_response:
                    self.log.warn(ai_response)  # Display with last message
                    break

                response_message = {'role': ai_response.choices[0].message.role,
                                    'content': ai_response.choices[0].message.content
                                    }
                function_name = None
                function_args = None
                if ai_response.choices[0].finish_reason == 'function_call':
                    # if ai_response.choices[0].message.get("function_call"):
                    function_call = ai_response.choices[0].message.function_call
                    function_name = function_call.name
                    function_args = json.loads(function_call.arguments)
                    response_message['function_call'] = {'name': function_name, 'arguments': function_call.arguments}
                else:
                    self.answer = f"{self.answer}\n\n - {response_message['content']}"

                self.messages.append(response_message)
                self.log.ai_msg(step, response_message)  # Display with last message
                if ai_response.choices[0].finish_reason == 'function_call':
                    new_msg = await self.available_functions[function_name](self, **function_args,
                                                                            process_name=process_name)
                    self.messages.append(new_msg)
                    self.log.ret_msg(step, new_msg)
                    repeat = True
                else:
                    if response_message['content'] and response_message['content'].lower().endswith("continue?"):
                        repeat = True
                        msg = {'role': 'user', 'content': 'Continue.'}
                        self.messages.append(msg)
                        self.log.umsg(step, msg)

                # Gather Answer
                self.e_stats['prompt_tokens'] = \
                    self.e_stats['prompt_tokens'] + ai_response.usage.prompt_tokens
                self.e_stats['completion_tokens'] = \
                    self.e_stats['completion_tokens'] + ai_response.usage.completion_tokens

        self.e_stats['sp_cost'] = pricing['input'] * (self.e_stats['prompt_tokens'] / 1000.0)
        self.e_stats['sc_cost'] = pricing['output'] * (self.e_stats['completion_tokens'] / 1000.0)
        self.e_stats['s_total'] = self.e_stats['sp_cost'] + self.e_stats['sc_cost']
        self.log.stop_step(step)

        return self.answer

    async def chat(self, messages: list[dict[str, str]]):

        # self.log.info(f"Calling {self.model} chat with messages: ")
        # self.log.info(messages)
        try:
            response = await AI.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                functions=self.functions,
                function_call="auto")
            # messages = messages,
            # model = self.model,
            # temperature = self.temperature,
            # tools = self.functions,
            # tools_choice = "auto"
        except Exception as err:
            err_msg = f"Call to ChatGpt returned error: {err}"
            self.log.error(err_msg)
            response = {'role': 'system', 'error': err_msg}
            # raise

        # AI.log.info(f"{self.model} chat Response")
        return response

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


if __name__ == "__main__":
    print(f"Models: {len(OpenAI_API_Costs)}")
    for m in sorted(OpenAI_API_Costs):
        print(f'\t{OpenAI_API_Costs[m]}')
