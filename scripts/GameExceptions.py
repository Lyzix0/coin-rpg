class PlaceException(Exception):
    def __str__(self):
        return f"Нельзя применять place на один объект дважды."


class DirectInitException(Exception):
    def __str__(self):
        return f"x и y должны принимать значения от -1 до 1"


class NotPlacedException(Exception):
    def __str__(self):
        return f"Объект не может нарисован, его нужно разместить на игровом поле"
