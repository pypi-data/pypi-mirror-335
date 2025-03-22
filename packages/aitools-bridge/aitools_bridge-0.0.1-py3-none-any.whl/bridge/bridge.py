import contextlib
import inspect
import jsonref
import logging
import re
from griffe import Docstring, DocstringStyle, DocstringSectionKind
from pydantic import BaseModel, create_model, Field
from pydantic.json_schema import GenerateJsonSchema
from typing import Callable, Dict, List, Optional


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict
    strict: bool = True
    additionalProperties: bool = False


class ToolDefinition(BaseModel):
    type: str = "function"
    function: FunctionDefinition


class CustomSchemaGenerator(GenerateJsonSchema):
    def generate(self, schema, mode):
        def rm_title(s):
            if isinstance(s, dict):
                s.pop("title", None)
                for v in s.values():
                    rm_title(v)
            elif isinstance(s, list):
                for i in s:
                    rm_title(i)

        schema = super().generate(schema)
        rm_title(schema)
        return jsonref.replace_refs(schema, merge_props=True)


def detect_docstring_style(doc: str) -> DocstringStyle:
    weight: dict[DocstringStyle, int] = {"google": 0, "sphinx": 0, "numpy": 0}

    google_patterns = r"^(Args|Arguments|Returns|Raises):"
    weight["google"] = len(set(re.findall(google_patterns, doc, re.MULTILINE)))

    sphinx_patterns = r"^:(param\s|type\s|return:|rtype:)"
    weight["sphinx"] = len(set(re.findall(sphinx_patterns, doc, re.MULTILINE)))

    numpy_patterns = r"^(Parameters|Returns|Examples)\s*\n\s*-{3,}"
    weight["numpy"] = len(set(re.findall(numpy_patterns, doc, re.MULTILINE)))

    style = max(weight, key=weight.get)
    if weight[style] == 0:
        style = "google"
    return style


@contextlib.contextmanager
def suppress_log():
    logger = logging.getLogger("griffe")
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    try:
        yield
    finally:
        logger.setLevel(previous_level)


class ToolsBridge:
    _registry: Dict[str, ToolDefinition] = {}

    @classmethod
    def register(
        cls,
        description: Optional[str] = None,
        param_descriptions: Optional[Dict[str, str]] = None,
    ):
        def decorator(func: Callable):
            nonlocal description
            tool_name = func.__name__
            tool_description = description or ""

            _param_descriptions = {}
            doc = inspect.getdoc(func)
            if doc is not None:
                with suppress_log():
                    docstring = Docstring(doc, parser=detect_docstring_style(doc))
                    parsed = docstring.parse()

                for section in parsed:
                    if (
                        section.kind == DocstringSectionKind.text
                        and tool_description == ""
                    ):
                        tool_description = section.value
                    if section.kind == DocstringSectionKind.parameters:
                        for param in section.value:
                            _param_descriptions[param.name] = param.description
            sig = inspect.signature(func)

            fields = {}
            for param in sig.parameters.values():
                if param.name in ["self", "cls"]:
                    continue

                py_type = (
                    param.annotation
                    if param.annotation != inspect.Parameter.empty
                    else object
                )

                param_desc = _param_descriptions.get(param.name, "")
                field_info = {
                    "default": ...
                    if param.default == inspect.Parameter.empty
                    else param.default,
                    "description": param_descriptions.get(param.name, param_desc)
                    if param_descriptions
                    else param_desc,
                }
                fields[param.name] = (py_type, Field(**field_info))

            param_model = create_model(f"{tool_name}Params", **fields)
            schema = param_model.model_json_schema(
                schema_generator=CustomSchemaGenerator
            )
            parameters = {}
            params_properties = schema["properties"]
            if params_properties != {}:
                parameters["properties"] = params_properties
                parameters["type"] = "object"

            params_required = schema.get("required", None)
            if params_required is not None:
                parameters["required"] = params_required

            tool_def = ToolDefinition(
                function=FunctionDefinition(
                    name=tool_name, description=tool_description, parameters=parameters
                )
            )

            cls._registry[tool_name] = tool_def
            return func

        return decorator

    @classmethod
    def get_tools(cls) -> List[dict]:
        return [tool.model_dump() for tool in cls._registry.values()]

    @classmethod
    def get_tool(cls, tool_name: str) -> dict:
        if tool_name in cls._registry:
            return cls._registry[tool_name].model_dump()
        return {}
