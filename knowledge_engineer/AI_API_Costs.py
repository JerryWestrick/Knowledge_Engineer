# AI API Costs Dictionary

AI_API_Costs = {
    # OpenAI models
    "gpt-4o-mini": {"llm": "openai", "model": "gpt-4o-mini", "input": 0.15 / 1_000_000, "output": 0.6 / 1_000_000,
                    "context": 128000},
    "gpt-4o": {"llm": "openai", "model": "gpt-4o", "input": 5.0 / 1_000_000, "output": 15.0 / 1_000_000,
               "context": 128000},
    "gpt-4o-2024-05-13": {"llm": "openai", "model": "gpt-4o-2024-05-13", "input": 5.0 / 1_000_000, "output": 15.0 / 1_000_000,
               "context": 128000},
    "gpt-4o-mini-2024-07-18": {"llm": "openai", "model": "gpt-4o-mini-2024-07-18", "input": 0.15 / 1_000_000, "output": 0.6 / 1_000_000,
                    "context": 128000},

    # Mistral models
    "open-mistral-nemo-2407": {"llm": "mistral", "model": "open-mistral-nemo-2407", "input": 0.3 / 1_000_000,
                               "output": 0.3 / 1_000_000, "context": 32000},
    "mistral-large-2407": {"llm": "mistral", "model": "mistral-large-2407", "input": 3.0 / 1_000_000,
                           "output": 9.0 / 1_000_000, "context": 32000},
    "codestral-2405": {"llm": "mistral", "model": "codestral-2405", "input": 1.0 / 1_000_000, "output": 3.0 / 1_000_000,
                       "context": 32000},
    "mistral-embed": {"llm": "mistral", "model": "mistral-embed", "input": 0.1 / 1_000_000, "output": 0.1 / 1_000_000,
                      "context": 32000},
    "mistral-7b": {"llm": "mistral", "model": "open-mistral-7b", "input": 0.25 / 1_000_000, "output": 0.25 / 1_000_000,
                      "context": 32000},
    "mixtral-8x7b": {"llm": "mistral", "model": "open-mixtral-8x7b", "input": 0.7 / 1_000_000, "output": 0.7 / 1_000_000,
                      "context": 32000},
    "mixtral-8x22b": {"llm": "mistral", "model": "open-mixtral-8x22b", "input": 2.0 / 1_000_000, "output": 6.0 / 1_000_000,
                      "context": 32000},
    "mistral-small": {"llm": "mistral", "model": "mistral-small", "input": 1.0 / 1_000_000, "output": 3.0 / 1_000_000,
                      "context": 32000},
    "mistral-medium": {"llm": "mistral", "model": "mistral-medium", "input": 2.75 / 1_000_000, "output": 8.1 / 1_000_000,
                      "context": 32000},

    # Anthropic models
    "claude-3-5-sonnet-20240620": {"llm": "anthropic", "model": "claude-3-5-sonnet-20240620", "input": 3.00 / 1_000_000,
                                   "output": 15.00 / 1_000_000, "context": 4096},
    "claude-3-opus-20240229": {"llm": "anthropic", "model": "claude-3-opus-20240229", "input": 15.0 / 1_000_000,
                               "output": 75.0 / 1_000_000, "context": 4096},
    "claude-3-sonnet-20240229": {"llm": "anthropic", "model": "claude-3-sonnet-20240229", "input": 3.0 / 1_000_000,
                                 "output": 15.0 / 1_000_000, "context": 4096},
    "claude-3-haiku-20240307": {"llm": "anthropic", "model": "claude-3-haiku-20240307", "input": 0.25 / 1_000_000,
                                "output": 1.25 / 1_000_000, "context": 4096},
    "claude-2.1": {"llm": "anthropic", "model": "claude-2.1", "input": 8.0 / 1_000_000,
                    "output": 24.0 / 1_000_000, "context": 4096},
    "claude-2.0": {"llm": "anthropic", "model": "claude-2.0", "input": 8.0 / 1_000_000,
                    "output": 24.0 / 1_000_000, "context": 1000},
    "claude-instant-1.2": {"llm": "anthropic", "model": "claude-instant-1.2", "input": 0.80 / 1_000_000,
                    "output": 2.40 / 1_000_000, "context": 1000},

    # Ollama models local
    "llama3": {"llm": "ollama", "model": "llama3", "input": 0.0, "output": 0.0, "context": 4096},
    "phi3": {"llm": "ollama", "model": "phi3", "input": 0.0, "output": 0.0, "context": 4096},

    # Groq model
    "llama3-70b-8192": {"llm": "groq", "model": "llama3-70b-8192", "input": 0.59 / 1000000, "output": 0.79 / 1000000,
                        "context": 8192}
}


