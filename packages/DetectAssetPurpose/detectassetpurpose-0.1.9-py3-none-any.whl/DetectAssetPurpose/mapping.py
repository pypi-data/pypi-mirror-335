from dataclasses import asdict, dataclass, replace
from enum import Enum 
class StrEnum(str, Enum):  # ✅ Manually create StrEnum for Python 3.10
    pass

from typing import Any, TypedDict


class Purpose(StrEnum):
    BRAND_BUILDING = "brand_building"
    CONVERSION = "conversion"


@dataclass(frozen=True)
class Objectives:
    purpose: Purpose
    autodetected: bool
    reasoning: str



_defaults = Objectives(
    purpose=Purpose.BRAND_BUILDING,
    autodetected=True,
    reasoning="none provided",
)


def get_defaults():
    return asdict(_defaults)


def get_only_objectives(benchmark_settings: dict[str, Any]):
    return {
        k: v
        for k, v in benchmark_settings.items()
        if k
        in {
            "purpose",
        }
    }


def get_default_objectives():
    return get_only_objectives(get_defaults())


class _Mappings(TypedDict):
    purpose: dict[str, Purpose]


mappings: _Mappings = {
    "purpose": {
        "brand building": Purpose.BRAND_BUILDING,
        "conversion": Purpose.CONVERSION,
    },
}