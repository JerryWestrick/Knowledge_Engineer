import datetime
import os
import shutil
import traceback
from pathlib import Path
import re
import glob

from .line_statement import Compiler
from .logger import Logger
from .version import get_version


# This class represents a simple database that stores its data as files in a directory hierarchy.

class DB:
    """
    The Memory is designed to force uniformity to the access of the directory holding all the files for a process.
    This allows us to add / modify several additions to the normal file access:
    1- The "Backup" system to save older versions of a file when it is overwritten.
    2- The execution of include statements and other statements implemented for the .kepe files.
    3- Macro Expansion added to the .kepe files, allowing for an additional level of redundancy

    Additionally, since the DB class encapsulates file access for a process, it is initialized once per execution,
    This is the reason for the SingleTon Design.  In order to do multiple Tests a class method "reset" is available
    to reset the singleton.

    The Directory being managed here represents all the memory needs of a KnowledgeEngineer "process", and is
    configured via environment variables.  The values for these variables are stored in the "ke_process_config.env"
    file.  The "ke_process_config.env" file should set the following environment variables:
    KE_PROC_DIR_PROMPTS='Prompts'
    KE_PROC_DIR_STEPS='Process'
    KE_PROC_DIR_REQUIREMENTS='Requirements'
    OPENAI_API_KEY=<Your Open API key>

    The first 3 values are the subdirectories where the process stores different value types,
    i.e. a Steps file called "1- Step One" will be looked for in:  ./Process/"1- Step One.kesteps"

    """
    log = Logger(namespace='DB', debug=False)
    # a class variable holding a dictionary of all macro_name -> values
    # this is used to replace macro names in the contents of the files
    # macro syntax is '${macro_name}$ i.e. ${version}$ will be replaced with the version number defined below'
    # macro is set to a shallow copy of the variables of each step before step execution.
    macro: dict[str, str] = get_version()

    _instance = None

    def __new__(cls, *args, **kwargs):
        """The DB Memory is designed as a SingleTon.  This makes testing more difficult, but usage easier.
         """
        if not cls._instance:
            cls._instance = super(DB, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def rest(cls):
        cls._instance = None

    def __init__(self, path = None):
        # path is the base directory where the process data is stored.
        # if path=None then use the current directory is used.
        #
        # The all cases the path=directory must contain a file named "ke_process_config.env".

        if path is None:
            path = os.curdir

        self.path = Path(path).absolute()
        self.path.mkdir(parents=True, exist_ok=True)
        self.compiler = Compiler(self)

    def __contains__(self, key):
        return (self.path / key).is_file()

    def __delitem__(self, key: str):
        # Implement the logic to delete the item with the given key
        full_path = self.path / key
        if full_path.is_file():
            os.remove(full_path)
        else:
            shutil.rmtree(f'{full_path}')
        return

    def read_msgs(self, key: str, process_name: str = ''):
        content = self.read(key, process_name)
        lines = content.splitlines()
        msgs = self.get_messages(key, lines, process_name=process_name)
        return msgs

    def read(self, key: str, process_name: str = ''):

        # if process_name:
        #     full_path = self.path / process_name / key
        # else:
        #     full_path = self.path / key
        full_path = self.path / key
        if not full_path.is_file():
            self.log.error(f"Invalid Memory Item.  \nPath not found: {full_path}")
            raise KeyError(key)
        with full_path.open("r", encoding="utf-8") as f:
            # read the file and return the contents
            self.log.info(f"Reading>>{key}")
            content = f.read()
        return content

    def __getitem__(self, key: str) -> [dict[str, str]]:
        """Return the contents of the file with the given key."""
        lines = self.read(key).splitlines()
        msgs = self.get_messages(key, lines)
        return msgs

    def get_messages(self, name: str, macro_source: [str], process_name: str = '') -> [dict[str, str]]:
        """ Compile the code in source into a list of statements
            Execute the statements to return a list of messages"""
        source = []
        for line in macro_source:
            source.append(self.replace_macros(line))
        code = self.compiler.compile(source)
        try:
            msgs = self.compiler.execute(code, process_name=process_name)
        except Exception as err:
            tb_str = traceback.format_exc()
            self.log.error(f"Error {tb_str}")
            raise

        return msgs

    def glob_files(self, search: str) -> [str]:
        """ Return a list of all files in the database that match the search pattern """
        s = self.path / search
        l = len(str(self.path))
        files = [x[l + 1:] for x in glob.glob(str(s))]
        return files

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def backup_file(self, full_path):
        if os.path.exists(full_path):
            path, filename = os.path.split(full_path)
            name, ext = os.path.splitext(filename)

            counter = 1
            new_file_name = f"{path}/{name}.~{counter:02}~{ext}"

            while os.path.exists(new_file_name):
                counter += 1
                new_file_name = f"{path}/{name}.~{counter:02}~{ext}"

            os.rename(full_path, new_file_name)

    def __setitem__(self, key, val):
        full_path = self.path / key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(val, str):
            self.backup_file(full_path)  # make backup
            full_path.write_text(val, encoding="utf-8")
        # If val is not str assume it was a directory...
        self.log.info(f"Writing<<{key}")

    def replace_macros(self, string: str) -> str:
        # this routine is used to substitute macros within a string
        # find all '${' and '}$' pairs, occurring in the string
        # processes them in reverse order (right to left)

        # if there is no '${' in the string, return the string
        if '${' not in string:
            return string

        # split the string into substrings where '${' is found
        begin = string.split('${')

        # while there are still portions separated by '${' in the string
        while len(begin) > 1:
            # get last portion after '${'
            ending = begin.pop()

            # if there is no '}$' in the last portion, no macro substitution needed
            if ending.find('}$') == -1:
                begin.append(begin.pop() + '${' + ending)
                continue
            else:
                # split the last portion by first '}$'
                (macro_name, rest) = ending.split('}$', 1)

                # replace the macro name with its value, and add to end of string
                t = begin.pop()
                if macro_name in self.macro:
                    t += str(self.macro[macro_name]) + rest
                else:
                    t += '${' + macro_name + '}$'
                begin.append(t)
                continue

        # we now have a string with no '${' as only element in begin
        return begin[0]

    def clear_dynamic_memory(self, directory_path):
        try:
            directory_path = self.path / directory_path
            for item in directory_path.iterdir():
                if item.is_file():
                    item.unlink()  # Delete the file
                elif item.is_dir():
                    self.clear_dynamic_memory(item)  # Recursive call for subdirectories
            # directory_path.rmdir()  # Delete the now-empty directory
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_memory_backup(self, directory_path: str):
        try:
            directory_path = self.path / directory_path
            for item in directory_path.iterdir():
                if item.is_file():
                    if len(item.suffixes) > 1:
                        if re.search(r"\.~\d\d~\.", item.name):
                            # print(f"Deleting file {item}")
                            item.unlink()  # Delete the file
                elif item.is_dir():
                    self.clear_dynamic_memory(item)  # Recursive call for subdirectories
            # directory_path.rmdir()  # Delete the now-empty directory
        except Exception as e:
            print(f"An error occurred: {e}")
