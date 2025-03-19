from base64 import b64encode
from dataclasses import asdict, replace
from io import BytesIO
from PIL import Image
from functools import lru_cache
from typing import Any
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("LANGCHAIN_API_KEY")

import langsmith

from DetectAssetPurpose.mapping import (
    _defaults,
    Objectives,
)

from django.conf import settings
from langchain.callbacks import LangChainTracer
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_google_vertexai import ChatVertexAI

import yaml
from pathlib import Path
config_path = Path(__file__).parent / "config.yaml"
print(f"🔍 Looking for config.yaml at: {config_path}")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)


# Detect Objectives > Image v14
purpose_autodetection = config["process_a"]["PURPOSE_AUTODETECTION"]

prompt = (
    f"{purpose_autodetection['role']}\n\n"
    f"Knowledge Sharing:\n"
    f"{purpose_autodetection['knowledge-sharing']['section-description']}\n\n"
    f"Key Concepts:\n{purpose_autodetection['knowledge-sharing']['key-concepts']}\n\n"
    f"Input Overview:\n{purpose_autodetection['input-overview']}\n\n"
    f"Task:\n{purpose_autodetection['task']}\n\n"
    f"Instruction:\n{purpose_autodetection['instruction']}\n\n"
    f"Response:\n{purpose_autodetection['response']}\n\n"
    f"Overview:\n{purpose_autodetection['overview']}\n\n"
    f"Template:\n{purpose_autodetection['template']}\n\n"
    f"Example:\n{purpose_autodetection['example']}"
)


_chat = ChatVertexAI(
    model_name="gemini-1.5-pro-002",
    max_output_tokens=2048,
    temperature=0.1,
)

_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=prompt),
        HumanMessagePromptTemplate.from_template(
            [
                {
                    "text": "# Asset to be analysed is provided below:",
                },
                {
                    "image_url": "{asset}",
                },
            ]
        ),
    ]
)

def convert_to_jpeg(image: bytes):
    with Image.open(BytesIO(image)) as img:
        buf = BytesIO()

        if img.mode != "RGB":
            img = img.convert("RGB")

        img.save(buf, format="jpeg")

        return buf.getvalue()


def fit_to_filesize(img: bytes, filesize: int):
    while filesize < len(img):
        with Image.open(BytesIO(img)) as m:
            buf = BytesIO()
            m.resize((int(m.width * 0.8), int(m.height * 0.8))).save(
                buf,
                format=m.format,
            )

            img = buf.getvalue()

    return img
  
# This little bastard throws an exception during initialitation if the api key isn't valid.
# During testing, we wont have any api key, this can't be in global state - so we go the
# classic Pythonic "technically not global state" route to circumvent that issue.
@lru_cache
def _get_tracer():
    return LangChainTracer(
        project_name="Objective Detection",
        client=langsmith.Client(api_key=api_key),
    )


def detect_image_objectives(img: bytes) -> dict[str, Any]:
    # VertexAI either has a bug in their SDK, or doesn't support WebP
    # images as of yet. For this reason, we'll convert all images to
    # trusty old JPEG. The same approach is taken for AI insights.
    # TODO Investigate whether/how VertexAI supports WebP images
    img = convert_to_jpeg(img)
    img = fit_to_filesize(img, 5000000)

    chain = _prompt | _chat | JsonOutputParser()
    generated: dict[str, str] = chain.invoke(
        {
            "asset": f"data:image/jpeg;base64,{b64encode(img).decode()}",
        },
        config={
            "callbacks": [_get_tracer()],
            "tags": ["image"],
        },
    )
    print("Generated Output Keys:", generated.keys())

    # Combine defaults with generated data
    combined_data = {**asdict(_defaults), **generated}

    return asdict(
        replace(
            Objectives(**combined_data),
            autodetected=True,
        )
    )