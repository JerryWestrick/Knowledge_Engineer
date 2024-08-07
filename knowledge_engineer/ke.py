import argparse
import asyncio
import glob
import json
import shutil
import time
from json import JSONDecodeError
from pathlib import Path

import traceback

from ansi2html import Ansi2HTMLConverter
from rich.traceback import install

from dotenv import load_dotenv

from knowledge_engineer.AI_API_Costs import AI_API_Costs
from knowledge_engineer.ai import AI, AIException
from knowledge_engineer.create_new_process import create_new_proc
from knowledge_engineer.db import DB
from knowledge_engineer.logger import Logger
from knowledge_engineer.step import Step
from knowledge_engineer.version import get_version
import os

install()
log = Logger(namespace="ke", debug=True)
memory = DB()


async def execute_process(process_name: str, step_glob: str):
    if step_glob == '':
        step_glob = "*"

    log.info(f'Begin Execution of Process "{process_name} steps {step_glob}"')
    step_no: int = 1
    start_time: float = time.time()
    e_stats = {}
    steps_dir = os.getenv("KE_PROC_DIR_PROMPTS")
    full_step_names = memory.glob_files(f"{steps_dir}/{step_glob}.kepf")
    full_step_names.sort()
    log.info(f'Found "{full_step_names}"')
    for full_file_name in full_step_names:
        dirs = full_file_name.split('/')
        sname = dirs[-1]
        # pname = '/'.join(dirs[:-2])
        # step = Step.from_file(pname, sname)
        if sname[0] == '_':
            log.info(f'Skipping step {sname}')
        else:
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
    # process_management_group.add_argument("-l", "--list", action='store_true',
    #                                       help="List all steps in the current process")
    execution_control_group = parser.add_argument_group('Execution Control')
    # execution_control_group.add_argument("-e", "--exec", metavar="exec", type=str,
    #                                      help="Execute one or more steps in the current process matched by glob")
    execution_control_group.add_argument("-e", "--exec", metavar="exec", type=str, nargs='?', const="*",
                                         help="Execute one or more steps in the current process matched by glob",
                                         default=None)
    execution_control_group.add_argument("-s", "--steps", action='store_true',
                                         help="List all steps in the current process")
    # execution_control_group.add_argument("--log", metavar="FILE", type=str, help="Log output to the specified file")

    information_group = parser.add_argument_group('Information')
    information_group.add_argument("-m", "--models", action='store_true', help="List all available OpenAI models")
    information_group.add_argument("-f", "--functions", action='store_true',
                                   help="List all implemented functions available to AI")

    information_group.add_argument("-v", "--version", action='store_true',
                                   help="Print the version of Knowlege_Engineer")

    information_group.add_argument("--macros", action='store_true',
                                   help="Print the values of the Macro Storage")

    debug_group = parser.add_argument_group('debug')
    debug_group.add_argument("-d", "--debug", action='store_true')

    # Parse the arguments (This line is necessary for the actual argument parsing, but not for generating the help text)
    # args = parser.parse_args()

    # Check for ke_process_config.env file

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()
    # main(args)
    if args.create:
        create_new_proc(args.create)
        return

    if args.models:
        log.info(f" {'LLM':15} {'Model':35} {'Max Token'} {'$/m-Tok In':>12} {'$/m-Tok Out':>12}")
        log.info(f" {'-' * 15} {'-' * 35} {'-' * 10} {'-' * 12} {'-' * 12} ")

        # Sort by LLM name, then model.
        sortable_keys = [f"{AI_API_Costs[model]['llm']}:{model}" for model in AI_API_Costs.keys()]
        sortable_keys.sort()

        for k in sortable_keys:
            llm, model_name = k.split(':', maxsplit=1)
            v = AI_API_Costs.get(model_name)
            model = '"' + v['model'] + '"'
            input = f"{v['input']*1000:06.4f}"
            output = f"{v['output']*1000:06.4f}"
            llm = f'"{v["llm"]}"'
            log.info(f" {llm:15} {model :35} {v['context']:>10,} {input:>12} {output:>12}")

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

    if args.steps:
        list_all_processes()
        return

    default_dir = os.getcwd()
    dotenv_file = f'{default_dir}/ke_process_config.env'
    found = os.path.exists(dotenv_file)
    if not found:
        print(f"[No ke_process_config.env file]\n The Directory {default_dir} is not a KnowledgeEngineer Process Directory")
        exit(2)



    asyncio.run(run_ke(args))


