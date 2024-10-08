# The name of the step is the key to the dictionary
import os
import time

from .ai import AI, AIException, OpenAI, Mistral, Anthropic, Ollama, GroqAI
from .db import DB
from .logger import Logger


class Step:
    log = Logger(namespace="Step", debug=True)
    memory = DB()

    def __init__(self,
                 name: str,
                 prompt_name: str | None = None,
                 macros: dict[str, str] = None,
                 # AI params
                 llm_name: str = '',
                 model: str = 'gpt-4o-mini',
                 temperature: int = 0,
                 max_tokens: int = 4000,
                 response_format=None,
                 debug:bool = False
                 ):
        self.debug = debug
        self.name: str = name
        self.prompt_name: str | None = prompt_name
        self.macros: dict[str, str] = macros

        if macros is None:
            self.macros = {}


        rf = response_format
        if response_format:
            rf = {"type": f"{response_format}"}

        # This should happen inside of AI(...)
        if llm_name == 'openai':
            self.ai: AI = OpenAI(llm_name=llm_name,
                                 model=model,
                                 max_tokens=max_tokens,
                                 temperature=temperature,
                                 response_format=rf,
                                 debug=self.debug
                                 )
        elif llm_name == 'mistral':
            self.ai: AI = Mistral(llm_name=llm_name,
                                  model=model,
                                  max_tokens=max_tokens,
                                  temperature=temperature,
                                  response_format=rf,
                                 debug=self.debug
                                  )
        elif llm_name == 'anthropic':
            self.ai: AI = Anthropic(llm_name=llm_name,
                                    model=model,
                                    max_tokens=max_tokens,
                                    temperature=temperature,
                                    response_format=rf,
                                 debug=self.debug
                                    )
        elif llm_name == 'ollama':
            self.ai: AI = Ollama(llm_name=llm_name,
                                 model=model,
                                 max_tokens=max_tokens,
                                 temperature=temperature,
                                 response_format=rf,
                                 debug=self.debug
                                 )
        elif llm_name == 'groq':
            self.ai: AI = GroqAI(llm_name=llm_name,
                                 model=model,
                                 max_tokens=max_tokens,
                                 temperature=temperature,
                                 response_format=rf,
                                 debug=self.debug
                                 )
        else:
            raise ValueError(f"Unknown LLM: {llm_name}")

    def update_gui(self):
        # Send Update to the GUI
        # msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        # response = json.dumps(msg, ensure_ascii=False, default=str)
        # self.log.info(f"Update GUI called with {msg}")
        pass

    async def run(self, pname, messages):
        self.pname = pname  # Add name of process to step...
        self.interaction_no = 0  # start count of interactions with AI
        start_time = time.time()
        head_len = 12
        head = ' ' * head_len
        self.memory.macro = self.macros  # Use these values for macro substitution

        # Clear Old History
        # self.log.info("step.run()::1")
        self.ai.answer = ''
        self.ai.messages = []
        self.ai.files = {}
        self.ai.e_stats['elapsed_time'] = 0.0
        self.ai.e_stats['prompt_tokens'] = 0.0
        self.ai.e_stats['completion_tokens'] = 0.0
        self.ai.e_stats['sp_cost'] = 0.0
        self.ai.e_stats['sc_cost'] = 0.0
        self.ai.e_stats['s_total'] = 0.0
        self.ai.e_stats['elapsed_time'] = 0.0

        txt = f'{self.log.top_left}{self.log.horizontal_mid} Step: {self.pname}:"{self.name}"'
        self.log.info(f"{txt}")
        txt = f'{self.log.vertical_mid} Model: "{self.ai.model}", Temperature: {self.ai.temperature}, Max Tokens: {int(self.ai.max_tokens):,} Company: {self.ai.llm_name}'
        if self.ai.response_format:
            txt += f', Response Format: "{self.ai.response_format["type"]}"'
        self.log.info(txt)

        try:
            # self.ai.messages = messages
            self.update_gui()
            ai_response = await self.ai.generate(self, messages, process_name=self.pname)
        except AIException as err:
            err_msg = f'Step: {self.pname}:"{self.name}" ai.generate failed: {err}'
            self.log.error(err_msg, err)
        except Exception as err:
            err_msg = f'Step: {self.pname}:"{self.name}" ai.generate failed: {err}'
            self.log.error(err_msg, err)

            # Write log file
            log_dir: str = os.getenv('KE_PROC_DIR_LOGS')
            full_path: str = f"{log_dir}/{self.prompt_name} log.md"
            self.log.info(f'{self.log.vertical_mid} Writing log "{full_path}"')
            self.memory[full_path] = f"{self.ai.answer}\nError:{err_msg}"

            raise err

        self.update_gui()

        # Write log file if required...
        log_dir: str = os.getenv('KE_PROC_DIR_LOGS')
        full_path: str = f"{log_dir}/{self.prompt_name} log.md"
        self.log.info(f'{self.log.vertical_mid} Writing log "{full_path}"')
        self.memory[full_path] = self.ai.answer

        total_tokens = (int(self.ai.e_stats['prompt_tokens']) + int(self.ai.e_stats['completion_tokens']))
        self.ai.e_stats['total_tokens'] = total_tokens
        if total_tokens > int(self.ai.max_tokens):
            wcolor = "dark_orange3"
        else:
            wcolor = "green"

        self.ai.e_stats['elapsed_time'] = time.time() - start_time
        mins, secs = divmod(self.ai.e_stats['elapsed_time'], 60)

        self.log.info(f"{self.log.vertical_mid} Elapsed: {int(mins)}m {secs:.2f}s Token Usage: "
                      f"Total: [{wcolor}]{total_tokens:,}[/] ("
                      f"Prompt: {int(self.ai.e_stats['prompt_tokens']):,}, "
                      f"Completion: {int(self.ai.e_stats['completion_tokens']):,})"
                      f"\n{self.log.ts()}{head}"
                      f"{self.log.vertical_mid} Costs:: Total: [green]${self.ai.e_stats['s_total']:.2f}[/] "
                      f"(Prompt: ${self.ai.e_stats['sp_cost']:.4f}, "
                      f"Completion: ${self.ai.e_stats['sc_cost']:.4f})"
                      f"\n{self.log.ts()}{head}{self.log.bottom_left}{self.log.horizontal_mid * 80}")
