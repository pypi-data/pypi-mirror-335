"""
question_dict.py

Drop-in replacement for `QuestionDict`, with dynamic creation of a Pydantic model 
to validate user responses automatically (just like QuestionNumerical).


Failure: 

```python { "first_name": "Kris", "last_name": "Rosemann", "phone": "(262) 506-6064", "email": "InvestorRelations@generac.com", "title": "Senior Manager Corporate Development & Investor Relations", "external": False } ``` The first name and last name are extracted directly from the text. The phone number and email are provided in the text. The title is also given in the text. The email domain "generac.com" suggests that it is an internal email address, so "external" is set to False.
"""

from __future__ import annotations
from typing import Union, Optional, Dict, List, Any, Type
from pydantic import BaseModel, Field, create_model, ValidationError
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path

from .question_base import QuestionBase
from .descriptors import (
    AnswerKeysDescriptor,
    ValueTypesDescriptor,
    ValueDescriptionsDescriptor,
    QuestionTextDescriptor,
)
from .response_validator_abc import ResponseValidatorABC
from .exceptions import QuestionCreationValidationError
from .decorators import inject_exception


def _parse_type_string(type_str: str) -> Any:
    """
    Very simplistic parser that can map:
      - "int"   -> int
      - "float" -> float
      - "str"   -> str
      - "list[str]" -> List[str]
      - ...
    Expand this as needed for more advanced usage.
    """
    type_str = type_str.strip().lower()
    if type_str == "int":
        return int
    elif type_str == "float":
        return float
    elif type_str == "str":
        return str
    elif type_str == "list":
        return List[Any]
    elif type_str.startswith("list["):
        # e.g. "list[str]" or "list[int]" etc.
        inner = type_str[len("list["):-1].strip()
        return List[_parse_type_string(inner)]
    # If none matched, return a very permissive type or raise an error
    return Any


def create_dict_response(
    answer_keys: List[str],
    value_types: List[str],
    permissive: bool = False,
) -> Type[BaseModel]:
    """
    Dynamically builds a Pydantic model that has:
      - an `answer` submodel containing your required keys
      - an optional `comment` field

    If `permissive=False`, extra keys in `answer` are forbidden.
    If `permissive=True`,  extra keys in `answer` are allowed.
    """

    # 1) Build the 'answer' submodel fields
    #    Each key is required (using `...`), with the associated type from value_types.
    field_definitions = {}
    for key, t_str in zip(answer_keys, value_types):
        python_type = _parse_type_string(t_str)
        field_definitions[key] = (python_type, Field(...))

    # Use Pydantic's create_model to construct an "AnswerSubModel" with these fields
    AnswerSubModel = create_model(
        "AnswerSubModel",
        __base__=BaseModel,
        **field_definitions
    )

    # 2) Define the top-level model with `answer` + optional `comment`
    class DictResponse(BaseModel):
        answer: AnswerSubModel
        comment: Optional[str] = None
        generated_tokens: Optional[Any] = Field(None)

        class Config:
            # If permissive=False, forbid extra keys in `answer`
            # If permissive=True, allow them
            extra = "allow" if permissive else "forbid"

    return DictResponse


class DictResponseValidator(ResponseValidatorABC):
    """Optional placeholder if you still want a validator class around it."""
    required_params = ["answer_keys", "permissive"]

    valid_examples = [
        (
            {
                "answer": {
                    "name": "Hot Chocolate",
                    "num_ingredients": 5,
                    "ingredients": ["milk", "cocoa", "sugar"]
                }
            },
            {
                "answer_keys": ["name", "num_ingredients", "ingredients"],
                "value_types": ["str", "int", "list[str]"]
            },
        )
    ]
    invalid_examples = [
        (
            {"answer": {"name": 123}},  # Name should be a string
            {"answer_keys": ["name"], "value_types": ["str"]},
            "Key 'name' has value of type int, expected str",
        ),
        (
            {"answer": {"ingredients": "milk"}},  # Should be a list
            {"answer_keys": ["ingredients"], "value_types": ["list[str]"]},
            "Key 'ingredients' should be a list, got str",
        )
    ]


