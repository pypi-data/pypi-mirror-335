"""Functions creating validators"""

from .helperModels import ValidatorModel


def numberValidator(
    minValue: int = None, maxValue: int = None, error: str = None
) -> ValidatorModel:
    """A validator for number values.

    Args:
        minValue (int): Minimum value for the number validator.
        maxValue (int): Maximum value for the number validator.
        error (str): Custom error text to display. Optional.
    """
    return ValidatorModel(
        type="number", minValue=minValue, maxValue=maxValue, text=error
    )


def textValidator(
    minLength: int = None,
    maxLength: int = None,
    allowDigits: bool = True,
    error: str = None,
) -> ValidatorModel:
    """A validator for text values.

    Args:
        minLength (int): Minimum length for the text validator.
        maxLength (int): Maximum length for the text validator.
        allowDigits (bool): Whether to allow digits for the text validator. Default is True.
        error (str): Custom error text to display. Optional.
    """
    return ValidatorModel(
        type="text",
        allowDigits=allowDigits,
        minLength=minLength,
        maxLength=maxLength,
        text=error,
    )


def emailValidator(error: str = None) -> ValidatorModel:
    """A validator for email values.

    Args:
        error (str): Custom error text to display. Optional
    """
    return ValidatorModel(type="email", text=error)


def expressionValidator(expression: str = None, error: str = None) -> ValidatorModel:
    """An expression based validator.

    Args:
        expression (str): Expression for the expression validator.
        error (str): Custom error text to display. Optional
    """
    return ValidatorModel(type="expression", expression=expression, text=error)


def answerCountValidator(
    minCount: int = None, maxCount: int = None, error: str = None
) -> ValidatorModel:
    """A validator for answer count.

    Args:
        minCount (int): Minimum count for the answer count validator.
        maxCount (int): Maximum count for the answer count validator.
        error (str): Custom error text to display. Optional
    """
    return ValidatorModel(
        type="answercount", minCount=minCount, maxCount=maxCount, text=error
    )


def regexValidator(regex: str = None, error: str = None) -> ValidatorModel:
    """A regex based validator.

    Args:
        regex (str): Regular expression for the regex validator.
        error (str): Custom error text to display. Optional
    """
    return ValidatorModel(type="regex", regex=regex, text=error)
