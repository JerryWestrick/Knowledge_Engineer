# Knowledge Engineer Getting Started

# Preparation
## Linux / Mac
![img.png](Preparation.png)

## Dos / Windows

```
mkdir ke
cd ke
python3 -m venv .venv
.venv\Scripts\activate
```

# Installation
![Installation.png](Installation.png)

# Create New Snake Project
![NewSnakeProject.png](NewSnakeProject.png)

# Setup Project

cd snake
edit ke_process_config.env

Enter Your API Keys in the ke_process_config.env file: 
OPENAI_API_KEY='<Your Open API Key>'

There are many other keys available to be entered.

# Execute Example Project

![Execute.png](Execute.png)

# Conclusion: Bravo!!!!   It Works!!!

But what did I just do?

Lets take a look at what we got...

# The Snake Project
The directory contains a Knowledge-Engineer project
(since it has a ke_process_config.env file)

Here is a directory listing of the files in the project

![SnakeProjectDir.png](SnakeProjectDir.png)

We will look at these one by one...

### snake/ke_process_config.env

This is the configuration file for the Project:
```
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

FIle existence defines the directory as a knowledge engineer project

first 2 lines define special directories for the project:
 - **KE_PROC_DIR_PROMPTS='Steps'** says look for prompts in the "snake/Steps" subdir.
 - **KE_PROC_DIR_LOGS='Logs'** says to write logs to the "snake/Logs" subdir.

the next lines with "_API_KEY="  define the secret API keys for the different platforms

and finally the **KE_PROC_DB_URL** parameter will define the database the AI should access

End of configuration...


## Some info about installed knowledge-engineer
The is some information you can view about Knowledge_Engineer:

### Version
To see the version of knowledge-engineer installed:
![knowledge-engineer_version.png](knowledge-engineer_version.png)

### Macros
The following will give you a list of Macros values that can be used in prompting.
(Macro usage is not encouraged yet.)
![knowledge-engineer_macros.png](knowledge-engineer_macros.png)

### Functions
Using the following command you can get a list of functions available on your machine that the LLM may call.
![knowledge-engineer_functions.png](knowledge-engineer_functions.png)


### LLM Models
And this command lists all available LLM models that you can use.

![knowledge-engineer_models.png](knowledge-engineer_models.png)


## Project Information
You can list the steps in the project:
These are the files in the snake/Steps directory:

![Snake_Steps.png](Snake_Steps.png)

So lets look at these Steps:
### 1- Make Game Prompt.kepf

![1-MakeGameprompt.kepf.png](1-MakeGameprompt.kepf.png)

All in all not very complicated:
- The ".llm" line defines the LLM model to call.  It is one of the values in the models list above
- The ".clear" line tells knowledge-engineer to delete everything the listed directories
- The lines following the ".system" line describe the "System Prompt" or "how the LLM should behave"
- The lines following the ".user" line are the prompt for the LLm Model.
- The ".exec" line Tells knowledge-engineer to start an interaction with the model.

The are several concepts here:
1. The file (Step) is a conversation with a model, with a shared context. Other steps are different conversations with other context and may even use different models.
2. The ".exec" is used to start a conversation with the model and await its response.  Further messages can then be sent to the model within the same context.

When the step is executed, as seen below, the file Planning/Game Prompt.md is written:

![Exec_Step_1.png](Exec_Step_1.png)

And this is what the generated prompt look like (For me, yours will differ)

![GamePrompt.png](GamePrompt.png)

And Now the second Step:

### 2- Make Snake Game.kepf

![2-MakeSnakeGame.png](2-MakeSnakeGame.png)

Here we have a new statement:
- **".include Planning/Game Prompt.md"** which includes the file generate in the previous step as a prompt in this one.
 
I could have told the LLM to **read** the file instead of **including** it, but that would have been an extra round trip.

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


