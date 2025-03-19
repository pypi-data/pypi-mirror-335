"""Module for creating OpenAI function schemas from Python functions."""

from __future__ import annotations

from collections.abc import (
    Callable,  # noqa: TC003
    Sequence,  # noqa: F401
)
import dataclasses
from datetime import date, datetime, time, timedelta, timezone
import decimal
import enum
import inspect
import ipaddress
import logging
from pathlib import Path
import re
import types
import typing
from typing import Annotated, Any, Literal, NotRequired, Required, TypeGuard
from uuid import UUID

import docstring_parser
import pydantic

from py2openai.typedefs import (
    OpenAIFunctionDefinition,
    OpenAIFunctionTool,
    Property,
    ToolParameters,
)


logger = logging.getLogger(__name__)


class FunctionType(str, enum.Enum):
    """Enum representing different function types."""

    SYNC = "sync"
    ASYNC = "async"
    SYNC_GENERATOR = "sync_generator"
    ASYNC_GENERATOR = "async_generator"


def get_param_type(param_details: Property) -> type[Any]:
    """Get the Python type for a parameter based on its schema details."""
    if "enum" in param_details:
        # For enum parameters, we just use str since we can't reconstruct
        # the exact enum class
        return str

    type_map = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return type_map.get(param_details.get("type", "string"), Any)  # type: ignore


