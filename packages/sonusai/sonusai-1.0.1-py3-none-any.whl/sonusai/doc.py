"""sonusai doc

usage: doc [-h] [TOPIC]

options:
   -h, --help   Display this help.

Show SonusAI documentation.

"""


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    from sonusai import doc

    topic = args["TOPIC"]

    print(f"SonusAI {sai_version} Documentation")
    print("")

    topics = sorted([item[4:] for item in dir(doc) if item.startswith("doc_")])

    if topic not in topics:
        if topic is not None:
            print(f"Unknown topic: {topic}")
            print("")

        print("Available topics:")
        for item in topics:
            print(f"  {item}")
        return

    text = getattr(doc, "doc_" + topic)()
    print(text[1:])


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)
