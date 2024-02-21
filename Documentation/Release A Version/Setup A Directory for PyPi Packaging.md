# Directory Setup

```
    os/
    LICENSE
    MANIFEST.in
    pyproject.toml
    README.md
    setup.cfg
    ...
    os/
        __init__.py
        ...
        path/
```


## \_\_init\_\_.py


At its core __init__.py , marks a directory as a Python package. So, we
include the top-level __init__.py file which marks the directory as our
‘package’.

## setup.cfg
```
[metadata]
name = knowledge_engineer
version = 0.1.2
author = Jerry Westrick
author_email = jerry@westrick.com
description = Engineer GPT Knowledge within a process
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/JerryWestrick/KnowledgeEngineer
classifiers =
    Programming Language :: Python :: 3
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent

[options]
packages = find:
python_requires = >=3.7
include_package_data = False

[options.entry_points]
console_scripts =
    knowledge-engineer = knowledge_engineer.ke:main
    
```

