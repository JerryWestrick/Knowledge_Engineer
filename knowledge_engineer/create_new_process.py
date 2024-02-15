import os

from knowledge_engineer.logger import Logger

New_Process_Prompts: dict[str, str] = {
    # =======================================
    '1- Make Requirements.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-1106", "max_tokens": "50000"
.clear "Code/*", "Planning/*", "Logs/*"
.include Requirements/Actor.kepf
.user
read Requirements/ApplicationDescription.md
Make a Requirements Document for the "Snake" game which includes:
- The info in Application Description (above)
- List the games rules.
- list the user interface/interactions
Write the application description to 'Planning/Requirements.md'
.exec
Read 'Planning/Requirements.md' re-write the file 'Planning/Requirements.md' including anything forgotten.
""",

    # ==========================================
    '2- Make Implementation Plan.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-1106", "max_tokens": "50000"
.include Requirements/Actor.kepf
.user
Read the requirements from file 'Planning/Requirements.md'.
Design an implementation plan, which includes all functions / routines to be implemented
write implementation plan in file 'Planning/Implementation_Plan.md'
.exec
Study the implementation plan.  re-write 'Planning/Implementation_Plan.md' including any
missing or additional routines.
""",

    # ==========================================
    '3- Implement Snake Program.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-1106", "max_tokens": "50000"
.system
You are a Python 3 programmer.
.user
for context please read:
 - Requirements: 'Planning/Requirements.md' and
 - Implementation Plan: 'Planning/Implementation_Plan.md'

code each routine into the file 'Code/Snake.py'
Each function should have a docstring explaining its parameters and function.
.exec

- Find a function that is not fully coded yet.
- Code the function and rewrite the file 'Code/Snake.py'.
- Then Prompt User with "\nContinue?".
Repeat this until the program has been fully coded.
Once all is fully coded, prompt User with "\nDone!"
.exec
""",

    # ==========================================
    '4- Review Implementation.kepf':
        """.llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-1106", "max_tokens": "50000"
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
