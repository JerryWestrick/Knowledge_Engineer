# KnowledgeEngineer

***Command Line Program allowing for the Engineering of Knowledge for Chat-GPT.***


# Quick Start
### Installation

    pip install knowledge-engineer

### Create New Project
    knowledge_engineer --create=snake

### Setup Project
    cd snake
    edit ke_process_config.env

    OPENAI_API_KEY='<Your Open API Key>'


### execute example Project
    knowledge_engineer --execute


# Documentation
[Getting Started](Documentation/Getting%20Started/Getting%20Started.html)

[.kepf Reference]('Documentation/Getting Started/Getting Started.html')


# P.S.
## The project is managed with JetBrains YouTrack, and GitHub
### YouTrack Configuration
- Place Configuration information here...
### GitHub Configuration
- Place Configuration information here...
### Pycharm Integration
- Place Configuration information here...





# Directory Structure of a Process:
All the memory requirements of a process are stored in a single directory.  This directory is the current directory in which the program is run.  The directory is required to have a configuration file named "ke_process_config.env".

### The "ke_process_config.env" file
contents should be:

    KE_PROC_DIR_PROMPTS='Prompts'
    KE_PROC_DIR_STEPS='Steps'
    KE_PROC_DIR_REQUIREMENTS='Requirements'
    OPENAI_API_KEY=<Your Open API key>

The first 3 values are the subdirectories where the process stores different value types, 

#### For example 
a Step file called "1- Step One" will be looked for in the directory:

    "./Process/1- Step One.kestep"


# Links and AIDs

[Distribute Python with pip install]('Documentation/How to Create Python Packages _ Towards Data Science.pdf')
