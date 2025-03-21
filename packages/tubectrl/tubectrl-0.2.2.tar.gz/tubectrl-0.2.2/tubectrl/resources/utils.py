from typing import Any

from ..schemas import Filter, OptionalParameters, Part, YouTubeRequest


def generate_part(part: Part) -> str:
    """Generate the 'Part' for a request.

    Parameters
    ----------
    part: Part
        An instance of part that contains all the required details.
    """
    part_str: str = ",".join(part.part)
    return part_str


def generate_optional_parameters(optional_params: OptionalParameters) -> dict[str, Any]:
    """Generate Optional parmateers for a request.

    Parameters
    ----------
    optional_parameters: OptionalParameters
        Optional parameters used when sending the request
    """
    optional: dict[str, Any] = dict()
    for key, value in optional_params.model_dump().items():
        #  We only want optional parameters that were provided
        if value:
            optional[key] = value
    #  This is useful when sending search request and type is provided as a list i.e ['video']
    if optional_params.model_dump().get("type"):
        optional["type"] = ",".join(optional_params.type)
    return optional


def generate_filter(request_filter: Filter) -> dict[str, Any]:
    """Generate the filters for request to youtube."""
    #  We pick the very first filter.
    for key, value in request_filter.model_dump().items():
        if value:
            if key == "id":
                value: str = ",".join(value)
            return {key: value}
    return {}


def create_request_dict(request_schema: YouTubeRequest) -> dict[str, Any]:
    """Create the request dict for sending request to youtube."""
    request_dict: dict[str, Any] = dict()
    request_dict["part"] = generate_part(request_schema.part)
    request_dict.update(
        generate_optional_parameters(request_schema.optional_parameters)
    )
    request_dict.update(generate_filter(request_schema.filter))
    return request_dict
