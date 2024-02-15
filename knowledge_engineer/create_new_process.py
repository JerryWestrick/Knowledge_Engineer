import os

from knowledge_engineer.logger import Logger

New_Process_Prompts: dict[str, str] = {
    # =======================================
    '1- Make Requirements.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000
.clear "Code/*", "Planning/*", "Logs/*"
.include Requirements/Actor.kepf
.user
read Requirements/ApplicationDescription.md
Make a Requirements Document for the "Snake" game.
Write the application description to 'Planning/Requirements.md' using function 'write_file'
.exec
read 'Planning/Requirements.md'.  Fully finish all sections leaving nothing not complete.
re-write entire requirements to 'Planning/Requirements.md' using the function 'write_file'.
""",

    # ==========================================
    '2- Make Implementation Plan.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000
.include Requirements/Actor.kepf
.user
Read the requirements from file 'Planning/Requirements.md'.
Design an implementation plan, which lists all functions / routines to be implemented, along with its description.
write implementation plan in file 'Planning/Implementation_Plan.md'
.exec
Study the implementation plan.
Check for startup and shutdown, step loop and "if __name__ eq 'main'".
write any missing or additional routines or comments to file 'Planning/Implementation_Plan.md'
""",

    # ==========================================
    '3- Implement Snake Program.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000
.clear "Code/*"
.system
You are a Python 3 programmer.
Do not tell me what you are about to do or did.
Write fully executable code, not 'dummy', 'pass', or 'here goes'.
.user
for context please read the following files:
 - Requirements: 'Planning/Requirements.md' and
 - Implementation Plan: 'Planning/Implementation_Plan.md'

fully implement the program and write it to the file 'Code/Snake.py'
.exec
Go through the file 'Code/Snake.py',
program all functions that is not fully coded, re-write the full 'Code/Snake.py'.
.exec
Go through file 'Code/Snake.py', look for any functions called that are not implemented,
   implement all the missing functions and write entire file 'Code/Snake.py'
.exec
""",

    # ==========================================
    '4- Review Implementation.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000
.system
You are a Python 3 programmer.
.user
Read 'Code/Snake.py' and study the program.
- Is the 'startup', 'execution', and 'shutdown' properly implemented.
- Are all called functions defined?
- Will the program run as coded?
Implement any changes by re-writing the 'Code/Snake.py' file
.exec
""",
}

New_Process_Requirements: dict[str, str] = {
    # =======================================
    'Actor.kepf':
        """.system
You are an IT Engineer, programming a Python 3 Application
Do not explain yourself.
Do not apologize.
Complete the tasks given in a way that is optimized for Chat GPT's easy comprehension while not leaving anything out.
Check all code for correctness.
None python answers will be in MarkDown.
""",

    # =======================================
    'ApplicationDescription.md':
        """You are writing a python version of the snake game using pygame.

# Game constants
    SNAKE_CHARACTERS = ["🔴", "🔵", "🟠", "🟡", "🟢", "🟣", "🟤"]
    FOOD_CHAR = "🍎"
    FOOD_COUNT = 5
    DIRECTION = {"Stop": (0, 0), "Up": (0,-1), "Down": (0,1), "Left": (-1,0), "Right": (1,0) }


# The Game

It is the standard "snake" game.

#### Architecture: 
python 3, with pygame

#### The game_board 
Terminal width x terminal height 2d character representation of the playing ground.
is kept up to date with the values of Snake and Foods; 
Therefor you can check for collisions by checking the value of the character in the game_board at position (x, y).

#### Step Logic:
The game is implemented as steps 5 per second.
""",
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

    # Create Example Config File
    with open(f"./{proc_name}/ke_process_config.env", "w") as f:
        f.write("""KE_PROC_DIR_PROMPTS='Prompts'
KE_PROC_DIR_REQUIREMENTS='Requirements'
KE_PROC_DIR_LOGS='Logs'
OPENAI_API_KEY='<Your Open API Key>'
"""
                )

    # Create Prompt Directory
    os.makedirs(f"./{proc_name}/Prompts")
    for k, v in New_Process_Prompts.items():
        with open(f"./{proc_name}/Prompts/{k}", "w") as f:
            f.write(v)

    # Create Requirements Directory
    os.makedirs(f"./{proc_name}/Requirements")
    for k, v in New_Process_Requirements.items():
        with open(f"./{proc_name}/Requirements/{k}", "w") as f:
            f.write(v)

    log.info(f"Created ExampleProcess in {proc_name}.")
    log.info(f"cd {proc_name}")
    log.info(f"Edit the ke_process_config.env, and insert your OPENAI_API_KEY.")
