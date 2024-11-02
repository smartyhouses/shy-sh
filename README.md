# Shy.sh

Sh shell AI copilot

**Help**

Usage: shy [OPTIONS] [PROMPT]...

Arguments
prompt [PROMPT]

Options

- -i Interactive mode [default false if a prompt is passed else true]
- -x Do not ask confirmation before executing scripts
- -s Take a screenshot to be analyzed with the prompt (requires vision model)
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
> shy rescale movie.avi to 1024x768 and save it in mp4

🛠️ ffmpeg -i movie.avi -vf scale=1024:768 -c:v libx264 output.mp4

Do you want to execute this command? [Y/n/c]: c

🤖: Command copied to the clipboard!
```

```sh
> shy

✨: Hello, how are you?

🤖: Hello! I'm fine thanks

✨: how many file in this folder

🛠️ ls | wc -l

Do you want to execute this command? [Y/n/c]:

5

✨: exit

🤖: 👋 Bye!
```
