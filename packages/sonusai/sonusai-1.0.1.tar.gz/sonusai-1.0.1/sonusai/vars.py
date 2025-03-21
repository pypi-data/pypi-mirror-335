"""sonusai vars

usage: vars [-h]

options:
   -h, --help   Display this help.

List custom SonusAI variables.

"""


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils import trim_docstring

    docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    from os import environ
    from os import getenv

    from sonusai.constants import DEFAULT_NOISE

    print("Custom SonusAI variables:")
    print("")
    print(f"${{default_noise}}: {DEFAULT_NOISE}")
    print("")
    print("SonusAI recognized environment variables:")
    print("")
    print(f"DEEPGRAM_API_KEY {getenv('DEEPGRAM_API_KEY')}")
    print(f"GOOGLE_SPEECH_API_KEY {getenv('GOOGLE_SPEECH_API_KEY')}")
    print("")
    items = ["DEEPGRAM_API_KEY", "GOOGLE_SPEECH_API_KEY"]
    items += [item for item in environ if item.upper().startswith("AIXP_WHISPER_")]


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)
