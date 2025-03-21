# WHAT THIS FILE DOES
# it makes a custom exception class, i can raise it whenever i please

class PointerNotInRangeError(Exception):
    def __init__(self, message, position):
        self.message = message
        super().__init__(message)
        self.position = position

    def __str__(self):
        return str(f"{self.message}: Caught at character {self.position}")
    