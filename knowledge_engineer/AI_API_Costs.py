AI_API_Costs = {

    "gpt-4o": {"llm": "openai", "model": "gpt-4o", "input": 0.005, "output": 0.015, "context": 128000, },
    "gpt-4-1106-preview": {"llm": "openai","model": "gpt-4-1106-preview", "input": 0.01, "output": 0.03, "context": 128000, },
    "gpt-4": {"llm": "openai", "model": "gpt-4", "input": 0.03, "output": 0.06, "context": 8000, },
    "gpt-4-32k": {"llm": "openai", "model": "gpt-4-32k", "input": 0.06, "output": 0.12, "context": 32000, },
    "gpt-3.5-turbo-0125": {"llm": "openai", "model": "gpt-3.5-turbo-0125", "input": 0.0005, "output": 0.0015, "context": 16000, },
    "gpt-3.5-turbo-instruct": {"llm": "openai", "model": "gpt-3.5-turbo-instruct", "input": 0.0015, "output": 0.002, "context": 4000, },
    "open-mistral-7b": {"llm": "mistral", "model": "open-mistral-7b", "input": 0.25 / 1000, "output": 0.25 / 1000, "context": 32000, },
    "open-mistral-8x7b": {"llm": "mistral", "model": "open-mistral-8x7b", "input": 0.70 / 1000, "output": 0.70 / 1000, "context": 32000, },
    "mistral-small-latest": {"llm": "mistral", "model": "mistral-small-latest", "input": 2.00 / 1000, "output": 6.00 / 1000, "context": 32000, },
    "mistral-medium-latest": {"llm": "mistral", "model": "mistral-medium-latest", "input": 2.70 / 1000, "output": 8.10 / 1000, "context": 32000, },
    "mistral-large-latest": {"llm": "mistral", "model": "mistral-large-latest", "input": 8.00 / 1000, "output": 24.0 / 1000, "context": 32000, },
    "codestral-latest": {"llm": "mistral", "model": "codestral-latest", "input": 2.00 / 1000, "output": 6.00 / 1000, "context": 32000, },
    "open-mixtral-8x22b": {"llm": "mistral", "model": "open-mixtral-8x22b", "input": 2.00 / 1000, "output": 6.0 / 1000, "context": 64000, },
    # These are defined price per million...  But value in price is calculate as price per thousand
    "claude-3-5-sonnet-20240620": {"llm": "anthropic", "model": "claude-3-5-sonnet-20240620", "input": 0.00300 / 1000, "output": 0.015 / 1000, "context": 4096, },
    "claude-3-sonnet-20240229": {"llm": "anthropic", "model": "claude-3-sonnet-20240229", "input": 0.015 / 1000,  "output": 0.075 / 1000, "context": 4096, },
    "claude-3-opus-20240229": {"llm": "anthropic", "model": "claude-3-sonnet-20240229", "input": 0.03 / 1000,  "output": 15.0 / 1000, "context": 4096, },
    "claude-3-haiku-20240307": {"llm": "anthropic", "model": "claude-3-haiku-20240307", "input": 0.000025 / 1000, "output": 0.000125 / 1000, "context": 4096, },
}
