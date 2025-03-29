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
    type: str
    coordinates: List[int] = Field([0, 0, 0, 0], min_items=4, max_items=4)
    markers: List[int] = Field([0, 0, 0, 0], min_items=4, max_items=4)

    @field_validator('type')
    def validate_type(cls, v):
        """Validate region type is one of the supported types"""
        if v not in [r.value for r in RegionType]:
            raise ValueError(f'Invalid region type: {v}. Supported types: {", ".join(RegionType.__members__)}') # noqa
        return v

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


def convert_template_to_dict(template: Template) -> dict:
    """
    Convert a Pydantic model to a dictionary.
    This is needed because Template model dump does not display keys in the order they are defined.
    It's also useful for removing markers from the output.

    Args:
        template: Template model

    Returns:
        dict: Dictionary representation of the template with keys in the order they are defined
    """

    result = {
        'form_type': template.form_type,
        'form_title': template.form_title,
        'length': template.length,
        'width': template.width,
        'use_coordinates': template.use_coordinates,
        'regions': []
    }

    for region in template.regions:
        if template.use_coordinates:
            result['regions'].append({
                'name': region.name,
                'type': region.type,
                'coordinates': region.coordinates,
            })
        else:
            result['regions'].append({
                'name': region.name,
                'type': region.type,
                'markers': region.markers,
            })

    return result


def validate_template_file(file_path: str) -> Template:
    """
    Validate a YAML template file using Pydantic models

    Args:
        file_path: Path to the YAML template file

    Returns:
        Template: Validated template model

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
