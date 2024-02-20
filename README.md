# Knowledge Engineer

***Command Line Program allowing for the Engineering of Knowledge for LLM's.***

OpenAI GPT Chat is the first to be supported, but the program is designed to be extensible to other LLMs. The extensible design is implemented through the usage of the Knowledge Engineer Prompt File (**.kepf**) Domain Specific Language (DSL).

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



- The [Getting Started](Documentation/Getting%20Started/Getting%20Started.pdf) document contains a good place to start.  It is a PDF file that is a good introduction to the example project you just created and ran.  It is also available in HTML format.

- The [KEPF Language Reference]('Documentation/KEPF%20Language%20Reference/KEPF%20Language%20Reference.pdf') document is a good place to look into the options and syntax of the Domain Specific Language (DSL) used to create the prompts for the LLMs.  It is also available in HTML format.

- Aditionaly, the [Release A Version]('Documentation/Release%20A%20Version/Release%20A%20Version.pdf')  explains how to update PiPy (pip install) directory with future versions of the knowledge-engineer package.

- The [Why Knowledge Engineer](Documentation/Why%20Knowledge%20Engineer/Why%20Knowledge%20Engineer.pdf) document explains why I feel that LLMs need 'Knowledge Engineer'.

