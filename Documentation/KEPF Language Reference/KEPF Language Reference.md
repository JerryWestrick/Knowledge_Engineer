
# The Knowledge Engineer Prompt File (KEPF) Language Reference

The KEPF language is used to create conversations with LLMs (Large Language Models) in a way that is easy to understand and use.  

The KEPF language is designed to be used by Prompt Engineers.
The KEPF language is designed to be used by non-programmers.  
The KEPF language is designed to be used by domain experts (i.e. people who know the problem domain).

#### When we are discussing "how to build a conversation" (using KEPF), we cannot avoid seeing "the conversation we are building".  

I will avoid discussions about the conversations themselves (Prompt Engineering).  
And try to keep this document a ***HOW TO CREATE A PROMPT*** using the KEPF language.


# The grammar of the KEPF Language
The KEPF language is a Domain Specific Language (DSL) that is used to create the prompts for the LLMs.  
(i.e. A mini language for a specific purpose)
The language is designed to be simple and easy to use.

### General Syntax
The KEPF Language is line based.  i.e. Each line is processed separately.   

Its purpose is to build Prompts for LLMs.
A prompt for a LLM consists of messages.  

KEPF has a concept of a 'current message' that is being built.  The language has command to define the message being built.  
Text is added to the 'current message' until a new message is started or the Iteration with the LLM is started.  
This will become clear later, but knowing what is going to happen will give you an "AHA, I got it moment".

In KEPF there are 2 types of statements:
### Key Word Statements
These are lines that: 
   - have a period ('.') in column one 
   - immediately followed by a keyword
   - followed by one or more whitespace
   - and optionally may have text between the whitespace and the end of line.

```   
KEYWORD STATEMENT:
    +-- period
    |   +-- keyword
    |   |   +-- whitespace
    |   |   |
    |   |   |     +-- rest_of_line
    |   |   |     |
    v   v   v     v
    .include Planning/Gen_Code_Prompt.md 
```
    NOTE I have had several collisions with files that have a "." (dot) in column one of a line.  
         Maybe a different syntax should be chosen.

### Prompt Text

These are lines that do not follow the above syntax.  They contain the text is added to the 'current message'.  

### The following Key Word Statements are implemented:
| Key Word   | Description                                                           |
|------------|-----------------------------------------------------------------------|
| .llm       | Define the LLM to be used                                             |
| .clear     | Clear working directories                                             |
| .system    | Create a system message and make it "current message"                 |
| .user      | Create a user message and make it "current message"                   |
| .assistant | Imitate a LLM response as example of how you want LLM to respond      |
| .include   | Include a file in the "current message"                               |
| .cmd       | Execute a function locally from .kepf file                            |
| .exec      | Start an Iteration with the LLM                                       |




## .llm 
The llm statement is used to identify the LLM to which this Step will converse with. 
#### Example

    .llm "llm_name": "OpenAI", "model": "gpt-3.5-turbo-0125", "max_tokens": 50000

since the values specified are the defaults, the above is equivalent to: 

    .llm "model": "gpt-3.5-turbo-0125"

The statement tells Knowledge Engineer that it should communicate with ***OpenAI ChatGPT*** and that when instantiating the communications protocol, the following parameters should be used:
- **"model"**: "gpt-3.5-turbo-0125", 
- **"max_tokens"**: 50000


## .clear 
The clear statement is used to delete working files from previous runs of the process.  I suggest you only delete generated files. 
#### Example
    .clear "Code/*", "Planning/*", "Logs/*.log"
This statement tells Knowledge Engineer to delete all files in the Code, Planning, directories along with all log files in the Log Directory.


## .system 
The system statement is used to start creating the **system message** i.e. making it "Current Message". 

Further text lines are added to the "system message" until: 
- a user message is started with a **.user** key word statement or 
- the Iteration is started with a **.exec** key word statement.

#### Example

    .system
    You are a working on administrative services.
    evaluate provided documentation, and generate output as requested.

The statements above tell Knowledge Engineer to create a system message and insert the lines into that message.


## .user 
The user statement is used to start creating a **_user message_** and make it the "Current Message.

Further text lines are added to the "user message".  

