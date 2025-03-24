import os
from pathlib import Path
from typing import Any

from environs import Env

from liblaf import actions

env = Env(prefix="INPUT_")


def get_input(name: str) -> str:
    val: str = env.str(name.replace(" ", "_").upper(), "")
    return val.strip()


def get_multiline_input(name: str) -> list[str]:
    return list(actions.utils.splitlines(get_input(name)))


def notice(message: str) -> None:
    print(f"::notice::{message}")


def set_output(name: str, value: Any) -> None:
    fpath: Path = Path(os.getenv("GITHUB_OUTPUT", ""))
    with fpath.open("a") as fp:
        fp.write(f"{name}={value}\n")
