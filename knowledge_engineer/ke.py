import argparse
import asyncio
import glob
import json
import time
from json import JSONDecodeError
from pathlib import Path

from dotenv import load_dotenv

from knowledge_engineer.OpenAI_API_Costs import OpenAI_API_Costs
from knowledge_engineer.create_new_process import create_new_proc
from knowledge_engineer.db import DB
from knowledge_engineer.logger import Logger
from knowledge_engineer.step import Step
import os

log = Logger(namespace="ke", debug=True)
memory = DB()


async def execute_process(process_name: str):
    log.info(f"Begin Execution of Process {process_name}")
    step_no: int = 1
    start_time: float = time.time()
    e_stats = {}
    steps_dir = os.getenv("KE_PROC_DIR_PROMPTS")
    full_step_names = memory.glob_files(f"{steps_dir}/*.kepf")
    full_step_names.sort()
    for full_file_names in full_step_names:
        dirs = full_file_names.split('/')
        sname = dirs[-1]
        # pname = '/'.join(dirs[:-2])
        # step = Step.from_file(pname, sname)
        log.info(f"Execute {process_name}({step_no}): {sname}")
        step = await execute_step(process_name, sname)
        # await step.run(process_name)
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
    steps_dir = os.getenv('KE_PROC_DIR_PROMPTS')
    step_names = memory.glob_files(f"{steps_dir}/*.kepf")
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
    parser.add_argument("-log", metavar="log", type=str, help="Log to the specified file")
    parser.add_argument("-create", metavar="create", type=str, help="Create a process with given name")
    parser.add_argument("-list", action='store_true', help="List Steps in Process")
    parser.add_argument("-models", action='store_true', help="List all accepted Models")
    parser.add_argument("-execute", action='store_true', help="Execute Process")

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()
    # main(args)
    if args.create:
        create_new_proc(args.create)
        return

    if args.models:
        log.info(f"List of all Models:")
        log.info(f"    {'Generic':15} {'Model':25} {'Context Size'}")
        log.info(f"    {'-' * 15} {'-'*25} {'-'*15}")

        for k, v in OpenAI_API_Costs.items():
            model = '"' + v['model'] + '"'
            log.info(f"    {v['generic']:15} { model :25} {v['context']:,}")
        return

    asyncio.run(run_ke(args))


async def execute_step(proc_name: str, step_name: str) -> Step:
    prompt_dir = os.getenv('KE_PROC_DIR_PROMPTS')

    if step_name.startswith(prompt_dir):
        prompt_name = step_name
    else:
        prompt_name = f"{prompt_dir}/{step_name}"

    if '*' in prompt_name:
        step_names = glob.glob(prompt_name)
        log.info(f"Found {step_names}")
        prompt_name = step_names[0]

    if prompt_name[-5:] != '.kepf':
        prompt_name = prompt_name + '.kepf'

    try:
        messages = memory.read_msgs(prompt_name, process_name=proc_name)
    except Exception as err:
        log.error(f"Error in Prompt self.memory[{prompt_name}] {err}")
        raise

    # Get the LLM Definition off of list on messages
    json_str = '{' + messages.pop(0)['content'] + '}'
    try:
        step_parameters = json.loads(json_str)
    except JSONDecodeError as err:
        log.error(f".llm line syntax error in Prompt {prompt_name}")
        log.error(f"{json_str}")
        log.error(f"{err.msg}")
        exit(2)

    step_parameters['prompt_name'] = Path(prompt_name).stem
    step_parameters['name'] = prompt_name[:-5]

    try:
        step = Step(**step_parameters)
    except TypeError as err:
        log.error(f"Error in .llm line, unknown parm")
    # log.info(f"Step: {step}")

    # Check for Clear Directories
    if messages[0]['role'] == 'clear':
        clear_msg = messages.pop(0)
        json_str = '[ ' + clear_msg['content'] + ' ]'
        dirs = json.loads(json_str)
        log.info(f"Clearing {dirs}")
        for d in dirs:
            files = glob.glob(d)
            for f in files:
                os.remove(f)

    await step.run(proc_name, messages=messages)
    return step


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

    if args.log is not None:
        log.log_file(args.log)
        log.info(f"Logging to: {args.log}")

    if args.step:
        step: Step = await execute_step(proc_name, args.step)
        return

    if args.execute:
        await execute_process(proc_name)
        return


if __name__ == "__main__":
    main()
