import argparse
import asyncio
import glob
import json
import shutil
import time
from json import JSONDecodeError
from pathlib import Path

from dotenv import load_dotenv
from rich.markdown import Markdown

from knowledge_engineer.AI_API_Costs import AI_API_Costs
from knowledge_engineer.ai import AI
from knowledge_engineer.create_new_process import create_new_proc
from knowledge_engineer.db import DB
from knowledge_engineer.logger import Logger
from knowledge_engineer.step import Step
from knowledge_engineer.version import get_version
import os

log = Logger(namespace="ke", debug=True)
memory = DB()


async def execute_process(process_name: str):
    log.info(f'Begin Execution of Process "{process_name}"')
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
        log.info(f'Execute {process_name}({step_no}): "{sname}"')
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
    parser = argparse.ArgumentParser(
        description="Knowledge Engineering: AI Prompt Memory Engineering Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # This can help with showing default values
    )

    # Group arguments to enhance readability
    process_management_group = parser.add_argument_group('Process Management')
    process_management_group.add_argument("-c", "--create", metavar="dir", type=str,
                                          help="Create a new process in the specified directory")
    process_management_group.add_argument("-l", "--list", action='store_true',
                                          help="List all steps in the current process")
    execution_control_group = parser.add_argument_group('Execution Control')
    execution_control_group.add_argument("-e", "--execute", action='store_true',
                                         help="Execute all steps in the current process")

    execution_control_group.add_argument("-s", "--step", metavar="name", type=str,
                                         help="Execute the specified step in the process")
    execution_control_group.add_argument("--log", metavar="FILE", type=str, help="Log output to the specified file")

    information_group = parser.add_argument_group('Information')
    information_group.add_argument("-m", "--models", action='store_true', help="List all available OpenAI models")
    information_group.add_argument("-f", "--functions", action='store_true',
                                   help="List all implemented functions available to AI")

    information_group.add_argument("-v", "--version", action='store_true',
                                   help="Print the version of Knowlege_Engineer")

    information_group.add_argument("--macros", action='store_true',
                                   help="Print the values of the Macro Storage")

    # Parse the arguments (This line is necessary for the actual argument parsing, but not for generating the help text)
    # args = parser.parse_args()

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()
    # main(args)
    if args.create:
        create_new_proc(args.create)
        return

    if args.models:
        log.info(f" {'LLM':10} {'Model':25} {'Max Token'} {'$/m-Tok In':>12} {'$/m-Tok Out':>12}")
        log.info(f" {'-' * 10} {'-' * 25} {'-' * 10} {'-' * 12} {'-' * 12} ")

        keys: list[str] = list(AI_API_Costs.keys())
        keys.sort()
        for k in keys:
            v = AI_API_Costs.get(k)
            model = '"' + v['model'] + '"'
            input = f"{v['input']*1000:06.4f}"
            output = f"{v['output']*1000:06.4f}"
            llm = f'"{v["llm"]}"'
            log.info(f" {llm:10} {model :25} {v['context']:>10,} {input:>12} {output:>12}")

    if args.functions:
        log.info(f" {'Function':45} {'Description':50}")
        log.info(f" {'-' * 45} {'-' * 75}")

        for func in AI.functions:
            parm_str = ''
            params = func['parameters']['properties']
            for pname, pdef in params.items():
                ptype = pdef['type']
                pdesc = pdef['description']
                parm_str += ', ' + pname + ': ' + ptype
            func_str = f"{func['name']}({parm_str[2:]})"
            log.info(f" {func_str:45} \"{func['description']}\"")

    if args.version:
        ver: dict[str, str] = get_version()
        version_str: str = f"{ver['Name']}: {ver['Version']} \n"
        log.info(f" {version_str}")

    if args.macros:
        ver: dict[str, str] = get_version()
        version_str: str = ""
        for k, v in ver.items():
            version_str += f"{k}: {v}\n"
        log.info(f" {version_str}")

    if args.models or args.functions or args.version or args.macros:
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
        log.info(f'Found "{step_names}"')
        if len(step_names):
            prompt_name = step_names[0]

    if prompt_name[-5:] != '.kepf':
        prompt_name = prompt_name + '.kepf'

    try:
        messages = memory.read_msgs(prompt_name, process_name=proc_name)
    except Exception as err:
        log.error(f"Error in Prompt self.memory[{prompt_name}] {err}")
        raise

    # Get the LLM Definition off top of list on messages
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
        exit(2)
    # log.info(f"Step: {step}")

    # Check for Clear Directories
    if messages[0]['role'] == 'clear':
        clear_msg = messages.pop(0)
        json_str = '[ ' + clear_msg['content'] + ' ]'
        try:
            dirs = json.loads(json_str)
        except JSONDecodeError as err:
            log.error(f"Error parsing .clear line: {err.msg}\n.clear {json_str[2:-2]}\n{'-' * (err.pos + 5)}^")
            exit(2)

        log.info(f"Clearing {dirs}")
        for d in dirs:
            files = glob.glob(d)
            for f in files:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.isfile(f):
                    os.remove(f)
                else:
                    log.error(f"Unknown file type {f}")

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
