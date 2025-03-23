import copy
from collections.abc import Callable
from functools import partial
from typing import Any, Literal, TypeVar

from apispec_aiohttp.typedefs import HandlerType, IDataclass, SchemaType
from apispec_aiohttp.utils import get_or_set_apispec, get_or_set_schemas, resolve_schema_instance
from apispec_aiohttp.validation import ValidationSchema

# Locations supported by both openapi and webargs.aiohttpparser
ValidLocations = Literal[
    "cookies",
    "files",
    "form",
    "headers",
    "json",
    "match_info",
    "path",
    "query",
    "querystring",
]

VALID_SCHEMA_LOCATIONS = (
    "cookies",
    "files",
    "form",
    "headers",
    "json",
    "match_info",
    "path",
    "query",
    "querystring",
)

T = TypeVar("T", bound=HandlerType)
TDataclass = TypeVar("TDataclass", bound=IDataclass)


def request_schema(
    schema: SchemaType | type[TDataclass],
    location: ValidLocations = "json",
    put_into: str | None = None,
    example: dict[str, Any] | None = None,
    add_to_refs: bool = False,
    **kwargs: Any,
) -> Callable[[T], T]:
    """
    Add request info into the swagger spec and
    prepare injection keyword arguments from the specified
    webargs arguments into the decorated view function in
    request['data'] for validation_middleware validation middleware.

    Usage:

    .. code-block:: python

        from aiohttp import web
        from marshmallow import Schema, fields


        class RequestSchema(Schema):
            id = fields.Int()
            name = fields.Str(description="name")


        @request_schema(RequestSchema(strict=True))
        async def index(request):
            # apispec_aiohttp_middleware should be used for it
            data = request["data"]
            return web.json_response(
                {"name": data["name"], "id": data["id"]}
            )

    :param schema: :class:`Schema <marshmallow.Schema>` class or instance
    :param location: Default request locations to parse
    :param put_into: name of the key in Request object
                     where validated data will be placed.
                     If None (by default) default key will be used
    :param dict example: Adding example for current schema
    :param bool add_to_refs: Working only if example not None,
                             if True, add example for ref schema.
                             Otherwise, add example to endpoint.
                             Default False
    """

    if location not in VALID_SCHEMA_LOCATIONS:
        raise ValueError(f"Invalid location argument: {location}")

    schema_instance = resolve_schema_instance(schema)

    options = {"required": kwargs.pop("required", False)}

    def wrapper(func: T) -> T:
        func_apispec = get_or_set_apispec(func)
        func_schemas = get_or_set_schemas(func)

        _example = copy.copy(example) or {}
        if _example:
            _example["add_to_refs"] = add_to_refs

        func_apispec["schemas"].append(
            {
                "schema": schema_instance,
                "location": location,
                "options": options,
                "example": _example,
            }
        )

        if location in {sch.location for sch in func_schemas}:
            raise RuntimeError(f"Multiple `{location}` locations are not allowed")

        func_schemas.append(
            ValidationSchema(
                schema=schema_instance,
                location=location,
                put_into=put_into,
            )
        )

        return func

    return wrapper


# Decorators for specific request data validations (shortenings)
match_info_schema = partial(request_schema, location="match_info", put_into="match_info")
querystring_schema = partial(request_schema, location="querystring", put_into="querystring")
form_schema = partial(request_schema, location="form", put_into="form")
json_schema = partial(request_schema, location="json", put_into="json")
headers_schema = partial(request_schema, location="headers", put_into="headers")
cookies_schema = partial(request_schema, location="cookies", put_into="cookies")