async def execute_step(proc_name: str, step_name: str) -> Step:
    prompt_dir = os.getenv('KE_PROC_DIR_PROMPTS')
    log_dir = os.getenv('KE_PROC_DIR_LOGS')
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

    log.info(f'Executing "{prompt_name}"')

    try:
        messages = memory.read_msgs(prompt_name, process_name=proc_name)
    except Exception as err:
        err_msg = f"Error in Prompt self.memory[{prompt_name}] {err}"
        log.error(err_msg, err)
        raise err

    # Get the LLM Definition off top of list on messages
    llm_parms = messages.pop(0)
    json_str = '{' + llm_parms['content'] + '}'
    try:
        step_parameters = json.loads(json_str)
    except JSONDecodeError as err:
        err_msg = f".llm line syntax error in Prompt {prompt_name}"
        log.error(err_msg, err)
        log.error(f"{json_str}", None)
        log.error(f"{err.msg}", None)
        raise err

    model = step_parameters['model']
    if model not in AI_API_Costs:
        err_msg = f"Unknown Model {model}..."
        err = ValueError()
        err.add_note(err_msg)
        log.error(err_msg)
        raise err

    llm = AI_API_Costs[step_parameters['model']]
    if 'llm_name' not in step_parameters:
        step_parameters['llm_name'] = llm['llm']
    if 'max_tokens' not in step_parameters:
        step_parameters['max_tokens'] = llm['context']

    step_parameters['prompt_name'] = Path(prompt_name).stem
    step_parameters['name'] = prompt_name[:-5]

    try:
        step = Step(**step_parameters)
    except TypeError as err:
        err_msg = f"Error in .llm line, unknown parm"
        log.error(err_msg, err)
        raise err
    # log.info(f"Step: {step}")

    # Check for Clear Directories
    if messages[0]['role'] == 'clear':
        clear_msg = messages.pop(0)
        json_str = '[ ' + clear_msg['content'] + ' ]'
        try:
            dirs = json.loads(json_str)
        except JSONDecodeError as err:
            err_msg = f"Error parsing .clear line: {err.msg}\n.clear {json_str[2:-2]}\n{'-' * (err.pos + 5)}^"
            log.error(err_msg, err)
            raise err

        log.info(f"Clearing {dirs}")
        for d in dirs:
            files = glob.glob(d)
            for f in files:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.isfile(f):
                    os.remove(f)
                else:
                    log.error(f"Unknown file type {f}", None)

    # Start Logging
    name = prompt_name[len(prompt_dir) + 1:-5]
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file_name = f"{log_dir}/{proc_name}-{name}.log"
    log.set_log_file(log_file_name)
    log.info(f"Logging to: {log_file_name}")

    await step.run(proc_name, messages=messages)

    convert_log_to_html(log_file_name, f"{log_file_name[:-4]}.html")
    return step


def convert_log_to_html(input_file, output_file):
    # Read the input file
    log.info(f"converting {input_file} to {output_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create an instance of the converter
    conv = Ansi2HTMLConverter(inline=True)

    # Convert ANSI to HTML
    html_content = conv.convert(content)

    # Create a full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Log Viewer</title>
        <style>
            body {{ font-family: monospace; background-color: #1e1e1e; color: #d4d4d4; }}
            .log-container {{ white-space: pre-wrap; word-wrap: break-word; }}
        </style>
    </head>
    <body>
        <div class="log-container">
            {html_content}
        </div>
    </body>
    </html>
    """

    # Write the HTML content to the output file
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     f.write(full_html)
    memory[output_file] = full_html


async def run_ke(args: argparse.Namespace):
    # Does Directory have configuration file?
    default_dir = os.getcwd()
    dotenv_file = f'{default_dir}/ke_process_config.env'

    proc_name = Path(default_dir).stem
    load_dotenv(dotenv_file)

    try:
        if args.exec:
            await execute_process(proc_name, args.exec)
            return

    except Exception as err:
        if args.debug:
            tb_str = traceback.format_exc()
            from rich import print
            print(tb_str)  # use rich print function to pretty print the traceback


if __name__ == "__main__":
    main()
