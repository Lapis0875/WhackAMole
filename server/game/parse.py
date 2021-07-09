from contextlib import suppress
from typing import Final, List, Any, Tuple, Union

__all__ = (
    'ExprParseException',
    'BOOL_TRUE_CHARS', 'BOOL_FALSE_CHARS', 'BooleanExprParseException', 'parse_boolean_expr',
    'NumberExprParseException', 'parse_number_expr',
    'STRING_CHAR', 'StringExprParseException', 'parse_string_expr',
    'ContainerExprParseException', 'parse_element',
    'LIST_START_CHAR', 'LIST_END_CHAR', 'LIST_SEP_CHAR', 'ListExprParseException', 'parse_list_expr'
)


"""
Object Expressions
"""


class ExprParseException(Exception):
    expr: str
    description: str
    """Base class of Expression Parse Exception."""
    def __init__(self, expr: str, description: str, *args, **kwargs):
        super(ExprParseException, self).__init__(*args)
        self.expr = expr
        self.description = description

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}[expr={self.expr},description={self.description}]'


# Boolean Expression Parser
BOOL_TRUE_CHARS: Final[Tuple[str, ...]] = ('true', 'True')
BOOL_FALSE_CHARS: Final[Tuple[str, ...]] = ('false', 'False')


class BooleanExprParseException(ExprParseException):
    def __init__(self, expr: str):
        super(BooleanExprParseException, self).__init__(expr, f'{expr} is invalid boolean token.')


def parse_boolean_expr(expr: str) -> bool:
    if expr in BOOL_TRUE_CHARS:
        return True
    elif expr in BOOL_FALSE_CHARS:
        return False
    else:
        raise BooleanExprParseException(expr)


# Number Expression Parser


class NumberExprParseException(ExprParseException):
    def __init__(self, expr: str, description: str):
        super(NumberExprParseException, self).__init__(expr, description)


def parse_number_expr(expr: str) -> Union[int, float]:
    if expr.isnumeric():
        return int(expr)
    elif expr.count('e') == 1:
        try:
            return int(expr)
        except ValueError:
            raise NumberExprParseException(expr, f'{expr} is using invalid large-number expression: 3E6 = 3×10^6')

    elif expr.isdecimal():
        return float(expr)
    else:
        raise NumberExprParseException(expr, f'{expr} is not a valid number token.')


# Boolean Expression Parser
STRING_CHAR: Final[str] = '"'


class StringExprParseException(ExprParseException):
    def __init__(self, expr: str, description: str):
        super(StringExprParseException, self).__init__(expr, description)


def parse_string_expr(expr: str) -> str:
    if not (expr.startswith(STRING_CHAR) and expr.endswith(STRING_CHAR)):
        raise StringExprParseException(expr, f'{expr} does not captured with string token `{STRING_CHAR}`')

    content: str = expr[1:-1]
    if STRING_CHAR in content:
        raise StringExprParseException(expr, f'{expr} has been improperly captured : more than two string token is used.')

    return content


"""
Container Expressions
"""


class ContainerExprParseException(ExprParseException):
    def __init__(self, expr: str, description: str):
        super(ContainerExprParseException, self).__init__(expr, description)


def parse_element(element_expr: str) -> object:
    # Try parse as boolean.
    with suppress(BooleanExprParseException):
        return parse_boolean_expr(element_expr)
    # Try parse as number.
    with suppress(NumberExprParseException):
        return parse_number_expr(element_expr)
    # Try parse as string.
    with suppress(StringExprParseException):
        return parse_string_expr(element_expr)

    # Failed in all cases.
    # Currently, all failed cases are interpreted as string, due to the lack of types.
    # Will raise exception in future.
    return element_expr     # as string.


# List Expression Parser
LIST_START_CHAR: Final[str] = '['
LIST_END_CHAR: Final[str] = ']'
LIST_SEP_CHAR: Final[str] = ','


class ListExprParseException(ExprParseException):
    def __init__(self, expr: str, description: str):
        super(ListExprParseException, self).__init__(expr, description)


def parse_list_expr(expr: str) -> List[Any]:
    if not (expr.startswith(LIST_START_CHAR) and expr.endswith(LIST_END_CHAR)):
        raise ListExprParseException(expr, 'Improper List Start/Close Token.')

    elements: List[str] = expr[1:-1].split(LIST_SEP_CHAR)
    # Objects in Container check.
    obj: List[Any] = list(map(parse_element, elements))
    return obj





