from typing import Any, TypedDict, List, Optional
from pydantic import BaseModel, field_validator
from .logger import logger  # Custom logger for warnings and errors


class ValidatedItemDict(TypedDict):
    """
    A type-hinted dictionary for a validated item.
    It expects a strict set of keys with defined types:
    - title: Optional[str]
    - content: List[str]
    - images: List[dict]
    """
    title: Optional[str]
    content: List[str]
    images: List[dict]


class UnvalidatedItemModel(BaseModel):
    """
    Model for one element of the unvalidated structure.
    This is used to process incoming items that may contain extra keys.
    """
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[dict]] = None

    class Config:
        extra = "allow"  # Allow any additional keys beyond those explicitly defined

    @field_validator('title', 'content', mode='before')
    def convert_to_str(cls, value):
        """
        Validator for 'title' and 'content' fields.
        - If the value is None, it is returned unchanged.
        - If the value is a string, it is returned unchanged.
        - If the value is numeric (int or float), it is converted to a string.
        - For other types, the value is left unchanged (you may raise an error if needed).
        """
        if value is None:
            return value
        elif isinstance(value, str):
            return value
        # If the value is numeric, convert it to a string.
        elif isinstance(value, (int, float)):
            logger.warning("Received numeric value instead of an expected string")
            return str(value)
        # For other types, leave the value unchanged.
        elif not isinstance(value, str):
            logger.warning("Received non-string value instead of an expected string")
            return None
        return value

    @field_validator('images', mode='before')
    def filter_images(cls, v):
        """
        Validator for the 'images' field.
        - If the input value is not a list, returns an empty list (indicating no images).
        - If it is a list, filters and retains only items of type dict.
        """
        if not isinstance(v, list):
            logger.warning(f"Invalid type for images: expected list, got {type(v)}")
            return []
        len_before = len(v)
        result_v = [i for i in v if isinstance(i, dict)]
        if len(result_v) != len_before:
            logger.warning(
                f"Filtered out non-dict items. Original length: {len_before}, filtered length: {len(result_v)}")
        return result_v


class UnvalidatedRootModel(BaseModel):
    """
    Model for the input structure.
    This model requires the key 'separate_information_relations', which contains the data used to augment the document.
    """
    separate_information_relations: List[Any]  # Initially accepts arbitrary elements

    class Config:
        extra = "allow"  # Allow extra fields at the top level


class ValidatedItemModel(BaseModel):
    """
    Model for a validated item.
    This model only allows the expected keys (any extra keys are forbidden).
    """
    title: Optional[str] = None
    content: List[str] = []
    images: List[dict] = []

    class Config:
        extra = "forbid"  # Forbid any additional keys that are not explicitly defined


def validate_data_pydantic(raw: dict) -> List[ValidatedItemDict]:
    """
    Validates and transforms the input data.

    .. note::
        This function should be used within a try-except block since the absence of the key
        'separate_information_relations' or unexpected values during validation will raise an error.

    Transformation logic:
    - Check if the input structure contains the key 'separate_information_relations'.
    - Process each element within 'separate_information_relations'.
    - Retain only the expected keys (other keys are not included in the validated result).
    - Split the 'content' string into paragraphs if newline characters are present.
    - Return a list of dictionaries, each containing only the expected keys.
    """
    # Convert input data into an UnvalidatedRootModel instance (this validates the presence of 'separate_information_relations')
    root = UnvalidatedRootModel(**raw)
    validated_result: List[ValidatedItemDict] = []  # List to accumulate validated items

    for item_any in root.separate_information_relations:
        # Convert each element into an UnvalidatedItemModel.
        # If the element is not a dict, an empty dict is used instead.
        unvalidated_item = UnvalidatedItemModel(**(item_any if isinstance(item_any, dict) else {}))

        # Split the content string into a list of strings using newline as a delimiter.
        content_list = unvalidated_item.content.split('\n') if isinstance(unvalidated_item.content, str) else []

        # Get the images list, or use an empty list if images are absent.
        images_list = unvalidated_item.images if isinstance(unvalidated_item.images, list) else []

        # If the item contains no information, skip creating a validated item.
        if not unvalidated_item.title and not content_list and not images_list:
            continue

        # Create a validated item with the available information.
        validated_item = ValidatedItemModel(
            title=unvalidated_item.title,
            content=content_list,
            images=images_list
        )
        # Convert the validated model to a dictionary and add it to the result list.
        validated_result.append(validated_item.model_dump())

    return validated_result


if __name__ == "__main__":
    # Example input data for testing the validation function.
    input_data = {
        'separate_information_relations': [
            {
                'title': 'my_header',
                'content': 'First row\nSecond row',
                'images': {"file":['base64text', 3, 'third element (prev was invalid)']}
            },
        ]
    }
    print('---------INPUT---------')
    print(input_data)

    # Validate the input data using the function.
    res = validate_data_pydantic(input_data)

    print('---------RESULT--------')
    print(res)
    print(type(res))

    print('------SINGLE-ITEM------')
    for item in res:
        print(type(item))
        print(item)
