# A Genric Transformation Function to transform JSON from format X to format Y.
# This is auto-generated code using LLM (Large Language Model) and Assistant Tool.
# As a part of ETL we dont need to write custom code for each transformation.
# Auto-generated code is used to transform JSON from format X to format Y.

import asyncio
import json
from pydantic import BaseModel
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.dataframe_tools import get_structured_output
from pydantic import BaseModel
from typing import Type

GLOBAL_GENERATED_PYTHON_CODE = {}

class GeneratedPythonCode(BaseModel):
    python_code: str

@assistant_tool
async def transform_json_code(input_json: str, output_json: str, function_name: str) -> str:
    """
    Use LLM to generate python code to transform JSON from format X to format Y.
    Save that to a GLOBAL variable.

    Args:
        input_json (str): Example input JSON.
        output_json (str): Example output JSON.
        function_name (str): The generated python function should be saved as.

    Returns:
        str: Function name that was saved to the global scope.
    """
    max_retries = 3
    error_message = ""

    for attempt in range(max_retries):
        # Prepare the message
        message = f"""
        Given the following input and output JSON schemas, generate a Python function that transforms the input JSON to the output JSON.
        Example Input JSON:
        {input_json}
        Example Output JSON:
        {output_json}
        Name the function as:
        {function_name}
        Check for NoneType in code before any concatination and make sure error does not happen lie "unsupported operand type(s) for +: 'NoneType' and 'str'"
        Preserve the output type to be of the type in output JSON. Convert input field to string and assign to output field if types dont match.
        Return the function code in 'python_code'. Do not include any imports or explanations; only provide the '{function_name}' code that takes 'input_json' as input and returns the transformed 'output_json' as output.
        """
        if error_message:
            message += f"\nThe previous attempt returned the following error:\n{error_message}\nPlease fix the function."

        # Get structured output
        generated_python_code, status = await get_structured_output(message, GeneratedPythonCode)
        if status == 'SUCCESS' and generated_python_code and generated_python_code.python_code:
            function_string = generated_python_code.python_code
            # Execute the generated function
            try:
                exec(function_string, globals())
                # Test the function
                input_data = json.loads(input_json)
                output_data = globals()[function_name](input_data)
                if output_data:
                    # Store the function code
                    GLOBAL_GENERATED_PYTHON_CODE[function_name] = globals()[function_name]
                    return function_name
                else:
                    error_message = "The function did not produce the expected output."
            except Exception as e:
                error_message = str(e)
        else:
            error_message = "Failed to generate valid Python code."
        if attempt == max_retries - 1:
            raise RuntimeError(f"Error executing generated function after {max_retries} attempts: {error_message}")


@assistant_tool
async def transform_json_with_type(input_json_str: str, response_type: Type[BaseModel], function_name: str):
    """
    Transforms the input JSON into the format specified by the given Pydantic response type.

    Args:
        input_json_str (str): The input JSON string to be transformed.
        response_type (Type[BaseModel]): The Pydantic model defining the desired output format.
        function_name (str): The name of the function to generate and execute.

    Returns:
        The transformed JSON string matching the response_type format.
    """
    # Create a sample instance of the Pydantic model
    sample_instance = response_type.construct()
    # Convert the instance to JSON
    response_type_json_str = sample_instance.json()
    return await transform_json_code(input_json_str, response_type_json_str, function_name)