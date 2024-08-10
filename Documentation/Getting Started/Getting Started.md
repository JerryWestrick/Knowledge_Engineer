# Knowledge Engineer Getting Started

## Installation ## Linux / Mac
```shell
mkdir ke
cd ke
python3 -m venv .venv
source .venv/bin/activate

pip install knowledge_engineer

```
You will need wget2...

```shell
sudo apt install wget2
```



## Installation Dos / Windows

```
mkdir ke
cd ke
python3 -m venv .venv
.venv\Scripts\activate

pip install knowledge_engineer
```
You will need wget2

Got to https://gitlab.com/gnuwget/wget2/-/releases
Download wget2.exe 

```shell
 mkdir c:\Users\Jerry\AppData\Local\wget2
 move wget2.exe c:\Users\Jerry\AppData\Local\wget2
```

And then add 'c:\Users\Jerry\AppData\Local\wget2' to your PATH environment variable.

(use your username not 'Jerry')

Logout and Log back in


### My first Project

```shell
knowledge-engineer --create snake
````

![NewSnakeProject.png](NewSnakeProject.png)

### Setup Project
```shell
cd snake
edit ke_process_config.env
```
*use your favorite editor: kate, notepad, whatever.*

Enter Your API Keys in the ke_process_config.env file: 
OPENAI_API_KEY='<Your Open API Key>'

There are many other keys available to be entered.  but the demo is setup to work with OpenAI

### Execute Example Project
```shell
knowledge_engineer --exec
```


![Execute.png](Execute.png)

## Conclusion: Bravo!!!!   It Works!!!

But what did we just do?

Lets take a look at what we got...

# The Snake Project
The directory contains a Knowledge-Engineer project
(since it has a ke_process_config.env file)

Here is a directory listing of the files in the project

![SnakeProjectDir.png](SnakeProjectDir.png)

We will look at some of these files...

## snake/ke_process_config.env

This is the configuration file for the Project:
```sh
KE_PROC_DIR_PROMPTS='Steps'
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
```

The simple fact that this file exists defines the directory as a knowledge engineer project

Now lets look into its contents:

first 2 lines define special directories for the project:

 - ```KE_PROC_DIR_PROMPTS='Steps'``` says look for prompts in the "snake/Steps" subdir.
 - ```KE_PROC_DIR_LOGS='Logs'``` says to write logs to the "snake/Logs" subdir.

the next lines with "_API_KEY="  define the secret API keys for the different platforms

and finally the **KE_PROC_DB_URL** parameter will define the database the AI should access 
if asked to do so. 

**End of configuration...**


# knowledge-engineer information
## General Information
The is some information you can view about Knowledge_Engineer itself:

### Version
To see the version of knowledge-engineer installed:
```shell
knowledge_engineer --version
```
![knowledge-engineer_version.png](knowledge-engineer_version.png)

### Macros
The following will give you a list of Macros values that can be used in prompting.

```shell
knowledge_engineer --macros
```
![knowledge-engineer_macros.png](knowledge-engineer_macros.png)
(Macro usage is not encouraged yet.)

### Functions
Using the following command you can get a list of functions available on your machine that the LLM may call.  

```shell
knowledge_engineer --functions
```
![knowledge-engineer_functions.png](knowledge-engineer_functions.png)
(Please execute the command as the screen copy above is outdated)

### LLM Models
And this command lists all available LLM models that you can use.

```shell
knowledge_engineer --models
```
![knowledge-engineer_models.png](knowledge-engineer_models.png)
(Please execute the command as the screen copy above is outdated)








## knowledge-engineer Project Information
You can list the steps in the project:
These are the files in the snake/Steps directory:
```shell
knowledge_engineer --steps
```

![Snake_Steps.png](Snake_Steps.png)

## So lets look at these Steps:
### 1- Make Game Prompt.kepf

![1-MakeGameprompt.kepf.png](1-MakeGameprompt.kepf.png)

The .kepf file is executed line by line as follows:
1. The ".llm" line defines the LLM model to call.  It must be listed in --models list above 
2. The ".clear" line deletes everything the listed directories. 
3. The ".system" sets the current message being built to the System Message (or how the model should behave)
4. The lines between .system and .user lines are the system message. 
5. The ".user" line terminates the system message, and starts a "user" message. 
6. The lines between .user and .exec are the user message. 
7. The ".exec" line Tells knowledge-engineer to start an interaction with the model using the message built.

The are several concepts here:
1. The file (Step) is a conversation with a model, with a shared context. Other steps are different conversations with other context and may even use different models.
2. The ".exec" is used to converse with the model and await its response, repeating the send/receive cycle until the conversation stops.  Once stopped the next line in the Step is executed which could be to build a new message and send it to the LLM


When the step is executed, as seen below, the file Planning/Game Prompt.md is written:

![Exec_Step_1.png](Exec_Step_1.png)

Lets look at the lines:

| line                                                                | meaning                        |
|---------------------------------------------------------------------|--------------------------------|
| ke::Begin Execution "snake steps 1*"                                | command being executed         |
| ke::Found "['Steps/1- Make Game Promot.kepf']"                      | steps to be executed           |
| ke::Execute snake(1): "1 - Make Game Prompt.kepf"                   | step being loaded              |
| ke::Exectuting "1 - Make Game Prompt.kepf"                          | Begin of execution             |
| ke::Clearing ['Code/*', 'Planning/*', 'Logs/*']                     | Old files being deleted        |
| ke::Logging to: Logs/snake-1- Make Game Prompt.log                  | opened the log file.           |
| Step::┌─ Step: snake:"Steps/1- Make Game Prompt"                    | Begining of Step               |
| Step::│ Model: "gpt-4o-mini", Temperature: 0, Max Tokens: 128,000   | LLM with parameters            |
| _ AI::│ ┌───────────────────────────────────                        | Begin first Conversation       |
| _ AI::│ │         system You are a Knowledge Engineer creating...   | the system message             |
| _ AI::│ │           user Write a prompt for Chat GPT that will...   | the user message               |
| _ AI::│ │      writefile (Planning/Game Prompt.md, ...)...          | AI calls writefile             |
| _ AI::│ │        call_id 0                                          | AI id for function call        |
| _ AI::│ │         return writefile(0):: Done.                       | ke notifies execution complete |
| _ AI::│ │       AI (stop) [The prompt has been written to the ...   | AI task is complete            |
| _ AI::│ └───────────────────────────────────                        | End first Conversation         |
| Step::│ Writing log "Logs/1- Make Game Prompt log.md"               | Closing up Logfile             |
| Step::│ Elapsed: 0m 3.69s Token Usage: Total: 582                   | Stats for this Step            |
| .     │ Costs:: Total: $0.00 (Prompt: $0.0001, Completion: $0.0000) | Stats for this Step            |
| .     ╰───────────────────────────────────────                      | End of Step                    |
| ke::converting Logs/snake-1- Make Game Prompt.log to                | Converting log to Html         |
| ke::Elapsed: 0m 3.72s Token Usage: Total: 582.0 (Prom...            | Job Stats                      |
| .   Costs:: Total: $0.00 (Prompt: $0.0001, Completion: $0.0000)     | Job Stats                      |

At step termination the logs are written, and the run statistics are printed.

Lets look at the created file

![GamePrompt.png](GamePrompt.png)

Pretty cool, And Now the second Step:

### 2- Make Snake Game.kepf

![2-MakeSnakeGame.png](2-MakeSnakeGame.png)

Here we have a new statement:
- **".include Planning/Game Prompt.md"** which includes the file generate in the previous step into the prompt in this one.
 
We could have told the LLM to read it using the **readfile** function instead of **including** it, but that would have been an extra round trip.

![Exec_Step_2.png](Exec_Step_2.png)

Here you will note that the file **Code/snake_game.py** was written...

This can be executed with the command: 
```shell
python Code/snake_game.py
```
![NoModule.png](NoModule.png)
Uppps: no module pygame.....

```shell
pip install pygame
```

# And Now it Works
```shell
python Code/snake_game.py
```

Phew that was a lot of documenting!!!!

