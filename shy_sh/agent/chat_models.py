from shy_sh.settings import settings
from functools import lru_cache


@lru_cache
def get_llm():
    llm = None
    match settings.llm.provider:
        case "openai":
            from langchain.chat_models.openai import ChatOpenAI

            llm = ChatOpenAI(
                model=settings.llm.name,
                temperature=settings.llm.temperature,
                api_key=settings.llm.api_key,
            )
        case "ollama":
            from langchain_community.chat_models.ollama import ChatOllama

            llm = ChatOllama(
                model=settings.llm.name, temperature=settings.llm.temperature
            )

        case "groq":
            from langchain_groq import ChatGroq

            llm = ChatGroq(
                model=settings.llm.name,
                temperature=settings.llm.temperature,
                api_key=settings.llm.api_key,
            )

        case "anthropic":
            from langchain_community.chat_models.anthropic import ChatAnthropic

            llm = ChatAnthropic(
                model_name=settings.llm.name,
                temperature=settings.llm.temperature,
                anthropic_api_key=settings.llm.api_key,
            )

        case "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os

            # Suppress logging warnings
            os.environ["GRPC_VERBOSITY"] = "ERROR"
            os.environ["GLOG_minloglevel"] = "2"

            llm = ChatGoogleGenerativeAI(
                model=settings.llm.name,
                temperature=settings.llm.temperature,
                api_key=settings.llm.api_key,
            )

        case "aws":
            from langchain_aws import ChatBedrock
            import boto3

            region, access_key, secret_key = settings.llm.api_key.split(" ")

            boto_client = boto3.client(
                "bedrock-runtime",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )

            llm = ChatBedrock(
                model_id=settings.llm.name,
                client=boto_client,
                model_kwargs={"temperature": settings.llm.temperature},
            )
    return llm