class FunctionSchema(pydantic.BaseModel):
    """Schema representing an OpenAI function definition and metadata.

    This class encapsulates all the necessary information to describe a function to the
    OpenAI API, including its name, description, parameters, return type, and execution
    characteristics. It follows the OpenAI function calling format while adding
    additional metadata useful for Python function handling.

    The schema includes support for complex parameter types, optional values,
    and different function execution patterns (sync, async, generators).
    """

    name: str
    """The name of the function as it will be presented to the OpenAI API."""

    description: str | None = None
    """
    Optional description of what the function does. This helps the AI understand
    when and how to use the function.
    """

    parameters: ToolParameters = pydantic.Field(
        default_factory=lambda: ToolParameters(type="object", properties={}),
    )
    """
    JSON Schema object describing the function's parameters. Contains type information,
    descriptions, and constraints for each parameter.
    """

    required: list[str] = pydantic.Field(default_factory=list)
    """
    List of parameter names that are required (do not have default values).
    These parameters must be provided when calling the function.
    """

    returns: dict[str, Any] = pydantic.Field(
        default_factory=lambda: {"type": "object"},
    )
    """
    JSON Schema object describing the function's return type. Used for type checking
    and documentation purposes.
    """

    function_type: FunctionType = FunctionType.SYNC
    """
    The execution pattern of the function (sync, async, generator, or async generator).
    Used to determine how to properly invoke the function.
    """

    model_config = pydantic.ConfigDict(frozen=True)

    def _create_pydantic_model(self) -> type[pydantic.BaseModel]:
        """Create a Pydantic model from the schema parameters."""
        fields: dict[str, tuple[type[Any], pydantic.Field]] = {}  # type: ignore
        properties = self.parameters.get("properties", {})
        required = self.parameters.get("required", self.required)

        for name, details in properties.items():
            # Get base type
            if "enum" in details:
                values = tuple(details["enum"])  # type: ignore
                param_type = Literal[values]  # type: ignore
            else:
                type_map = {
                    "string": str,
                    "integer": int,
                    "number": float,
                    "boolean": bool,
                    "array": list[Any],  # type: ignore
                    "object": dict[str, Any],  # type: ignore
                }
                param_type = type_map.get(details.get("type", "string"), Any)

            # Handle optional types (if there's a default of None)
            default_value = details.get("default")
            if default_value is None and name not in required:
                param_type = param_type | None  # type: ignore

            # Create a proper pydantic Field
            field = (
                param_type,
                pydantic.Field(default=... if name in required else default_value),
            )
            fields[name] = field  # type: ignore

        return pydantic.create_model(f"{self.name}_params", **fields)  # type: ignore

    def model_dump_openai(self) -> OpenAIFunctionTool:
        """Convert the schema to OpenAI's function calling format.

        Returns:
            A dictionary matching OpenAI's complete function tool definition format.

        Example:
            ```python
            schema = FunctionSchema(
                name="get_weather",
                description="Get weather information for a location",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "unit": {"type": "string", "enum": ["C", "F"]}
                    }
                },
                required=["location"]
            )

            openai_schema = schema.model_dump_openai()
            # Result:
            # {
            #     "type": "function",
            #     "function": {
            #         "name": "get_weather",
            #         "description": "Get weather information for a location",
            #         "parameters": {
            #             "type": "object",
            #             "properties": {
            #                 "location": {"type": "string"},
            #                 "unit": {"type": "string", "enum": ["C", "F"]}
            #             },
            #             "required": ["location"]
            #         }
            #     }
            # }
            ```
        """
        parameters: ToolParameters = {
            "type": "object",
            "properties": self.parameters["properties"],
            "required": self.required,
        }

        # First create the function definition
        function_def = OpenAIFunctionDefinition(
            name=self.name,
            description=self.description or "",
            parameters=parameters,
        )

        # Then wrap it in the tool
        return OpenAIFunctionTool(
            type="function",
            function=function_def,
        )

    def to_python_signature(self) -> inspect.Signature:
        """Convert the schema back to a Python function signature.

        This method creates a Python function signature from the OpenAI schema,
        mapping JSON schema types back to their Python equivalents.

        Returns:
            A function signature representing the schema parameters

        Example:
            ```python
            schema = FunctionSchema(...)
            sig = schema.to_python_signature()
            print(str(sig))  # -> (location: str, unit: str = None, ...)
            ```
        """
        model = self._create_pydantic_model()

        # Get parameter information from the Pydantic model
        parameters: list[inspect.Parameter] = []
        for name, field in model.model_fields.items():
            param = inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=field.annotation,
                default=(
                    inspect.Parameter.empty if field.is_required() else field.default
                ),
            )
            parameters.append(param)

        return inspect.Signature(
            parameters=parameters,
            return_annotation=Any,
        )

    def get_annotations(self, return_type: Any = str) -> dict[str, type[Any]]:
        """Get a dictionary of parameter names to their Python types.

        This can be used directly for __annotations__ assignment.

        Returns:
            Dictionary mapping parameter names to their Python types.
        """
        model = self._create_pydantic_model()
        annotations: dict[str, type[Any]] = {}

        for name, field in model.model_fields.items():
            annotations[name] = field.annotation  # type: ignore

        annotations["return"] = return_type
        return annotations

    @classmethod
    def from_dict(cls, schema: dict[str, Any]) -> FunctionSchema:
        """Create a FunctionSchema from a raw schema dictionary.

        Args:
            schema: OpenAI function schema dictionary.
                Can be either a direct function definition or a tool wrapper.

        Returns:
            New FunctionSchema instance

        Raises:
            ValueError: If schema format is invalid or missing required fields
        """
        from py2openai.typedefs import _convert_complex_property

        # Handle tool wrapper format
        if isinstance(schema, dict):
            if "type" in schema and schema["type"] == "function":
                if "function" not in schema:
                    msg = 'Tool with type "function" must have a "function" field'
                    raise ValueError(msg)
                schema = schema["function"]
            elif "type" in schema and schema.get("type") != "function":
                msg = f"Unknown tool type: {schema.get('type')}"
                raise ValueError(msg)

        # Validate we have a proper function definition
        if not isinstance(schema, dict):
            msg = "Schema must be a dictionary"
            raise ValueError(msg)  # noqa: TRY004

        # Get function name
        name = schema.get("name", schema.get("function", {}).get("name"))
        if not name:
            msg = 'Schema must have a "name" field'
            raise ValueError(msg)

        # Extract parameters
        param_dict = schema.get("parameters", {"type": "object", "properties": {}})
        if not isinstance(param_dict, dict):
            msg = "Schema parameters must be a dictionary"
            raise ValueError(msg)  # noqa: TRY004

        # Clean up properties that have advanced JSON Schema features
        properties = param_dict.get("properties", {})
        cleaned_properties: dict[str, Property] = {}

        for prop_name, prop in properties.items():
            cleaned_properties[prop_name] = _convert_complex_property(prop)

        # Get required fields
        required = param_dict.get("required", [])

        # Create parameters with cleaned properties
        parameters: ToolParameters = {
            "type": "object",
            "properties": cleaned_properties,
        }
        if required:
            parameters["required"] = required

        # Create new instance
        return cls(
            name=name,
            description=schema.get("description"),
            parameters=parameters,
            required=required,
            returns={"type": "object"},
            function_type=FunctionType.SYNC,
        )


