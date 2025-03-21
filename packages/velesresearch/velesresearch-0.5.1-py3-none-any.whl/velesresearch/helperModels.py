"""Classes for additional SurveyJS elements"""

import warnings
from pydantic import BaseModel
from pydantic.functional_validators import model_validator
from .utils import dict_without_defaults


class ValidatorModel(BaseModel):
    """Validator dictionary generator

    Args:
        type (str): The type of the validator. Can be 'number', 'text', 'email', 'expression', 'answercount', 'regex'.
        text (str): Custom error text to display. Optional.
        maxValue (int): Maximum value for the number validator.
        minValue (int): Minimum value for the number validator.
        allowDigits (bool): Whether to allow digits for the text validator. Default is True.
        maxLength (int): Maximum length for the text validator.
        minLength (int): Minimum length for the text validator.
        expression (str): Expression for the expression validator.
        maxCount (int): Maximum count for the answer count validator.
        minCount (int): Minimum count for the answer count validator.
        regex (str): Regular expression for the regex validator.
    """

    type: str
    text: str | None = None
    # numericValidator
    minValue: int | None = None
    maxValue: int | None = None
    # textValidator
    allowDigits: bool = True
    minLength: int | None = None
    maxLength: int | None = None
    # expressionValidator
    expression: str | None = None
    # answerCountValidator
    minCount: int | None = None
    maxCount: int | None = None
    # regexValidator
    regex: str | None = None

    @model_validator(mode="before")
    def check_type_and_arguments(cls, values):
        if isinstance(values, list):
            values = values[0].dict()
        type_ = values["type"]

        # Define valid types and related fields for each type
        type_field_map = {
            "number": ["maxValue", "minValue"],
            "text": ["allowDigits", "maxLength", "minLength"],
            "email": [],
            "expression": ["expression"],
            "answercount": ["maxCount", "minCount"],
            "regex": ["regex"],
        }

        # Ensure type is valid
        if type_ not in type_field_map:
            raise ValueError(
                f"Invalid type '{type_}'. Must be one of {list(type_field_map.keys())}."
            )

        # Warn if fields irrelevant to the given type are provided
        relevant_fields = type_field_map[type_]
        irrelevant_fields = [
            field
            for field in values.keys()
            if field not in relevant_fields
            and field not in ["type", "text"]
            and values.get(field) is not None
        ]

        if irrelevant_fields:
            warnings.warn(
                f"For type '{type_}', the following fields are irrelevant and were provided: {', '.join(irrelevant_fields)}"
            )

        return values

    def dict(self):
        return dict_without_defaults(self)
