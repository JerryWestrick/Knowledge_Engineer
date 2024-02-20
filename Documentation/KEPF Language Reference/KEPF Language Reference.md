
# The Knowledge Engineer Prompt File (KEPF) Language Reference

The KEPF language is used to create conversations with LLMs (Large Language Models) in a way that is easy to understand and use.  

The KEPF language is designed to be used by non-programmers.  It is designed to be used by the domain experts.  It is designed to be used by the people who know the problem domain.

#### When we are discussing "how to build a conversation" (using KEPF), we cannot avoid seeing "the conversation we are building".  

I will avoid discussions about the conversations themselves (Prompt Engineering).  And try to keep this document a ***HOW TO CREATE A PROMPT*** using the KEPF language.


## The grammar of the KEPF Language
The KEPF language is a Domain Specific Language (DSL) that is used to create the prompts for the LLMs.  The language is designed to be simple and easy to use.

### General Syntax
The KEPF Language is line based.  Each line is a statement.   

Prompts to LLMs consist of messages.  KEPF has a concept of the 'current message' which is being built.  Text is added to the 'current message' until a new message is started or the Iteration with the LLM is started.

There are 2 types of statements:
1. ***Key Word Statements***: These are lines that: 
   - have a period ('.') in column one 
   - immediately followed by a keyword
   - followed one or more whitespace
   - and optionally may have text between the whitespace and the end of line.

   
    +-- period
    |   +-- keyword
    |   |   +-- whitespace
    |   |   |
    |   |   |     +-- rest_of_line
    |   |   |     |
    v   v   v     v
    .include Planning/Gen_Code_Prompt.md 

2. ***Prompt Text***: These are lines that do not follow the above syntax.  
    The text is included in the 'current message'.  

### The following Key Word Statements are implemented:
| Key Word | Description                                           |
|----------|-------------------------------------------------------|
| .llm     | Define the LLM to be used                             |
| .clear   | Clear working directories                             |
| .system  | Create a system message and make it "current message" |
| .user    | Create a user message and make it "current message"   |
| .include | Include a file in the "current message"               |
| .cmd     | Execute a command on the local system                 |
| .exec    | Start an Iteration with the LLM                       |


## .llm 
The llm statement is used to identify the LLM to which this Step will converse with. 
#### Example
    .llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000

The statement tells Knowledge Engineer that it should communicate with ***OpenAI ChatGPT*** and that when instantiating the communications protocol, the following parameters should be used:
- **"model"**: "gpt-3.5-turbo-0125", 
- **"max_tokens"**: 50000


## .clear 
The clear statement is used to delete working files from previous runs of the process.
#### Example
    .clear "Code/*", "Planning/*", "Logs/*.log"
This statement tells Knowledge Engineer to delete all files in the Code, Planning, directories along with all log files in the Log Directory.


## .system 
The system statement is used to create a **system message** to be sent to the LLM and make it "Current Message". 

Further prompt lines are added to the "system message" until: 
- a user message is started with a **.user** key word statement or 
- the Iteration is started with a **.exec** key word statement.

#### Example
    .system
    You are a Knowledge Engineer creating a GPT4 Turbo prompt.
    The prompt will instruct GPT3.5 to create a Python 3 Application
    Do not explain yourself.
    Do not apologize.
    Complete the tasks given in a way that is optimized for Chat GPTs easy comprehension while not leaving anything out.
    Your answers will be in MarkDown
    .user

The statement above tells Knowledge Engineer to create a system message and insert the following lines into that message.


## .user 
The user statement is used to create a **_user message_** to be sent to the LLM and make it the "Current Message.

Further prompt lines are added to the "user message" until:
- the Iteration is started with a **.exec** key word statement.

#### Example

    .user
    read the description of the program: Requirements/ApplicationDescription.md
    create a prompt that will instruct GPT 4 Turbo to:
       - create a complete running program as described.
       - contain initialize, process, and terminate phases
       - list all the rules to be implemented
       - implement all the requirements in the prompts
    Write the prompt to 'Planning/Gen_Code_Prompt.md' using function 'write_file'.
    .exec

The ***.user*** statement above tells Knowledge Engineer to create a user message. Sub Sequent Prompt lines are added to the user message.

## .include 
The include statement is used to copy the contents of a file, inserting it into the current message. 

