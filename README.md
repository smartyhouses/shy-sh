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

`pip install git+https://github.com/mceck/shy-sh`

Use `shy --configure` to change LLM (default use ollama - llama3.1)

api_key format for aws bedrock: `region_name acces_key secret_key`

**Examples**

```
shy find all python files in this folder

🛠️ find . -type f -name '*.py'
./src/chat_models.py
./src/agent/tools.py
./src/agent/__init__.py
./src/agent/agent.py
./src/settings.py
./src/main.py

🤖: Here are all the Python files found in the current folder and its subfolders.
```

```
shy convert aaa.png to jpeg and resize to 200x200

🛠️ convert aaa.png -resize 200x200 aaa.jpg
Success!
🤖: I converted the file aaa.png to JPEG format and resized it to 200x200 pixels.
```

```
shy -i

✨: Hello, how are you?

🤖: Hello! I'm fine thanks
```
