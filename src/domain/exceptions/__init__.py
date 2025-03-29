class UnitMismatchError(Exception):
    def __init__(
        self,
        message="You can't sum cows and pigs at the same time: Please drink a coffee and try again",
    ):
        self.message = message
        super().__init__(self.message)


class ValueOutOfRangeError(Exception):
    pass


class NoValuesError(Exception):
    pass
