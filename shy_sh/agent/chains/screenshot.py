from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from shy_sh.agent.chat_models import get_llm
from rich import print
from base64 import b64encode
from PIL import ImageGrab
from io import BytesIO


def screenshot_chain(task: str):
    print(f"📸 [bold yellow]Taking a screenshot...[/bold yellow]")
    image = ImageGrab.grab().convert("RGB")
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_b64 = b64encode(buffered.getvalue()).decode("utf-8")

    llm = get_llm()
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"Write a concise descrption of the image.\nDescribe what you see but only the parts that are usefull to solve this task: {task}",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            },
        ],
    )
    result = ""
    print(f"🤖: ", end="")
    chain = llm | StrOutputParser()
    for chunk in chain.stream([message]):
        print(chunk, end="", flush=True)
        result += chunk
    print()
    return result
