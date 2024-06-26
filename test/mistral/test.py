import asyncio
import json

from databases import Database
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from knowledge_engineer.logger import Logger

log = Logger(namespace="TestMistral", debug=True)

user_msg = [
    {'role': "system", 'content': "You are an DB specialist. Execute code using the provided query_db function when "
                                  "required to answer questions.  Do not explain the code, just execute it.  "},
    {'role': "user", 'content': "Write a file TableName.md with a list of tables defined in the database."},
]


db = Database("postgresql+aiopg://jerry:tapachula@localhost/rs")


def read_file_to_string(file_path):
    global log
    log.info(f"Reading file: {file_path}")
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def write_string_to_file(file_path, text):
    global log
    log.info(f"Writing file: {file_path}")
    with open(file_path, 'w') as file:
        file.write(text)


async def query_db_ai(sql: str):
    global log
    global db

    log.info(f"About to Query Database: {sql}")
    result = await db.fetch_all(query=sql)
    result_as_dict = [dict(row) for row in result]
    # log.info(f"Query Database Result: {result_as_dict}")
    return result_as_dict


def read_file(name: str):
    try:
        file_contents = read_file_to_string('/path/to/your/file')
    except Exception as err:
        log.error(f"Error while reading file for AI... ", err)
        result = {'role': 'tool',
                  'name': 'read_file',
                  'content': f'ERROR file not found: {name}'
                  }
        return result

    return file_contents


def write_file(name: str, contents: str):
    full_name = name
    try:
        write_string_to_file(file_path=name, text=contents)
    except Exception as err:
        log.error(f"Error while writing file for AI...", err)
        raise

    return 'Done.'


tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a named file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to read"
                    }
                },
                "required": ["name"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write the contents to a named file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to write"
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents of the file"
                    }
                },
                "required": ["name", "contents"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_db",
            "description": "Execute an SQL against psql (PostgreSQL) 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1) database and"
                           " get the results as a JSON list of dictionaries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL command to be executed"
                    }
                },
                "required": ["sql"]
            }
        }
    }
]
available_functions = {
    "read_file": read_file,
    "write_file": write_file,
    "query_db": query_db_ai,
}


async def main():
    global db
    global user_msg
    global log
    messages = []

    await db.connect()
    model = "mistral-small-latest"
    api_key = "JcUm79weiHQFoULdGqhDnhsjCzjNwwFv"
    client = MistralClient(api_key=api_key)

    next_message = user_msg.pop(0)
    msg = ChatMessage(role=next_message['role'], content=next_message['content'])
    while True:
        log.info(f'[cyan]{msg.role}>>>[/] {msg.content}')
        messages.append(msg)
        response = client.chat(model=model, messages=messages, tools=tools, tool_choice="auto")
        messages.append(response.choices[0].message)  # Always add the msg to the list
        finish_reason = response.choices[0].finish_reason
        msg = response.choices[0].message

        match finish_reason:
            case 'tool_calls':
                if len(msg.tool_calls) > 1:
                    log.error(f"{finish_reason} more than one tool call {msg.tool_calls}", None)
                    exit(1)
                function_call = response.choices[0].message.tool_calls[0].function
                function_name = function_call.name
                log.info(f"[blue]<<{msg.role}[/] [magenta bold]{finish_reason}[/] {function_name}({function_call.arguments})")
                function_args = json.loads(function_call.arguments)
                result = ''
                match function_name:
                    case 'query_db':
                        result = await query_db_ai(**function_args)

                    case 'read_file':
                        result = read_file(**function_args)

                    case 'write_file':
                        result = write_file(**function_args)
                msg = ChatMessage(role="tool", name=function_name, content=json.dumps(result))

            case 'stop':
                log.info(f"[blue]<<<{msg.role}[/] [magenta bold]{finish_reason}[/] {msg.content}")
                if user_msg:
                    next_message = user_msg.pop(0)
                    msg = ChatMessage(role=next_message['role'], content=next_message['content'])
                else:
                    log.info("[bold darkgreen]No more messages to send to Mistral[/]")
                    break

            case _:
                log.error(f"Invalid finish_reason: <{finish_reason}>", None)
                break

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
