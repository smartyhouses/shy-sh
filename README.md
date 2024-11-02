# Shy.sh

Sh shell AI copilot

**Help**

Usage: shy [OPTIONS] [PROMPT]...

Arguments
prompt [PROMPT]

Options

- -i Interactive mode [default false if a prompt is passed else true]
- -a Ask confirmation before executing scripts [default false]
- --configure Configure LLM
- --help Show this message and exit.

**Install**

`pip install shy-sh`

Use `shy --configure` to change LLM (default use ollama - llama3.1)

api_key format for aws bedrock: `region_name acces_key secret_key`

**Examples**

```sh
> shy find all python files in this folder

🛠️ find . -type f -name '*.py'

Do you want to execute this command? [Y/n/c]:

./src/chat_models.py
./src/agent/tools.py
./src/agent/__init__.py
./src/agent/agent.py
./src/settings.py
./src/main.py

🤖: Here are all the Python files found in the current folder and its subfolders.
```

```sh
> shy -x convert aaa.png to jpeg and resize to 200x200

🛠️ convert aaa.png -resize 200x200 aaa.jpg
Success!
🤖: I converted the file aaa.png to JPEG format and resized it to 200x200 pixels.
```

```sh
> shy how many filer in this folder

🛠️ ls | wc -l

Do you want to execute this command? [Y/n/c]: c

🤖: Command copied to the clipboard!
```

```sh
> shy

✨: Hello, how are you?

🤖: Hello! I'm fine thanks

✨: how many filer in this folder

🛠️ ls | wc -l

Do you want to execute this command? [Y/n/c]:

5

✨: exit

🤖: 👋 Bye!
```
