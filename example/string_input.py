from interfaces import Input


class StringInput(Input):
    def __init__(self, input: str):

        self.s = input

    def get_input(self) -> str:
        return self.s
