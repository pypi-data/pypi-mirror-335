def register_keyboard_interrupt() -> None:
    import signal

    def signal_handler(_sig, _frame):
        import sys

        from sonusai import logger

        logger.info("Canceled due to keyboard interrupt")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