#### Example

    .user

    with this webpage:
    .cmd www_get(url=https://docs.anthropic.com/en/docs/about-claude/models)
    .cmd www_get(url="https://mistral.ai/technology/#pricing")
    .cmd www_get(url="https://openai.com/api/pricing/")
    
    Here is the old Pricing:
    .cmd readfile(filename=Prices/AI_API_Costs.py)
    
    update the pricing and write it to Prices/AI_API_Costs.py
    .exec

The ***.user*** statement above tells Knowledge Engineer to create a user message and start adding lines to it.

## .assistant 
The assistant statement is used just like the .system and .user statements.  But it creates an **_assistant message_**. 

Using the assistant message "fakes" previous AI answers in the conversations.  This technic is used in Prompt Engineering 
to give the LLM an example response in the way you want it.  

#### Example

    .user
    list the following topics as a definition list:
    One: One is the loneliest number. Two: Two is the second in the list. Three: Three is at the end.
    .assistant
    <definition list>
    <item>One<definition>One is the loneliest number. </definition></item>
    <item>Two<definition>Two is the second in the list. </definition></item>
    <item>Three<definition>Three is at the end.</definition></item>
    </definition list>
    .user 
    Make a definition list of all the topics covered in the essay
    .exec

The ***.assistant*** statement above "pretends" to be a msg the LLm answered previously, 
and thereby shows the LLM the format that you want returned.

## .include 
The include statement is used to copy the contents of a file, inserting it as text lines into the current message. 

#### Example
    .user
    .include Planning/Gen_Code_Prompt.md
    write a complete executable program to 'Code/snake.py' with the 'write_file' function
    
    .exec


The ***.include*** statement above tells Knowledge Engineer to insert the contents of the file 'Planning/Gen_Code_Prompt.md' into the current Message.  The .exec terminates the "Current Message" (a User Message) and starts an Iteration with the LLM.


## .cmd function(parm1=xxx,parm2=yyy)
The cmd statement is used to execute one of the functions on the local system:  
The command is executed in the current directory (where the Knowledge Engineer is running).

List the available functions:

    knowledge-engineer --functions
    ke:: Function                                      Description                                       
    ke:: --------------------------------------------- ---------------------------------------------------------------------------
    ke:: readfile(filename: string)                    "Read the contents of a named file"
    ke:: www_get(url: string)                          "Read a webpage url and return the contents"
    ke:: writefile(filename: string, content: string)  "Write the contents to a named file on the local file system"
    ke:: exec(command: string)                         "Execute a command on the local Linux-6.8.0-39-generic-x86_64-with-glibc2.39 system"
    ke:: query_db(sql: string)                         "Execute an SQL against psql (PostgreSQL) 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1) database"
    ke:: ask_user(question: string)                    "Get Clarification by Asking the user a question"
 

#### Example
    .user

    with this webpage:
    .cmd www_get(url=https://docs.anthropic.com/en/docs/about-claude/models)
    .cmd www_get(url="https://mistral.ai/technology/#pricing")
    .cmd www_get(url="https://openai.com/api/pricing/")
    
    Here is the old Pricing:
    .cmd readfile(filename=Prices/AI_API_Costs.py)
    
    update the pricing and write it to Prices/AI_API_Costs.py
    .exec

The first .cmd statement calls the www_get(...) function which:
1. retrieves https://docs.anthropic.com/en/docs/about-claude/models webpage, 
2. converts it to text and 
3. inserts it in a new user message  

The content of this message is formated as follows:

        ```www_get(url=https://docs.anthropic.com/en/docs/about-claude/models)
        <webpage text contents>
        ```

## .exec 
The exec statement tells Knowledge Engineer to initiate an Iteration with the LLM.  The LLM will be sent the system and user messages.  Knowledge Engineer and LLM will then respond to each other until the Iteration is complete.


#### Example
    .user
    write a complete executable program to 'Code/snake.py' with the 'write_file' function
    
    .exec
    
The statement above tells Knowledge Engineer to close the "Current Message" and start an Iteration with the LLM.


# More complex example of a KEPF file:

    .llm "model": "gpt-4o-mini"
    .system
    You are a working on administrative services.
    evaluate provided documentation, and generate output as requested.
    .user
    
    with this webpage:
    .cmd www_get(url=https://docs.anthropic.com/en/docs/about-claude/models)
    .cmd www_get(url="https://mistral.ai/technology/#pricing")
    .cmd www_get(url="https://openai.com/api/pricing/")
    
    Here is the old Pricing:
    .cmd readfile(filename=Prices/AI_API_Costs.py)
    
    update the pricing and write it to Prices/AI_API_Costs.py
    .exec
## Description
This Prompt File tells Knowledge engineer to: 
1. go get 3 webpages
2. To read the old prices from Prices/AI_API_Costs.py file
3. then update old prices with contents of webpages 
4. and finally write new prices to Prices/AI_API_Costs.py file 


# EBNF like grammar
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

