# OpenAI_API_Costs = {
#
#     # GPT4 Turbo
#     'gpt-4-1106-preview': {'model': 'gpt-4-1106-preview', 'input': 0.0100, 'output': 0.0300, 'context': 128000},
#     'gpt-4-0125-preview': {'model': 'gpt-4-0125-preview', 'input': 0.0100, 'output': 0.0300, 'context': 128000},
#
#     # GPT4
#     'gpt-4':     {'model': 'gpt-4',     'input': 0.0300, 'output': 0.0600, 'context': 8000},
#     'gpt-4-32k': {'model': 'gpt-4-32k', 'input': 0.0600, 'output': 0.1200, 'context': 32000},
#
#     # GPT3
#     'gpt-3.5-turbo-1106':     {'model': 'gpt-3.5-turbo-1106',     'input': 0.0010, 'output': 0.0020, 'context': 16000},
#     'gpt-3.5-turbo-instruct': {'model': 'gpt-3.5-turbo-instruct', 'input': 0.0015, 'output': 0.0020, 'context': 4000},
# }
AI_API_Costs = {
    "gpt-4-0125-preview":     {"llm": "openai",  "model": "gpt-4-0125-preview",     "input": 0.01,        "output": 0.03,         "context": 128000, },
    "gpt-4-1106-preview":     {"llm": "openai",  "model": "gpt-4-1106-preview",     "input": 0.01,        "output": 0.03,         "context": 128000, },
    "gpt-4":                  {"llm": "openai",  "model": "gpt-4",                  "input": 0.03,        "output": 0.06,         "context": 8000,   },
    "gpt-4-32k":              {"llm": "openai",  "model": "gpt-4-32k",              "input": 0.06,        "output": 0.12,         "context": 32000,  },
    "gpt-3.5-turbo-0125":     {"llm": "openai",  "model": "gpt-3.5-turbo-0125",     "input": 0.0005,      "output": 0.0015,       "context": 16000,  },
    "gpt-3.5-turbo-instruct": {"llm": "openai",  "model": "gpt-3.5-turbo-instruct", "input": 0.0015,      "output": 0.002,        "context": 4000,   },
    "open-mistral-7b":        {"llm": "mistral", "model": "open-mistral-7b",        "input": 0.25 / 1000, "output": 0.25 / 1000,  "context": 128000, },
    "open-mistral-8x7b":      {"llm": "mistral", "model": "open-mistral-8x7b",      "input": 0.70 / 1000, "output": 0.70 / 1000,  "context": 128000, },
    "mistral-small-latest":   {"llm": "mistral", "model": "mistral-small-latest",   "input": 2.00 / 1000, "output": 6.00 / 1000,  "context": 128000, },
    "mistral-medium-latest":  {"llm": "mistral", "model": "mistral-medium-latest",  "input": 2.70 / 1000, "output": 8.10 / 1000,  "context": 128000, },
    "mistral-large-latest":   {"llm": "mistral", "model": "mistral-large-latest",   "input": 8.00 / 1000, "output": 24.0 / 1000,  "context": 128000, }
}