def _is_optional_type(typ: type) -> TypeGuard[type]:
    """Check if a type is Optional[T] or T | None.

    Args:
        typ: Type to check

    Returns:
        True if the type is Optional, False otherwise
    """
    origin = typing.get_origin(typ)

    # Not a Union/UnionType, can't be Optional
    if origin not in (typing.Union, types.UnionType):  # pyright: ignore
        return False

    args = typing.get_args(typ)
    # Check if any of the union members is None or NoneType
    return any(arg is type(None) for arg in args)


def _resolve_type_annotation(
    typ: Any,
    description: str | None = None,
    default: Any = inspect.Parameter.empty,
    is_parameter: bool = True,
) -> Property:
    """Resolve a type annotation into an OpenAI schema type.

    Args:
        typ: Type to resolve
        description: Optional description
        default: Default value if any
        is_parameter: Whether this is for a parameter (affects dict schema)
    """
    from py2openai.typedefs import _create_simple_property

    schema: dict[str, Any] = {}

    # Handle anyOf/oneOf fields
    if isinstance(typ, dict) and ("anyOf" in typ or "oneOf" in typ):
        # For simplicity, we'll treat it as a string that can be null
        # This is a common pattern for optional fields
        schema["type"] = "string"
        if default is not None:
            schema["default"] = default
        if description:
            schema["description"] = description
        return _create_simple_property(
            type_str="string",
            description=description,
            default=default,
        )

    # Handle Annotated types first
    if typing.get_origin(typ) is Annotated:
        # Get the underlying type (first argument)
        base_type = typing.get_args(typ)[0]
        return _resolve_type_annotation(
            base_type,
            description=description,
            default=default,
            is_parameter=is_parameter,
        )

    origin = typing.get_origin(typ)
    args = typing.get_args(typ)

    # Handle Union types (including Optional)
    if origin in (typing.Union, types.UnionType):  # pyright: ignore
        # For Optional (union with None), filter out None type
        non_none_types = [t for t in args if t is not type(None)]
        if non_none_types:
            # Use the first non-None type
            schema.update(
                _resolve_type_annotation(
                    non_none_types[0],
                    description=description,
                    default=default,
                    is_parameter=is_parameter,
                )
            )
        else:
            schema["type"] = "string"  # Fallback for Union[]

    # Handle dataclasses
    elif dataclasses.is_dataclass(typ):
        schema["type"] = "object"
    elif typing.is_typeddict(typ):
        properties = {}
        required = []
        for field_name, field_type in typ.__annotations__.items():
            # Check if field is wrapped in Required/NotRequired
            origin = typing.get_origin(field_type)
            if origin is Required:
                is_required = True
                field_type = typing.get_args(field_type)[0]
            elif origin is NotRequired:
                is_required = False
                field_type = typing.get_args(field_type)[0]
            else:
                # Fall back to checking __required_keys__
                is_required = field_name in getattr(
                    typ, "__required_keys__", {field_name}
                )

            properties[field_name] = _resolve_type_annotation(
                field_type,
                is_parameter=is_parameter,
            )
            if is_required:
                required.append(field_name)

        schema.update({
            "type": "object",
            "properties": properties,
        })
        if required:
            schema["required"] = required
    # Handle mappings - updated check
    elif (
        origin in (dict, typing.Dict)  # noqa: UP006
        or (origin is not None and isinstance(origin, type) and issubclass(origin, dict))
    ):
        schema["type"] = "object"
        if is_parameter:  # Only add additionalProperties for parameters
            schema["additionalProperties"] = True

    # Handle sequences
    elif origin in (
        list,
        set,
        tuple,
        frozenset,
        typing.List,  # noqa: UP006  # pyright: ignore
        typing.Set,  # noqa: UP006  # pyright: ignore
    ) or (
        origin is not None
        and origin.__module__ == "collections.abc"
        and origin.__name__ in {"Sequence", "MutableSequence", "Collection"}
    ):
        schema["type"] = "array"
        item_type = args[0] if args else Any
        schema["items"] = _resolve_type_annotation(
            item_type,
            is_parameter=is_parameter,
        )

    # Handle literals
    elif origin is typing.Literal:
        schema["type"] = "string"
        schema["enum"] = list(args)

    # Handle basic types
    elif isinstance(typ, type):
        if issubclass(typ, enum.Enum):
            schema["type"] = "string"
            schema["enum"] = [e.value for e in typ]

        # Basic types
        elif typ in (str, Path, UUID, re.Pattern):
            schema["type"] = "string"
        elif typ is int:
            schema["type"] = "integer"
        elif typ in (float, decimal.Decimal):
            schema["type"] = "number"
        elif typ is bool:
            schema["type"] = "boolean"

        # String formats
        elif typ is datetime:
            schema["type"] = "string"
            schema["format"] = "date-time"
            if description:
                description = f"{description} (ISO 8601 format)"
        elif typ is date:
            schema["type"] = "string"
            schema["format"] = "date"
            if description:
                description = f"{description} (ISO 8601 format)"
        elif typ is time:
            schema["type"] = "string"
            schema["format"] = "time"
            if description:
                description = f"{description} (ISO 8601 format)"
        elif typ is timedelta:
            schema["type"] = "string"
            if description:
                description = f"{description} (ISO 8601 duration)"
        elif typ is timezone:
            schema["type"] = "string"
            if description:
                description = f"{description} (IANA timezone name)"
        elif typ is UUID:
            schema["type"] = "string"
        elif typ in (bytes, bytearray):
            schema["type"] = "string"
            if description:
                description = f"{description} (base64 encoded)"
        elif typ is ipaddress.IPv4Address or typ is ipaddress.IPv6Address:
            schema["type"] = "string"
        elif typ is complex:
            schema.update({
                "type": "object",
                "properties": {
                    "real": {"type": "number"},
                    "imag": {"type": "number"},
                },
            })
        # Default to object for unknown types
        else:
            schema["type"] = "object"
    else:
        # Default for unmatched types
        schema["type"] = "string"

    # Add description if provided
    if description is not None:
        schema["description"] = description

    # Add default if provided and not empty
    if default is not inspect.Parameter.empty:
        schema["default"] = default

    from py2openai.typedefs import (
        _create_array_property,
        _create_object_property,
        _create_simple_property,
    )

    if schema["type"] == "array":
        return _create_array_property(
            items=schema["items"],
            description=schema.get("description"),
        )
    if schema["type"] == "object":
        prop = _create_object_property(description=schema.get("description"))
        if "properties" in schema:
            prop["properties"] = schema["properties"]
        if "additionalProperties" in schema:
            prop["additionalProperties"] = schema["additionalProperties"]
        if "required" in schema:
            prop["required"] = schema["required"]
        return prop

    return _create_simple_property(
        type_str=schema["type"],
        description=schema.get("description"),
        enum_values=schema.get("enum"),
        default=default if default is not inspect.Parameter.empty else None,
        fmt=schema.get("format"),
    )


