from typing import Any, Dict, Optional, Union, List, Tuple, get_origin, get_args
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, create_model
import aiohttp
import asyncio
import sys
import os
import json

# Create an MCP server
mcp = FastMCP("mcp-superiorapis")

# Get credentials from environment variables
TOKEN = os.getenv("TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")

# Check if required environment variables are set
if not TOKEN:
    sys.exit("❌ Error: Environment variable 'TOKEN' is not set. Please set this variable before running the program.")

if not APPLICATION_ID:
    sys.exit("❌ Error: Environment variable 'APPLICATION_ID' is not set. Please set this variable before running the program.")
# API endpoint and headers
API_ENDPOINT = "https://superiorapis-creator.cteam.com.tw/manager/module/plugins/list_v2"
HEADERS = {
    "token": f"{TOKEN}"
}
PARAMS = {
    "application_id": f"{APPLICATION_ID}"
}
print(API_ENDPOINT)
print(HEADERS)
print(PARAMS)

def map_openapi_type_str(openapi_type: str) -> str:
    """
    Maps OpenAPI types to Python type strings.
    
    Args:
        openapi_type: OpenAPI type string
        
    Returns:
        Corresponding Python type string
    """
    mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict"
    }
    return mapping.get(openapi_type, "Any")


def get_annotation_type_str(annotation):
    """
    Gets the type string from a type annotation, handling Optional types.
    
    Args:
        annotation: Type annotation
        
    Returns:
        Type name as string
    """
    # Get inner type from Optional
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        # Filter out None
        non_none_types = [a for a in args if a is not type(None)]
        if non_none_types:
            return non_none_types[0].__name__
    try:
        return annotation.__name__
    except AttributeError:
        return 'Any'


def generate_flat_param(prop_name: str, prop_info: dict) -> str:
    """
    Generates a flat parameter definition string.
    
    Args:
        prop_name: Property name
        prop_info: Property info dictionary
        
    Returns:
        Parameter definition string
    """
    python_type = map_openapi_type_str(prop_info.get("type", "Any"))
    return f"{prop_name.replace('-', '_')}: Optional[{python_type}] = None"


def should_flatten(prop_info: dict) -> bool:
    """
    Determines if a property should be flattened.
    
    Args:
        prop_info: Property info dictionary
        
    Returns:
        True if property should be flattened, False otherwise
    """
    prop_type = prop_info.get("type", "object")
    if prop_type == "object" and "properties" in prop_info:
        return False
    if prop_type == "array" and prop_info.get("items", {}).get("type") == "object":
        return False
    return True


def generate_pydantic_sub_model(schema: dict, model_name: str) -> Tuple[BaseModel, Dict[str, BaseModel]]:
    """
    Recursively generates Pydantic models from a schema.
    
    Args:
        schema: OpenAPI schema
        model_name: Name for the model
        
    Returns:
        Tuple of (model, sub_models dictionary)
    """
    fields = {}
    sub_models = {}

    for prop, prop_info in schema.get('properties', {}).items():
        prop_type = prop_info.get('type', 'Any')

        if prop_type == 'object' and 'properties' in prop_info:
            sub_model_name = f"{model_name}_{prop.capitalize()}"
            sub_model, sub_def = generate_pydantic_sub_model(prop_info, sub_model_name)
            fields[prop] = (Optional[sub_model], None)
            sub_models.update(sub_def)

        elif prop_type == 'array' and prop_info.get('items', {}).get('type') == 'object':
            sub_model_name = f"{model_name}_{prop.capitalize()}Item"
            sub_model, sub_def = generate_pydantic_sub_model(prop_info['items'], sub_model_name)
            fields[prop] = (Optional[List[sub_model]], None)
            sub_models.update(sub_def)

        else:
            py_type = map_openapi_type_str(prop_type)
            fields[prop] = (Optional[eval(py_type)], None)

    model = create_model(model_name, **fields)
    sub_models[model_name] = model
    return model, sub_models


def generate_async_function(schema: Dict[str, Any], function_name: str) -> str:
    """
    Generates an async function from an OpenAPI schema.
    
    Args:
        schema: OpenAPI schema
        function_name: Name for the function
        
    Returns:
        Function definition as string
    """
    properties = schema.get("properties", {})
    flat_params = []
    nested_models = {}
    nested_param_lines = []

    for prop_name, prop_info in properties.items():
        if should_flatten(prop_info):
            flat_params.append(generate_flat_param(prop_name, prop_info))
        else:
            sub_model, sub_def = generate_pydantic_sub_model(prop_info, f"{function_name}_{prop_name.capitalize()}")
            nested_models.update(sub_def)
            nested_param_lines.append(f"{prop_name}: Optional[{sub_model.__name__}] = None")

    # Combine function parameters
    all_params = flat_params + nested_param_lines
    param_str = ",\n    ".join(all_params)

    # Combine nested class content
    nested_code = "\n\n".join([sub.__name__ + "(BaseModel):\n    " +
                               "\n    ".join([f"{name}: Optional[{getattr(field.outer_type_, '__name__', 'Any')}] = None"
                                             for name, field in sub.model_fields.items()])
                               for sub in nested_models.values()])
    
    # This function is incomplete in the original code