#### Example
    .user
    .include Planning/Gen_Code_Prompt.md
    write a complete executable program to 'Code/snake.py' with the 'write_file' function
    
    .exec


The ***.include*** statement above tells Knowledge Engineer to insert the contents of the file 'Planning/Gen_Code_Prompt.md' into the current Message.  The .exec terminates the "Current Message" (a User Message) and starts an Iteration with the LLM.


## .cmd 
The cmd statement is used to execute a command on the local system:  
- The command is executed in the current directory (where the Knowledge Engineer is running). 
- The command is executed in a subshell, 
- stdout and stderr are captured and inserted as Prompt Text into the current message. 
- Often the command generates a file which is either: 
  - included via a **.include statement**.
  - or read by the LLM using the **read_file function**.

#### Example
    .cmd curl https://openai.com/pricing | lynx -dump -stdin > Planning/openai_pricing.txt

The .cmd statement tells Knowledge Engineer to:
1. retrieve https://openai.com/pricing webpage, 
2. convert it to text and 
3. store it in the file:Planning/openai_pricing.txt.  

The output of the command is inserted into the current message.

## .exec 
The exec statement tells Knowledge Engineer to initiate an Iteration with the LLM.  The LLM will be sent the system and user messages.  Knowledge Engineer and LLM will then respond to each other until the Iteration is complete.


#### Example
    .user
    write a complete executable program to 'Code/snake.py' with the 'write_file' function
    
    .exec
    
The statement above tells Knowledge Engineer to close the "Current Message" and start an Iteration with the LLM.


# More complex example of a KEPF file:

    .llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000
    .clear "Planning/*"
    .user
    .cmd curl https://openai.com/pricing | lynx -dump -stdin > Planning/openai_pricing.txt
    read the file 'Planning/openai_pricing.txt'
    Describe the different offerings from OpenAI and write it to 'Code/OpenAI_API_Pricing.md'.
    Make document pretty, by using colors and arranging the info in tables.
    .exec
    read the file Code/OpenAI_API_Pricing.md and rewrite the file 'Code/OpenAI_API_Pricing.md' with the updated information.

## Description
First off the .kepf file does not end with a .exec statement but one was implied it is added to the end of the file.

    .llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000
use OpenAI's Chat GPT 3.5 Turbo

    .clear "Planning/*"
delete all files in the Planning directory.

    .user 
Start a user message

    .cmd curl https://openai.com/pricing | lynx -dump -stdin > Planning/openai_pricing.txt

- Download the OpenAI pricing page, 
- convert it to text and 
- store it in the file 'Planning/openai_pricing.txt'


    read the file 'Planning/openai_pricing.txt'
    Describe the different offerings from OpenAI and write it to 'Code/OpenAI_API_Pricing.md'.
    Make document pretty, by using colors and arranging the info in tables.

Add the "Prompt Text" lines to the user message.

    .exec
Start Iteration with the LLM. (Do It!)

    read the file Code/OpenAI_API_Pricing.md and rewrite the file 'Code/OpenAI_API_Pricing.md' with the updated information.

Add the Prompt Text to the current message.  (Since no .user or .system was defined it defaults to a new user message).

    .exec <-- this was added by the system.
The second Iteration with the LLM is started, with the final '.exec' statement that was added at the beginning.





## EBNF like grammar
    ?start: "." statement 
        
    ?statement: role_statement
            | include_statement
            | text_block_statement
            | exec_statement
            | llm_statement
            | clear_statement
            | cmd_statement
            
    role_statement: role_name 
    
    sl_role_statement: role_name rest_of_line
    
    role_name: "system"     -> system
             | "user"        -> user
             | "assistant"   -> assistant
             | "function"    -> function
        
    include_statement: "include" rest_of_line

    text_block_statement: "text_block" rest_of_line

    llm_statement: "llm" rest_of_line

    cmd_statement: "cmd" rest_of_line

    clear_statement: "clear" rest_of_line
    
    exec_statement:  "exec"
    
    rest_of_line: ENDOFLINE
    
    VAR.1: /[\w\d]+/ 
    
    ENDOFLINE: /[^\n]+/
    
    MEMORY_NAME: /[\w\d][\w\d\/]*/
    
    %ignore " "