def _determine_function_type(func: Callable[..., Any]) -> FunctionType:
    """Determine the type of the function.

    Args:
        func: Function to check

    Returns:
        FunctionType indicating the function's type
    """
    if inspect.isasyncgenfunction(func):
        return FunctionType.ASYNC_GENERATOR
    if inspect.isgeneratorfunction(func):
        return FunctionType.SYNC_GENERATOR
    if inspect.iscoroutinefunction(func):
        return FunctionType.ASYNC
    return FunctionType.SYNC


def create_schema(
    func: Callable[..., Any],
    name_override: str | None = None,
) -> FunctionSchema:
    """Create an OpenAI function schema from a Python function.

    Args:
        func: Function to create schema for
        name_override: Optional name override (otherwise the function name)

    Returns:
        Schema representing the function

    Raises:
        TypeError: If input is not callable

    Note:
        Variable arguments (*args) and keyword arguments (**kwargs) are not
        supported in OpenAI function schemas and will be ignored with a warning.
    """
    if not callable(func):
        msg = f"Expected callable, got {type(func)}"
        raise TypeError(msg)

    # Parse function signature and docstring
    sig = inspect.signature(func)
    docstring = docstring_parser.parse(func.__doc__ or "")

    # Get clean type hints without extras
    try:
        hints = typing.get_type_hints(func, localns=locals())
    except NameError:
        msg = "Unable to resolve type hints for function %s, skipping"
        logger.warning(msg, func.__name__)
        hints = {}

    # Process parameters
    parameters: ToolParameters = {
        "type": "object",
        "properties": {},
    }
    required: list[str] = []

    params = list(sig.parameters.items())
    skip_first = (
        inspect.isfunction(func)
        and not inspect.ismethod(func)
        and params
        and params[0][0] == "self"
    )

    for i, (name, param) in enumerate(sig.parameters.items()):
        # Skip the first parameter for bound methods
        if skip_first and i == 0:
            continue
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        param_doc = next(
            (p.description for p in docstring.params if p.arg_name == name),
            None,
        )

        param_type = hints.get(name, Any)
        parameters["properties"][name] = _resolve_type_annotation(
            param_type,
            description=param_doc,
            default=param.default,
            is_parameter=True,
        )

        if param.default is inspect.Parameter.empty:
            required.append(name)

    # Add required fields to parameters if any exist
    if required:
        parameters["required"] = required

    # Handle return type with is_parameter=False
    function_type = _determine_function_type(func)
    return_hint = hints.get("return", Any)

    if function_type in (FunctionType.SYNC_GENERATOR, FunctionType.ASYNC_GENERATOR):
        element_type = next(
            (t for t in typing.get_args(return_hint) if t is not type(None)),
            Any,
        )
        returns_dct = {
            "type": "array",
            "items": _resolve_type_annotation(element_type, is_parameter=False),
        }
    else:
        returns = _resolve_type_annotation(return_hint, is_parameter=False)
        returns_dct = dict(returns)  # type: ignore

    return FunctionSchema(
        name=name_override or func.__name__,
        description=docstring.short_description,
        parameters=parameters,  # Now includes required fields
        required=required,
        returns=returns_dct,
        function_type=function_type,
    )


if __name__ == "__main__":
    import json

    def get_weather(
        location: str,
        unit: typing.Literal["C", "F"] = "C",
        detailed: bool = False,
    ) -> dict[str, str | float]:
        """Get the weather for a location.

        Args:
            location: City or address to get weather for
            unit: Temperature unit (Celsius or Fahrenheit)
            detailed: Include extended forecast
        """
        return {"temp": 22.5, "conditions": "sunny"}

    # Create schema and executable function
    schema = create_schema(get_weather)

    # Print the schema
    print("OpenAI Function Schema:")
    print(json.dumps(schema.model_dump_openai(), indent=2))
