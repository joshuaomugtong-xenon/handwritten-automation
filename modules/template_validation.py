from pydantic import BaseModel, Field, field_validator
from typing import List
from enum import Enum
import yaml


class RegionType(str, Enum):
    TEXT = 'text'
    CHECKBOX = 'checkbox'
    ENCIRCLEMENT = 'encirclement'


class Region(BaseModel):
    """Model representing a single region in the template"""
    name: str
    type: RegionType
    coordinates: List[int] = Field([0, 0, 0, 0], min_items=4, max_items=4)
    markers: List[int] = Field([0, 0, 0, 0], min_items=4, max_items=4)

    @field_validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate coordinates are in [x1, y1, x2, y2] format"""
        if len(v) != 4:
            raise ValueError('Coordinates must have exactly 4 values [x1, y1, x2, y2]') # noqa
        x1, y1, x2, y2 = v
        if x1 >= x2 or y1 >= y2:
            raise ValueError('Coordinates must be in format [x1, y1, x2, y2] where x1 < x2 and y1 < y2') # noqa
        return v

    @field_validator('markers')
    def validate_markers(cls, v):
        """Validate markers are in [x1, y1, x2, y2] format"""
        if len(v) != 4:
            raise ValueError('Markers must have exactly 4 values [x1, y1, x2, y2]') # noqa
        return v


class Template(BaseModel):
    """Model representing a template"""
    form_type: str
    form_title: str
    length: int = Field(..., gt=0)
    width: int = Field(..., gt=0)
    use_coordinates: bool = False
    regions: List[Region]


def validate_template_file(file_path: str) -> Template:
    """
    Validate a YAML template file using Pydantic models

    Args:
        file_path: Path to the YAML template file

    Returns:
        TemplateModel: Validated template model

    Raises:
        ValueError: If validation fails
    """
    try:
        # Load YAML file
        with open(file_path, 'r') as f:
            yaml_data = yaml.safe_load(f)

        # Create and validate Pydantic model
        template = Template(**yaml_data)
        return template

    except Exception as e:
        raise ValueError(f"Template validation failed: {str(e)}")
