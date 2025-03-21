from typing import Any


class RandomChoice:
    def __init__(self, data: list, repetition: bool = False):
        self.data = data
        self.repeat = repetition
        self.choices: list = []

    def next(self) -> Any:
        from random import choice
        from random import sample

        if self.repeat:
            return choice(self.data)  # noqa: S311

        if not self.choices:
            self.choices = sample(self.data, len(self.data))

        return self.choices.pop()


class SequentialChoice:
    def __init__(self, data: list):
        self.data = data
        self.choices: list = []

    def next(self) -> Any:
        if not self.choices:
            self.choices = self.data.copy()
        return self.choices.pop()
