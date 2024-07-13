import os

from knowledge_engineer.logger import Logger

New_Process_Steps: dict[str, str] = {
    # =======================================
    '1- Make Game Prompt.kepf':
        """.llm "model": "gpt-3.5-turbo-0125"
.clear "Code/*", "Planning/*", "Logs/*"
.system
You are a Knowledge Engineer creating a Chat GPT prompt.
The prompt will instruct Chat GPT to create a Python 3 Application
Do not explain yourself.
Do not apologize.
Complete the tasks given in a way that is optimized for Chat GPTs easy comprehension while not leaving anything out.
Your answers will be in MarkDown
.user
Write a prompt for Chat GPT that will make it create a minimal snake game using pygame.
write it to the file Planning/Game Prompt.md
.exec
""",

    # ==========================================
    '2- Make Snake Game.kepf':
        """.llm "model": "gpt-3.5-turbo-0125"
.system
You are an IT Engineer, programming a Python 3 Application
Do not explain yourself.
Do not apologize.
Check all code for completeness, correctness, and make sure it is executable.
write all python code via the 'write_file' function to the 'Code/' directory.

.user
.include Planning/Game Prompt.md
.exec
""",

}

Base_Dir: dict[str, str] = {
    # =======================================
    'ke_process_config.env':
        """KE_PROC_DIR_PROMPTS='Steps'
KE_PROC_DIR_LOGS='Logs'
OPENAI_API_KEY='API Key'
MISTRAL_API_KEY='API Key'
CODESTRAL_API_KEY='API Key'
ANTHROPIC_API_KEY='API Key'
GROQ_API_KEY='API Key'
# KE_PROC_DB_URL = one of the following database definitions:
# PostgreSQL: "postgresql://user:password@localhost/dbname"
# MySQL: "mysql://user:password@localhost/dbname"
# SQLite: "sqlite:///path/to/dbfile"
""",

}

Requirements_Dir: dict[str, str] = {}


def create_new_proc(proc_name: str) -> None:
    log = Logger(namespace="create_new_proc", debug=True)
    log.info(f"Create new process {proc_name}")

    # Check that that directory f"./{proc_name}" does not exist:
    if os.path.exists(f"./{proc_name}"):
        log.error(f"Proc {proc_name} already exists", None)
        return

    # Create ExampleProcess in f"./{proc_name}"
    os.makedirs(f"./{proc_name}")

    # fill Base Directory
    for k, v in Base_Dir.items():
        with open(f"./{proc_name}/{k}", "w") as f:
            f.write(v)

    # Create Steps Directory
    os.makedirs(f"./{proc_name}/Steps")
    for k, v in New_Process_Steps.items():
        with open(f"./{proc_name}/Steps/{k}", "w") as f:
            f.write(v)

    # Create Prompt Directory
    # os.makedirs(f"./{proc_name}/Requirements")
    # for k, v in Requirements_Dir.items():
    #     with open(f"./{proc_name}/Requirements/{k}", "w") as f:
    #         f.write(v)

    log.info(f"Created ExampleProcess in {proc_name}.")
    log.info(f"cd {proc_name}")
    log.info(f"Edit the ke_process_config.env, and insert your OPENAI_API_KEY.")
