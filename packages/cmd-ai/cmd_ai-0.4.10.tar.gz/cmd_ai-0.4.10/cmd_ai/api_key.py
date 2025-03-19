#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'
"""
import os

from fire import Fire

from cmd_ai import config
from cmd_ai.version import __version__

# ===============================================================================================


def get_api_key():
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # print("KEY from ENV  ===  ", openai_api_key )
    if (openai_api_key == "") or (openai_api_key == None):
        # print("X... {fg.red} NO KEY in ENV.... {fg.default}")
        with open(os.path.expanduser("~/.openai.token")) as f:
            res = f.readlines()[0].strip()
        if not res is None and res != "":
            openai_api_key = res
        else:
            print("X... I need OPENAI_API_KEY  set !!!!!")
            print("X... {fg.red} export OPENAI_API_KEY= {fg.default}")
            sys.exit(1)

    # print("KEY ... final  ===  ", openai_api_key )
    # openai.api_key = openai_api_key
    return openai_api_key



def get_api_key_anthropic():
    openai_api_key = os.getenv("ANTHROPIC_API_KEY")

    # print("KEY from ENV  ===  ", openai_api_key )
    if (openai_api_key == "") or (openai_api_key == None):
        # print("X... {fg.red} NO KEY in ENV.... {fg.default}")
        with open(os.path.expanduser("~/.openai_anthropic.token")) as f:
            res = f.readlines()[0].strip()
        if not res is None and res != "":
            openai_api_key = res
        else:
            print("X... I need ANTHROPIC_API_KEY  set !!!!!")
            print("X... {fg.red} export ANTHROPIC_API_KEY= {fg.default}")
            sys.exit(1)

    # print("KEY ... final  ===  ", openai_api_key )
    # openai.api_key = openai_api_key
    return openai_api_key


if __name__ == "__main__":
    print("i... in the __main__ of unitname of cmd_ai")
    Fire()