def openapi_to_docstring_args(properties: dict, indent: int = 1, required_list=None) -> str:
    """
    Converts OpenAPI properties to docstring args format.
    
    Args:
        properties: OpenAPI properties
        indent: Indentation level
        required_list: List of required properties
        
    Returns:
        Formatted docstring for arguments
    """
    if required_list is None:
        required_list = []
    required_list = [str(r) for r in required_list]  # Convert to string type

    doc = ""
    space = "    " * indent
    for prop, detail in properties.items():
        prop_safe = prop.replace('-', '_')
        if not isinstance(detail, dict):
            doc += f"{space}{prop_safe} (unknown): Invalid OpenAPI schema format\n"
            continue

        prop_type = detail.get("type", "Any")
        description = detail.get("description", "")
        alias = detail.get("alias")
        if alias:
            description = f"{alias} - {description}"

        # Handle enum descriptions
        enum_desc = ""
        if "enum" in detail:
            enum_data = detail["enum"]
            if isinstance(enum_data, dict):
                enum_str = ', '.join([f'"{k}": "{v}"' for k, v in enum_data.items()])
            elif isinstance(enum_data, list):
                enum_str = ', '.join([f'"{str(e)}"' for e in enum_data])
            else:
                enum_str = f'"{str(enum_data)}"'
            enum_desc = f' | Enum: (Key: Value 預設請使用 Value) -> {{{enum_str}}}'

        # Add required hint
        required_hint = "required" if prop in required_list else "optional"

        if prop_type == "object" and "properties" in detail:
            doc += f"{space}{prop_safe} (dict, {required_hint}): {description}{enum_desc}\n"
            doc += f"{space}    Contains:\n"
            doc += openapi_to_docstring_args(detail["properties"], indent + 2, detail.get("required", []))

        elif prop_type == "array":
            items = detail.get("items", {})
            item_type = items.get("type", "Any")

            # Handle enum for array items
            item_enum_desc = ""
            if "enum" in items:
                item_enum = items["enum"]
                if isinstance(item_enum, dict):
                    item_enum_str = ', '.join([f"{k}: {v}" for k, v in item_enum.items()])
                elif isinstance(item_enum, list):
                    item_enum_str = ', '.join([str(e) for e in item_enum])
                else:
                    item_enum_str = str(item_enum)
                item_enum_desc = f" | Enum: {item_enum_str}"

            if item_type == "object" and "properties" in items:
                doc += f"{space}{prop_safe} (list[dict], {required_hint}: {description}{enum_desc}{item_enum_desc}\n"
                doc += f"{space}    Each item contains:\n"
                doc += openapi_to_docstring_args(items.get("properties", {}), indent + 2, items.get("required", []))
            else:
                doc += f"{space}{prop_safe} (list[{item_type}]){required_hint}: {description}{enum_desc}{item_enum_desc}\n"

        else:
            doc += f"{space}{prop_safe} ({prop_type}, {required_hint}): {description}{enum_desc}\n"

    return doc


def openapi_to_docstring_returns(responses: dict, indent: int = 1) -> str:
    """
    Converts OpenAPI responses to docstring returns format.
    
    Args:
        responses: OpenAPI responses
        indent: Indentation level
        
    Returns:
        Formatted docstring for return values
    """
    def parse_properties(properties, indent, required_list):
        """
        Helper function to recursively parse properties.
        
        Args:
            properties: Properties to parse
            indent: Indentation level
            required_list: List of required properties
            
        Returns:
            Formatted properties string
        """
        doc = ""
        space = "    " * indent
        # Convert required_list to strings
        required_list = [str(r) for r in required_list] if isinstance(required_list, list) else []

        for prop, detail in properties.items():
            prop_safe = prop.replace('-', '_')
            if not isinstance(detail, dict):
                doc += f"{space}{prop_safe} (unknown): Invalid schema\n"
                continue

            prop_type = detail.get("type", "Any")
            description = detail.get("description", "")
            alias = detail.get("alias")
            if alias:
                description = f"{alias} - {description}"

            # Add required/optional hint
            required_hint = "required" if prop in required_list else "optional"

            if prop_type == "object" and "properties" in detail:
                doc += f"{space}{prop_safe} (dict, {required_hint}: {description}\n"
                doc += f"{space}    Contains:\n"
                doc += parse_properties(detail["properties"], indent + 2, detail.get("required", []))
            elif prop_type == "array":
                items = detail.get("items", {})
                item_type = items.get("type", "Any")
                if item_type == "object":
                    doc += f"{space}{prop_safe} (list[dict], {required_hint}: {description}\n"
                    doc += f"{space}    Each item contains:\n"
                    doc += parse_properties(items.get("properties", {}), indent + 2, items.get("required", []))
                else:
                    doc += f"{space}{prop_safe} (list[{item_type}]){required_hint}: {description}\n"
            else:
                doc += f"{space}{prop_safe} ({prop_type}, {required_hint}): {description}\n"
        return doc

    doc = ""
    space = "    " * indent
    for status_code, response in responses.items():
        desc = response.get("description", "")
        schema = response.get("content", {}).get("application/json", {}).get("schema", {})
        if not schema:
            doc += f"{space}{status_code} (object): {desc}\n"
            continue

        desc_text = schema.get("description", "")
        if desc_text:
            desc = f"{desc} - {desc_text}"

        doc += f"{space}{status_code} (object): {desc}\n"
        if "properties" in schema:
            doc += f"{space}    Contains:\n"
            doc += parse_properties(schema["properties"], indent + 2, schema.get("required", []))
    return doc


