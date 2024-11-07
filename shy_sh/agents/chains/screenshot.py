from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain
from shy_sh.settings import settings
from shy_sh.agents.llms import get_llm
from rich import print
from base64 import b64encode
from PIL import ImageGrab
from io import BytesIO


@chain
def screenshot_chain(state):
    task = state["input"]
    image = ImageGrab.grab().convert("RGB")
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_b64 = b64encode(buffered.getvalue()).decode("utf-8")

    llm = get_llm()
    lang_ctx = ""
    if settings.language:
        lang_ctx = f"\nAnswer in {settings.language} language."

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder("history", optional=True),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"Write a detailed description of the image.{lang_ctx}\nDescribe what you see but only the parts that are usefull to solve this task: {task}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                ],
            ),
        ]
    )
    return prompt | llm | StrOutputParser()
