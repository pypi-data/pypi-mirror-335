class _AnywayMaximum:
    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __le__(self, other):
        return self == other

    def __lt__(self, other):
        return False

    def __ge__(self, other):
        return True

    def __gt__(self, other):
        return self != other


class _AnywayMinimum:
    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __le__(self, other):
        return True

    def __lt__(self, other):
        return self != other

    def __ge__(self, other):
        return self == other

    def __gt__(self, other):
        return False


ANYWAY_MAXIMUM = _AnywayMaximum()
ANYWAY_MINIMUM = _AnywayMinimum()