async def fetch_data():
    """
    Fetches API data asynchronously.
    
    Returns:
        API response data or None if request fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_ENDPOINT, headers=HEADERS, json=PARAMS) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"API request failed with status: {response.status}")
                    return None
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None


# Main function to generate tool functions
def generate_tool_functions(data):
    """
    Generates MCP tool functions from API data.
    
    Args:
        data: API data containing plugin information
        
    Returns:
        Generated code as string
    """
    func_template = ""

    for tool in data['plugins']:
        plugin = tool['plugin']
        plugin_name = plugin['name_for_model'].replace('-', '_')
        plugin_description = plugin['description_for_model']
        plugin_id = plugin['id']
        paths = plugin['interface']['paths']

        for path, path_info in paths.items():
            for method, meta in path_info.items():
                func_name = f"{method}_{plugin_name}".lower()
                class_name = ""
                payload = "" if method == "get" else ", json=payload"
                param_str = ""
                nested_code = ""
                pydantic_args = ""
                pydantic_returns = ""
                flat_params = []
                nested_models = {}
                nested_param_lines = []
                
                if 'requestBody' in meta:
                    model_name = ''.join(word.title() for word in plugin_name.split('_')) + "Params"
                    class_name = f"params: {model_name}"
                    pydantic_args = openapi_to_docstring_args(
                        meta['requestBody']['content']['application/json']['schema']['properties'], 
                        2
                    )
                    pydantic_returns = openapi_to_docstring_returns(meta['responses'], 2)
                    
                    for prop_name, prop_info in meta['requestBody']['content']['application/json']['schema']['properties'].items():
                        if should_flatten(prop_info):
                            flat_params.append(generate_flat_param(prop_name, prop_info))
                        else:
                            # Generate nested models
                            sub_model, sub_def = generate_pydantic_sub_model(
                                prop_info, 
                                f"{func_name}_{prop_name.capitalize()}"
                            )
                            nested_models.update(sub_def)
                            nested_param_lines.append(f"{prop_name}: Optional[{sub_model.__name__}] = None")
                    
                    all_params = flat_params + nested_param_lines
                    param_str = ",\n    ".join(all_params)

                    # Generate nested model definitions
                    nested_code = "\n\n".join([
                        f"class {sub.__name__}(BaseModel):\n" +
                        "\n".join([
                            f"    {name.replace('-', '_')}: Optional[{get_annotation_type_str(field.annotation)}] = None"
                            for name, field in sub.model_fields.items()
                        ])
                        for sub in nested_models.values()
                    ])
                
                # Generate the function template
                func_template += f"""
{nested_code}            
@mcp.tool()
async def {func_name}({param_str}) -> str:
    \"\"\"{plugin_description +' | '+meta['summary']+'.'}

    #Args:
{pydantic_args}
    #Returns:
{pydantic_returns}
    \"\"\"  
    api_endpoint = "https://superiorapis-creator.cteam.com.tw{path}"
    headers = {{"token": "{TOKEN}"}}

    try:
        payload = {{}}
        # Iterate over all local variables to build the request payload
        for k, v in locals().items():
            # Skip specific variables not intended for the payload
            if k in ('session', 'api_endpoint', 'headers', 'method', 'payload'):
                continue
            # Skip None values
            if v is None:
                continue
            # If the value is a Pydantic model, serialize it excluding None fields
            if isinstance(v, BaseModel):
                payload[k] = v.model_dump(exclude_none=True)  # Pydantic v2: serialize the model, excluding fields with None values
            else:
                payload[k] = v
        # Send the API request
        async with aiohttp.ClientSession() as session:
            async with session.{method}(api_endpoint, headers=headers, json=payload) as response:
                result = await response.json()
                if response.status == 200:
                    return json.dumps(result, ensure_ascii=False)
                return json.dumps({{"error": f"API failed with status code: {{response.status}}"}}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({{"error": f"API request error: {{str(e)}}"}}, ensure_ascii=False)
"""
    return func_template

async def main():
    # Fetch API data
    data = await fetch_data()
    if not data or data.get('status') == 0:
        sys.exit("❌ Error: API returned no data or status is 0. Please check if the API is working properly.")
    
    # Generate tool functions dynamically from API data
    func_template = generate_tool_functions(data)
    exec(func_template)
    
    # Start the MCP server
    mcp.run()