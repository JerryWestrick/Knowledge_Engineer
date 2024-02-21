# Knowledge Engineer

***Command Line Program allowing for the Engineering of Knowledge for LLM's.***



OpenAI GPT Chat is the first to be supported, but the program is designed to be extensible to other LLMs. The program can be extended by modifying the "Knowledge Engineer Prompt File" Domain Specific Language (DSL).  

(That is a fancy way to say:  "by modifying the syntax of the **.kepf** files.")

# Quick Start
### Installation
    pip install knowledge-engineer

### Create New Project
    knowledge_engineer --create=snake

### Setup Project
    cd snake
    edit ke_process_config.env

Enter Your OpenAI API Key in the following line of the ke_process_config.env file:

    OPENAI_API_KEY='<Your Open API Key>'

### execute example Project
    knowledge_engineer --execute

### Run Your Generated Snake Game
    python Code/snake.py

# Further Documentation
## For Users

- The [Getting Started](Documentation/Getting%20Started/Getting%20Started.pdf) document contains a good place to start.  It is a PDF file that is a good introduction to the example project you just created and ran.  It is also available in HTML format.

- The [KEPF Language Reference](Documentation/KEPF%20Language%20Reference/KEPF%20Language%20Reference.md) document is a good place to look into the options and syntax of the Domain Specific Language (DSL) used to create the prompts for the LLMs.  It is also available in HTML format.


## For Developers
- Aditionaly, the [Release A Version](Documentation/Release%20A%20Version/Release%20A%20Version.md)  explains how to update PiPy (pip install) directory with future versions of the knowledge-engineer package.


## For Philosophers
- The [Why Knowledge Engineer](Documentation/Why%20Knowledge%20Engineer/Philosophy.md) document explains why I feel that LLMs need 'Knowledge Engineer'.

