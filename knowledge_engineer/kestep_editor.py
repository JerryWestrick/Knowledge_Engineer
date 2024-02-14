import os
import sys
import glob
import argparse
from time import sleep

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Input, Select
from step import Step
from ai import AI
from OpenAI_API_Costs import OpenAI_API_Costs

This_File_Name: str | None = None

This_Process_Name: str | None = None

Dir_Process: str | None = None
Dir_Prompt: str | None = None
Dir_Requirements: str | None = None

This_Step_Name: str | None = None
This_Step: Step | None = None


class KEStepEditor(App):
    """Knowledge Engineer Step Editor"""
    thisStep: Step | None = None

    CSS_PATH = "kestep_editor.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("esc", "quit", "Quit Editor")
                ]

    def compose(self) -> ComposeResult:
        """Create Child Widgets for App"""
        yield Header()
        yield Footer()

        name_lbl = Label("Name: ", id="name_lbl", classes="label")
        name_text = Input(placeholder="Enter Step Name", value=This_Step.name, id="name_text", classes="text_edit")

        prompt_name_lbl = Label("Prompt: ", id="prompt_name_lbl", classes="label")
        my_prompts = glob.glob(os.path.join(Dir_Prompt, "*.kepf"))
        my_prompts.sort()
        values = [f"Prompts/{os.path.basename(p)}" for p in my_prompts]
        prompt_select = Select.from_values(values=values, id="prompt_select", classes="select_edit",
                                           value=f"{This_Step.prompt_name}", allow_blank=False)

        verify_prompt_lbl = Label("Verify Prompt: ", id="verify_prompt_lbl", classes="label")
        verify_prompt_text = Input(placeholder="Enter Verify Prompt", value=This_Step.verify_prompt,
                                   id="verify_prompt_text", classes="text_edit")

        storage_path_lbl = Label("Storage Path: ", id="storage_path_lbl", classes="label")
        storage_path_text = Input(placeholder="Enter Storage Path", value=This_Step.storage_path,
                                  id="storage_path_text", classes="text_edit")

        text_file_lbl = Label("Text File: ", id="text_file_lbl", classes="label")
        text_file_text = Input(placeholder="Enter Text File", value=This_Step.text_file, id="text_file_text",
                               classes="text_edit")

        model_lbl = Label("Model: ", id="model_lbl", classes="label")
        models = OpenAI_API_Costs.keys()
        model_select = Select.from_values(values=models, id="model_select", classes="select_edit",
                                          value=This_Step.ai.model, allow_blank=False)

        temperature_lbl = Label("Temperature: ", id="temperature_lbl", classes="label")
        temperature_text = Input(placeholder="Enter temperature", value=This_Step.ai.temperature, id="temperature_text",
                                 classes="text_edit")

        max_tokens_lbl = Label("Max Tokens: ", id="max_tokens_lbl", classes="label")
        max_tokens_text = Input(placeholder="Enter Max Tokens", value=This_Step.ai.max_tokens, type="integer",
                                id="max_tokens_text", classes="text_edit")

        mode_lbl = Label("Mode: ", id="mode_lbl", classes="label")
        mode_text = Input(placeholder="Enter Mode", value=This_Step.ai.mode, id="mode_text", classes="text_edit")

        self.edit_items = [name_lbl, name_text,
                           prompt_name_lbl, prompt_select,
                           verify_prompt_lbl, verify_prompt_text,
                           storage_path_lbl, storage_path_text,
                           text_file_lbl, text_file_text,
                           model_lbl, model_select,
                           temperature_lbl, temperature_text,
                           max_tokens_lbl, max_tokens_text,
                           mode_lbl, mode_text,
                           ]

        for item in self.edit_items:
            yield item

        self.classes = "step_editor"

    def action_toggle_dark(self) -> None:
        """An Action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """An Action to application."""
        self.app.exit(0)


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Knowledge Engineering: Step Editing Tool")
    # Add the arguments
    parser.add_argument("-file", metavar="file_name", type=str, help="Step File To Edit")
    parser.add_argument("-list", action='store_true', help="List Process Directory")

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()

    if args.file is None and args.list is False:
        print('No argument Provided')
        parser.print_help()
        exit(1)

    file_name = os.path.abspath(args.file)

    # Get the file extension
    path_no_ext, ext = os.path.splitext(file_name)
    if ext == "":
        file_name = f"{file_name}.kestep"
        ext = ".kestep"
        print(f"No extension given... Using [.kestep]")

    if ext != '.kestep':
        print(f'File does not have .kestep extension [{ext}]')
        parser.print_usage()
        exit(1)

    This_File_Name = file_name

    # Find Process
    dirs = path_no_ext.split('/')
    This_Step_Name = dirs[len(dirs) - 1]
    This_Process_Name = dirs[len(dirs) - 3]

    if os.path.isfile(This_File_Name):
        print(f'From Existing file: {This_File_Name}')
        This_Step = Step.from_file(This_Process_Name, This_Step_Name)
    else:
        print(f'Into New File [{This_File_Name}]')
        This_Step = Step(This_Process_Name, This_Step_Name)

    dir_process_name = '/'
    for dir_name in dirs:
        dir_process_name = os.path.join(dir_process_name, dir_name)
        if dir_name == This_Process_Name:
            Dir_Process = str(dir_process_name)
            break
    proc_config_file = os.path.join(Dir_Process, 'ke_process_config.env')
    if not load_dotenv(proc_config_file):
        print(f"Could not load {proc_config_file}")
        exit(1)
    Dir_Prompt = os.path.join(Dir_Process, os.getenv('KE_PROC_DIR_PROMPTS'))
    Dir_Steps = os.path.join(Dir_Process, os.getenv('KE_PROC_DIR_STEPS'))
    Dir_Requirements = os.path.join(Dir_Process, os.getenv('KE_PROC_DIR_REQUIREMENTS'))

    if args.list:
        # Check if file exists
        print(f'{"Process":>18}: [{This_Process_Name}]')
        print(f'{"Step":>18}: [{This_Step_Name}]')
        print('')

        print(f'{"Process Dir":>18}: {Dir_Process}')
        print(f'{"Prompt Dir":>18}: {Dir_Prompt}')
        print(f'{"Steps Dir":>18}: {Dir_Steps}')
        print(f'{"Requirements Dir":>18}: {Dir_Requirements}')

        print(f"\nPrompts")
        prompts = glob.glob(os.path.join(Dir_Prompt, "*.*"))
        prompts.sort()
        for prompt in prompts:
            print(f'{" " * 10}{os.path.basename(prompt)}')

        print(f"\nSteps")
        steps = glob.glob(os.path.join(Dir_Steps, "*.*"))
        steps.sort()
        for step in steps:
            print(f'{" " * 10}{os.path.basename(step)}')

        print(f"\nRequirements")
        requirements = glob.glob(os.path.join(Dir_Requirements, "*.*"))
        requirements.sort()
        for requirement in requirements:
            print(f'{" " * 10}{os.path.basename(requirement)}')

        exit(0)

    app = KEStepEditor()
    app.run()