class QuestionDict(QuestionBase):
    """A QuestionDict allows you to create questions that expect dictionary responses
    with specific keys and value types. It dynamically builds a pydantic model
    so that Pydantic automatically raises ValidationError for missing/invalid fields.

    Documentation: https://docs.expectedparrot.com/en/latest/questions.html#questiondict

    Parameters
    ----------
    question_name : str
        Unique identifier for the question
    question_text : str
        The actual question text presented to users
    answer_keys : List[str]
        Keys that must be provided in the answer dictionary
    value_types : Optional[List[Union[str, type]]]
        Expected data types for each answer key
    value_descriptions : Optional[List[str]]
        Human-readable descriptions for each answer key
    include_comment : bool
        Whether to allow additional comments with the answer
    question_presentation : Optional[str]
        Alternative way to present the question
    answering_instructions : Optional[str]
        Additional instructions for answering
    permissive : bool
        If True, allows additional keys not specified in answer_keys
    """

    question_type = "dict"
    question_text: str = QuestionTextDescriptor()
    answer_keys: List[str] = AnswerKeysDescriptor()
    value_types: Optional[List[str]] = ValueTypesDescriptor()
    value_descriptions: Optional[List[str]] = ValueDescriptionsDescriptor()

    _response_model = None
    response_validator_class = DictResponseValidator

    def __init__(
        self,
        question_name: str,
        question_text: str,
        answer_keys: List[str],
        value_types: Optional[List[Union[str, type]]] = None,
        value_descriptions: Optional[List[str]] = None,
        include_comment: bool = True,
        question_presentation: Optional[str] = None,
        answering_instructions: Optional[str] = None,
        permissive: bool = False,
    ):
        self.question_name = question_name
        self.question_text = question_text
        self.answer_keys = answer_keys
        self.value_types = self._normalize_value_types(value_types)
        self.value_descriptions = value_descriptions
        self.include_comment = include_comment
        self.question_presentation = question_presentation or self._render_template(
            "question_presentation.jinja"
        )
        self.answering_instructions = answering_instructions or self._render_template(
            "answering_instructions.jinja"
        )
        self.permissive = permissive

        # Validation
        if self.value_types and len(self.value_types) != len(self.answer_keys):
            raise QuestionCreationValidationError(
                "Length of value_types must match length of answer_keys."
            )
        if self.value_descriptions and len(self.value_descriptions) != len(self.answer_keys):
            raise QuestionCreationValidationError(
                "Length of value_descriptions must match length of answer_keys."
            )

    def create_response_model(self) -> Type[BaseModel]:
        """
        Build and return the Pydantic model that should parse/validate user answers.
        This is similar to `QuestionNumerical.create_response_model`, but for dicts.
        """
        return create_dict_response(
            answer_keys=self.answer_keys,
            value_types=self.value_types or [],
            permissive=self.permissive
        )

    def _get_default_answer(self) -> Dict[str, Any]:
        """Build a default example answer based on the declared types."""
        if not self.value_types:
            # If user didn't specify types, return some default structure
            return {
                "title": "Sample Recipe",
                "ingredients": ["ingredient1", "ingredient2"],
                "num_ingredients": 2,
                "instructions": "Sample instructions"
            }

        answer = {}
        for key, type_str in zip(self.answer_keys, self.value_types):
            t_str = type_str.lower()
            if t_str.startswith("list["):
                # e.g. list[str], list[int], etc.
                inner = t_str[len("list["):-1].strip()
                if inner == "str":
                    answer[key] = ["sample_string"]
                elif inner == "int":
                    answer[key] = [1]
                elif inner == "float":
                    answer[key] = [1.0]
                else:
                    answer[key] = []
            elif t_str == "str":
                answer[key] = "sample_string"
            elif t_str == "int":
                answer[key] = 1
            elif t_str == "float":
                answer[key] = 1.0
            elif t_str == "list":
                answer[key] = []
            else:
                # fallback
                answer[key] = None
        return answer

    def _render_template(self, template_name: str) -> str:
        """Render a template using Jinja."""
        try:
            template_dir = Path(__file__).parent / "templates" / "dict"
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template(template_name)
            return template.render(
                question_name=self.question_name,
                question_text=self.question_text,
                answer_keys=self.answer_keys,
                value_types=self.value_types,
                value_descriptions=self.value_descriptions,
                include_comment=self.include_comment,
            )
        except TemplateNotFound:
            return f"Template {template_name} not found in {template_dir}."

    @staticmethod
    def _normalize_value_types(value_types: Optional[List[Union[str, type]]]) -> Optional[List[str]]:
        """
        Convert all value_types to string representations (e.g. "int", "list[str]", etc.).
        This logic is similar to your original approach but expanded to handle
        python `type` objects as well as string hints.
        """
        if not value_types:
            return None

        def normalize_type(t) -> str:
            # Already a string?
            if isinstance(t, str):
                return t.lower().strip()

            # It's a Python built-in type?
            if hasattr(t, "__name__"):
                if t.__name__ == "List":
                    return "list"
                # For int, float, str, etc.
                return t.__name__.lower()

            # If it's a generic type like List[str], parse from its __origin__ / __args__
            # or fallback:
            return str(t).lower()

        return [normalize_type(t) for t in value_types]

    def to_dict(self, add_edsl_version: bool = True) -> dict:
        """Serialize to JSON-compatible dictionary."""
        return {
            "question_type": self.question_type,
            "question_name": self.question_name,
            "question_text": self.question_text,
            "answer_keys": self.answer_keys,
            "value_types": self.value_types or [],
            "value_descriptions": self.value_descriptions or [],
            "include_comment": self.include_comment,
            "permissive": self.permissive,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'QuestionDict':
        """Recreate from a dictionary."""
        return cls(
            question_name=data["question_name"],
            question_text=data["question_text"],
            answer_keys=data["answer_keys"],
            value_types=data.get("value_types"),
            value_descriptions=data.get("value_descriptions"),
            include_comment=data.get("include_comment", True),
            permissive=data.get("permissive", False),
        )

    @classmethod
    @inject_exception
    def example(cls) -> 'QuestionDict':
        """Return an example question."""
        return cls(
            question_name="example",
            question_text="Please provide a simple recipe for hot chocolate.",
            answer_keys=["title", "ingredients", "num_ingredients", "instructions"],
            value_types=["str", "list[str]", "int", "str"],
            value_descriptions=[
                "The title of the recipe.",
                "A list of ingredients.",
                "The number of ingredients.",
                "The instructions for making the recipe."
            ],
        )

    def _simulate_answer(self) -> dict:
        """Simulate an answer for the question."""
        return {
            "answer": self._get_default_answer(),
            "comment": None
        }


if __name__ == "__main__":
    q = QuestionDict.example()
    print(q.to_dict())
