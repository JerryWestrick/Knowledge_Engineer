# Knowledge Engineer Getting Started

## Installation ## Linux / Mac
```shell
mdkir ke
cd ke
python3 -m venv .venv
source .venv/bin/activate

pip install knowledge_engineer

```


## Installation Dos / Windows

```
mkdir ke
cd ke
python3 -m venv .venv
.venv\Scripts\activate

pip install knowledge_engineer
```


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
knowledge_engineer --execute
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
knowledge_engineer --list
```

![Snake_Steps.png](Snake_Steps.png)

## So lets look at these Steps:
### 1- Make Game Prompt.kepf

![1-MakeGameprompt.kepf.png](1-MakeGameprompt.kepf.png)

The .kepf file is executed line by line as follows:
- The ".llm" line defines the LLM model to call.  It must be listed in --models list above
- The ".clear" line deletes everything the listed directories.
- The ".system" sets the current message being built to the System Message (or how the model should behave)
- the lines between .system and .user lines are the system message.
- The ".user" line terminates the system message, and starts a "user" message.
- The lines between .user and .exec are the user message.
- The ".exec" line Tells knowledge-engineer to start an interaction with the model using the message built.

The are several concepts here:
1. The file (Step) is a conversation with a model, with a shared context. Other steps are different conversations with other context and may even use different models.
2. The ".exec" is used to converse with the model and await its response, repeating the send/receive cycle until the conversation stops.  Once stopped the next line in the Step is executed which could be to build a new message and send it to the LLM


When the step is executed, as seen below, the file Planning/Game Prompt.md is written:

![Exec_Step_1.png](Exec_Step_1.png)

Lets look at the lines:  
- "ke::Found" shows the Steps to be executed.  In this case just one.
- "ke::Clearing list the files being deleted."
- "Step::  Step: snake: " lists the step being executed.
- "Step::| Model: " lists the LLm version that will be used...
- "AI::| |      system" lists the constructed system message
- "AI::| |        user" lists the constructed user message
- "AI::| |   writefile" AI give the command to write to a file. 
- "AI::| |      return" knowledge_engineer tells AI it did it. 
- "AI::| |   AI (stop)" AI says it done. 

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

This can be executed with the command: "python Code/snake_game.py".

But 3 out of 4 times it will not work, as gpt 3.5 turbo is not up to the task.

So lets use something else:
## Modifying a Step
Edit "2- Make Snake Game,kepf"
change "gpt-3.5-turbo-0125" for "gpt-4o"
then run again using the command: ***"knowledge-engineer --step=2*"***

Now Python Code/snake_game.py will run...


