import os

from knowledge_engineer.logger import Logger

New_Process_Prompts: dict[str, str] = {
    # =======================================
    '1- Make Generate Code Prompt.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000
.clear "Code/*", "Planning/*", "Logs/*"
.system
You are a Knowledge Engineer creating a GPT4 Turbo prompt.
The prompt will instruct GPT3.5 to create a Python 3 Application
Do not explain yourself.
Do not apologize.
Complete the tasks given in a way that is optimized for Chat GPTs easy comprehension while not leaving anything out.
Your answers will be in MarkDown
.user
read the description of the program: Requirements/ApplicationDescription.md
create a prompt that will instruct GPT 4 Turbo to:
 - create a complete running program as described.
 - contain initialize, process, and terminate phases
 - list all the rules to be implemented
 - implement all the requirements in the prompts
Write the prompt to 'Planning/Gen_Code_Prompt.md' using function 'write_file'.
.exec
""",

    # ==========================================
    '2- Make Snake Game.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-4-0125-preview", "max_tokens": 50000

.system
You are an IT Engineer, programming a Python 3 Application
Do not explain yourself.
Do not apologize.
Check all code for completeness, correctness, and make sure it is executable.
write all python code via the 'write_file' function to the 'Code/' directory.

.user
.include Planning/Gen_Code_Prompt.md
write a complete executable program to 'Code/snake.py' with the 'write_file' function

.exec
""",

}

Base_Dir: dict[str, str] = {
    # =======================================
    'ke_process_config.env':
        """KE_PROC_DIR_PROMPTS='Prompts'
KE_PROC_DIR_LOGS='Logs'
OPENAI_API_KEY='Your Open AI API Key'
MISTRAL_API_KEY='Your Mistral API Key'
KE_PROC_DB_URL="postgresql+aiopg://user:password@localhost/database"
# PostgreSQL: "postgresql://user:password@localhost/dbname"
# MySQL: "mysql://user:password@localhost/dbname"
# SQLite: "sqlite:///path/to/dbfile"
""",

}

Requirements_Dir: dict[str, str] = {

    # =======================================
    'ApplicationDescription.md':
        """You are writing a python version of the snake game using pygame.

# The Game

Implement the standard "snake" game using arrow keys and 'q' to quit.
All rules and interface are to be as generally expected.

#### Architecture: 
python 3, with pygame

#### The game_board 
game_board size is 480x480.
use different colors for snake and foods

#### Game Play:
The game is implemented as steps 10 per second.

"""
}


def create_new_proc(proc_name: str) -> None:
    log = Logger(namespace="create_new_proc", debug=True)
    log.info(f"Create new process {proc_name}")

    # Check that that directory f"./{proc_name}" does not exist:
    if os.path.exists(f"./{proc_name}"):
        log.error(f"Proc {proc_name} already exists")
        return

    # Create ExampleProcess in f"./{proc_name}"
    os.makedirs(f"./{proc_name}")

    # fill Base Directory
    for k, v in Base_Dir.items():
        with open(f"./{proc_name}/{k}", "w") as f:
            f.write(v)

    # Create Prompt Directory
    os.makedirs(f"./{proc_name}/Prompts")
    for k, v in New_Process_Prompts.items():
        with open(f"./{proc_name}/Prompts/{k}", "w") as f:
            f.write(v)

    # Create Prompt Directory
    os.makedirs(f"./{proc_name}/Requirements")
    for k, v in Requirements_Dir.items():
        with open(f"./{proc_name}/Requirements/{k}", "w") as f:
            f.write(v)

    log.info(f"Created ExampleProcess in {proc_name}.")
    log.info(f"cd {proc_name}")
    log.info(f"Edit the ke_process_config.env, and insert your OPENAI_API_KEY.")
