import argparse
import asyncio
import time
from pathlib import Path

from dotenv import load_dotenv

from .db import DB
from .ai import AI
from .logger import Logger
from .step import Step
import shutil
import os

log = Logger(namespace="ke", debug=True)
memory = DB()


New_Process_Values: dict[str, str] = {
    'ke_process_config':
        """KE_PROC_DIR_PROMPTS='Prompts'
KE_PROC_DIR_STEPS='Steps'
KE_PROC_DIR_REQUIREMENTS='Requirements'
OPENAI_API_KEY='<Your Open API Key>'
""",

    'example_step':
        """{
  "py/object": "step.Step",
  "proto": null,
  "name": "ExampleStep",
  "prompt_name": "ExamplePrompt.kepf",
  "verify_prompt": "",
  "storage_path": "Planning",
  "text_file": "ExampleStep Log.md",
  "file_process_enabled": false,
  "file_process_name": "",
  "file_glob": "",
  "macros": {},
  "ai": {
    "py/object": "ai.AI",
    "temperature": 0.0,
    "max_tokens": "51000",
    "model": "gpt-3.5-turbo-1106",
    "mode": "chat",
    "messages": [],
    "answer": "",
    "files": {},
    "e_stats": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "total_tokens": 0,
      "sp_cost": 0.0,
      "sc_cost": 0.0,
      "s_total": 0.0,
      "elapsed_time": 0.0
    }
  },
  "pname": "test",
  "interaction_no": 0
}""",

    'example_prompt':
        """.include Requirements/Actor.kepf
.user
Read the description of the file the program in 'Requirements/ApplicationDescription.md'
write a the python program to 'Code/HelloWorld.py'
""",

    'actor':
        """.system
You are an IT Engineer, programming a Python 3 Application
Do not explain yourself.
Do not apologize.
Complete the tasks given in a way that is optimized for Chat GPT's easy comprehension while not leaving anything out.
Check all code for correctness.
Use MarkDown format for all None python answers.
""",
    'application_description':
        """# Hello World Program

This program when executed write the text "Hello World!" to the terminal.
"""
}

def create_new_proc(proc_name: str) -> None:
    log.info(f"Create new process {proc_name}")
    # Check that that directory f"./{proc_name}" does not exist:
    if os.path.exists(f"./{proc_name}"):
        log.error(f"Proc {proc_name} already exists")
        return

    # Create ExampleProcess in f"./{proc_name}"
    os.makedirs(f"./{proc_name}")

    # Create Example Config File
    with open(f"./{proc_name}/ke_process_config.env", "w") as f:
        f.write(New_Process_Values['ke_process_config'])

    # Create Steps
    os.makedirs(f"./{proc_name}/Steps")
    step = Step('ExampleStep.kestep',
                storage_path='Planning',
                text_file="ExampleStep Log.md",
                prompt_name="ExamplePrompt.kepf",
                ai=AI()
                )
    step.to_file(f"./{proc_name}/Steps/example_step.kestep")

    # Create Example Prompt
    os.makedirs(f"./{proc_name}/Prompts")
    with open(f"./{proc_name}/Prompts/ExamplePrompt.kepf", "w") as f:
        f.write(New_Process_Values['example_prompt'])

    # Create Requirements and Actor.kepf
    os.makedirs(f"./{proc_name}/Requirements")
    with open(f"./{proc_name}/Requirements/Actor.kepf", "w") as f:
        f.write(New_Process_Values['actor'])
    with open(f"./{proc_name}/Requirements/ApplicationDescription.md", "w") as f:
        f.write(New_Process_Values['application_description'])

    os.chdir(f'./{proc_name}')
    print(f"Created ExampleProcess in {proc_name}.")
    print(f"Edit the ke_process_config.env, and insert your OPENAI_API_KEY.")


async def execute_process(process_name: str):
    log.info(f"Begin Execution of Process {process_name}")
    step_no: int = 1
    start_time: float = time.time()
    e_stats = {}
    steps_dir = os.getenv("KE_PROC_DIR_STEPS")
    full_step_names = memory.glob_files(f"{steps_dir}/*.kestep")
    full_step_names.sort()
    for full_file_names in full_step_names:
        dirs = full_file_names.split('/')
        sname = dirs[-1]
        pname = '/'.join(dirs[:-2])
        step = Step.from_file(pname, sname)

        log.info(f"Execute {process_name}({step_no}): {step.name} (a {type(step).__name__}) ")
        await step.run(process_name)
        for k, v in step.ai.e_stats.items():
            e_stats[k] = e_stats.get(k, 0.0) + v

        step_no += 1
    e_stats['elapsed_time'] = time.time() - start_time
    mins, secs = divmod(e_stats['elapsed_time'], 60)
    head_len = 12
    head = ' ' * head_len

    log.info(f"Elapsed: {int(mins)}m {secs:.2f}s Token Usage: "
             f"Total: [green]{e_stats['total_tokens']:,}[/] ("
             f"Prompt: {int(e_stats['prompt_tokens']):,}, "
             f"Completion: {int(e_stats['completion_tokens']):,})"
             f"\n{log.ts()}{head}"
             f"Costs:: Total: [green]${e_stats['s_total']:.2f}[/] "
             f"(Prompt: ${e_stats['sp_cost']:.4f}, "
             f"Completion: ${e_stats['sc_cost']:.4f})")



def list_all_processes():
    this_proc = Path(os.getcwd()).stem
    proc_list = f"List of all Steps in Process {this_proc}:"
    steps_dir = os.getenv('KE_PROC_DIR_STEPS')
    step_names = memory.glob_files(f"{steps_dir}/*.kestep")
    step_names.sort()
    for step_full_name in step_names:
        step_name = Path(step_full_name).stem
        proc_list = f"{proc_list}\n    {step_name}"

    log.info(proc_list)


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Knowledge Engineering: AI Prompt Memory Engineering Tool")
    # Add the arguments
    # parser.add_argument("-proc", metavar="proc_name", type=str, help="execute the given process name")
    parser.add_argument("-step", metavar="step_name", type=str, help="execute the given step in the proc")
    parser.add_argument("-file", metavar="file_name", type=str, help="Log to the specified file")
    parser.add_argument("-create", metavar="create", type=str, help="Create a process with given name")
    parser.add_argument("-list", action='store_true', help="List Steps in Process")
    parser.add_argument("-execute", action='store_true', help="Execute Process")

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()
    # main(args)
    if args.create:
        create_new_proc(args.create)
        return

    asyncio.run(run_ke(args))


async def run_ke(args: argparse.Namespace):
    # Does Directory have configuration file?
    if not os.path.exists(f"./ke_process_config.env"):
        log.error(f"[No ke_process_config.env file]\n"
                  f"The Directory {os.getcwd()} is not a KnowledgeEngineer Process Directory")
        exit(2)

    proc_name = Path(os.getcwd()).stem
    load_dotenv('ke_process_config.env')

    if args.list:
        list_all_processes()
        return

    log_file = None
    if args.file is not None:
        log.log_file(args.file)
        log.info(f"Logging to: {args.file}")

    if args.step:
        step = Step.from_file(pname=proc_name, sname=args.step)
        log.info(f"Step: {step}")
        await step.run(proc_name)
        return

    if args.execute:
        await execute_process(proc_name)
        return


if __name__ == "__main__":
    main()
