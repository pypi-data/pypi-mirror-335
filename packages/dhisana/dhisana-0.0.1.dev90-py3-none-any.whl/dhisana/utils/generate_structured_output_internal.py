import asyncio
import hashlib
import json
import os
import re
import time
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from pydantic import BaseModel, TypeAdapter

import openai
from dhisana.utils import cache_output_tools
from dhisana.utils.openai_helpers import get_openai_access_token


# --------------------------------------------------------------------------
# Utility: retrieve Vector Store and list its files (unchanged)
# --------------------------------------------------------------------------

async def get_vector_store_object(
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict:
    openai_key = get_openai_access_token(tool_config)
    client_async = openai.AsyncOpenAI(api_key=openai_key)
    return await client_async.vector_stores.retrieve(vector_store_id=vector_store_id)


async def list_vector_store_files(
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None
) -> List:
    openai_key = get_openai_access_token(tool_config)
    client_async = openai.AsyncOpenAI(api_key=openai_key)
    page = await client_async.vector_stores.files.list(vector_store_id=vector_store_id)
    return page.data


# --------------------------------------------------------------------------
# get_structured_output_internal:
# Updated to include search for first output with .type == 'message'
# --------------------------------------------------------------------------

async def get_structured_output_internal(
    prompt: str,
    response_format: BaseModel,
    effort: str = "low",
    use_web_search: bool = False,
    model="o3-mini",
    tool_config: Optional[List[Dict]] = None
):
    """
    Makes a direct call to the new Responses API for structured output,
    bypassing file_search. No vector store usage, no chain-of-thought.
    """
    try:
        # For caching
        response_type_str = response_format.__name__
        message_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        response_type_hash = hashlib.md5(response_type_str.encode('utf-8')).hexdigest()
        cache_key = f"{message_hash}:{response_type_hash}"
        cached_response = cache_output_tools.retrieve_output(
            "get_structured_output_internal",
            cache_key
        )
        if cached_response is not None:
            parsed_cached_response = response_format.parse_raw(cached_response)
            return parsed_cached_response, "SUCCESS"

        schema = response_format.model_json_schema()
        schema["additionalProperties"] = False
        schema["title"] = response_type_str

        json_schema_format = {
            "name": response_type_str,
            "type": "json_schema",
            "schema": schema
        }

        openai_key = get_openai_access_token(tool_config)
        client_async = openai.AsyncOpenAI(api_key=openai_key)

        # Use web_search only if explicitly specified AND model starts with 'gpt-'
        if use_web_search and model.startswith("gpt-"):
            completion = await client_async.responses.create(
                input=[
                    {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                text={"format": json_schema_format},
                tool_choice="required",
                tools=[{"type": "web_search_preview"}],
                store=False,
            )
        else:
            # Only set reasoning if model starts with 'o'
            if model.startswith("o"):
                completion = await client_async.responses.create(
                    input=[
                        {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    reasoning={"effort": effort},
                    text={"format": json_schema_format},
                    store=False,
                )
            else:
                completion = await client_async.responses.create(
                    input=[
                        {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    text={"format": json_schema_format},
                    store=False,
                )

        if completion.output and len(completion.output) > 0:
            raw_text = None
            # Find the first output whose type is 'message'
            for out in completion.output:
                if out.type == 'message' and out.content and len(out.content) > 0:
                    raw_text = out.content[0].text
                    break

            if not raw_text or not raw_text.strip():
                return "No text returned", "FAIL"

            try:
                parsed_obj = response_format.parse_raw(raw_text)
                # Cache the successful result
                cache_output_tools.cache_output(
                    "get_structured_output_internal",
                    cache_key,
                    parsed_obj.json()
                )
                return parsed_obj, "SUCCESS"
            except json.JSONDecodeError:
                logging.warning("ERROR: Could not parse JSON from model output.")
                return raw_text, "FAIL"
        else:
            return "No output returned", "FAIL"

    except openai.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=502,
            detail="Error communicating with the OpenAI API."
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request."
        )


# --------------------------------------------------------------------------
# get_structured_output_with_assistant_and_vector_store:
# Similarly updated to provide search for first output .type == 'message'
# --------------------------------------------------------------------------

async def get_structured_output_with_assistant_and_vector_store(
    prompt: str,
    response_format: BaseModel,
    vector_store_id: str,
    effort: str = "low",
    tool_config: Optional[List[Dict]] = None
):
    """
    If the vector store has NO files, call get_structured_output_internal directly.
    Otherwise, do a single call to the new Responses API with a 'file_search' tool
    to incorporate vector-store knowledge.
    """
    try:
        # 1. Ensure vector store exists
        await get_vector_store_object(vector_store_id, tool_config)

        # 2. Check if the vector store contains any files
        files = await list_vector_store_files(vector_store_id, tool_config)
        if not files:
            # No files => just do the internal structured approach
            return await get_structured_output_internal(prompt, response_format, tool_config=tool_config)

        # 3. If files exist => do a single "Responses" call with file_search
        response_type_str = response_format.__name__
        message_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        response_type_hash = hashlib.md5(response_type_str.encode('utf-8')).hexdigest()
        cache_key = f"{message_hash}:{response_type_hash}"
        cached_response = cache_output_tools.retrieve_output(
            "get_structured_output_with_assistant_and_vector_store",
            cache_key
        )
        if cached_response is not None:
            parsed_cached_response = response_format.parse_raw(cached_response)
            return parsed_cached_response, "SUCCESS"
        
        schema = response_format.model_json_schema()
        schema["additionalProperties"] = False
        schema["title"] = response_type_str

        json_schema_format = {
            "name": response_type_str,
            "type": "json_schema",
            "schema": schema
        }

        openai_key = get_openai_access_token(tool_config)
        client_async = openai.AsyncOpenAI(api_key=openai_key)

        # Single call to the new Responses API
        completion = await client_async.responses.create(
            input=[
                {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            model="o3-mini",
            text={"format": json_schema_format},
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
            }],
            reasoning={"effort": effort},
            tool_choice="required",
            store=False
        )

        if completion.output and len(completion.output) > 0:
            raw_text = None
            # Find the first output whose type is 'message'
            for out in completion.output:
                if out.type == 'message' and out.content and len(out.content) > 0:
                    raw_text = out.content[0].text
                    break

            if not raw_text or not raw_text.strip():
                logging.error("No response text from the model.")
                raise HTTPException(status_code=502, detail="No response from the model.")

            try:
                parsed_obj = response_format.parse_raw(raw_text)
                cache_output_tools.cache_output(
                    "get_structured_output_with_assistant_and_vector_store",
                    cache_key,
                    parsed_obj.json()
                )
                return parsed_obj, "SUCCESS"
            except json.JSONDecodeError:
                logging.warning("ERROR: Model returned invalid JSON.")
                return raw_text, "FAIL"
        else:
            return "No output returned", "FAIL"

    except openai.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=502,
            detail="Error communicating with the OpenAI API."
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request."
        )
