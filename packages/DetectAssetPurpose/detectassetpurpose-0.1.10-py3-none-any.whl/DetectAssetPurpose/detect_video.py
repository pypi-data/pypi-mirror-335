from base64 import b64encode
from dataclasses import asdict, replace
from typing import Any
import os
from functools import lru_cache 
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("LANGCHAIN_API_KEY")

import langsmith

from DetectAssetPurpose.mapping import (
    _defaults,
    Objectives,
)

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
            "# Video asset to be analysed is provided below:\n{asset}"
        ),
    ]
)

@lru_cache
def _get_tracer():
    return LangChainTracer(
        project_name="Objective Detection",
        client=langsmith.Client(api_key=api_key),
    )


def detect_video_objectives(video_uri: str) -> dict[str, Any]:
    """
    Detect objectives for a video using Vertex AI.
    
    Args:
        video_uri: URI of the video file (e.g., gs://bucket-name/video.mp4).

    Returns:
        A dictionary containing the detected objectives.
    """
    chain = _prompt | _chat | JsonOutputParser()
    generated: dict[str, str] = chain.invoke(
        {
            "asset": video_uri,
        },
        config={
            "callbacks": [_get_tracer()],
            "tags": ["video"],
        },
    )
    print("Generated Output Keys:", generated.keys())

    combined_data = {**asdict(_defaults), **generated}

    return asdict(
        replace(
            Objectives(**combined_data),
            autodetected=True,
        )
    )
