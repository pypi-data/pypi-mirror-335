import json
import logging
import re
import traceback
from typing import Optional, List, Any, Dict

from fastapi import HTTPException
from pydantic import BaseModel
import openai
from dhisana.utils.openai_helpers import get_openai_access_token


# -----------------------------------------------------------------------------
# Vector Store Helpers
# -----------------------------------------------------------------------------

async def create_vector_store(
    vector_store_name: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Create a new vector store with a cleaned name. Returns the vector store details.
    """
    normalized_name = vector_store_name.lower()
    normalized_name = re.sub(r'[^a-z0-9_]+', '_', normalized_name)
    normalized_name = normalized_name[:64]
    openai_key = get_openai_access_token(tool_config)

    client = openai.OpenAI(api_key=openai_key)
    try:
        vector_store = client.vector_stores.create(name=normalized_name)
        return {
            "id": vector_store.id,
            "name": vector_store.name,
            "created_at": vector_store.created_at,
            "file_count": vector_store.file_counts.completed
        }
    except Exception as e:
        logging.error(f"Error creating vector store: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


async def delete_vector_store(
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None
) -> None:
    """
    Delete a vector store by ID.
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)
    try:
        client.vector_stores.delete(vector_store_id=vector_store_id)
    except Exception as e:
        logging.error(f"Error deleting vector store {vector_store_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------------------------------
# File Upload Helpers
# -----------------------------------------------------------------------------

async def upload_file_openai_and_vector_store(
    file_path_or_bytes: Any,
    file_name: str,
    mime_type: str,
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None
):
    """
    Upload a local file or bytes to OpenAI, then attach to a vector store.
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)
    purpose = "assistants"
    if mime_type in ["image/jpeg", "image/png"]:
        purpose = "vision"

    try:
        # file=(filename, file_content, mime_type) if bytes
        # or file=open(file_path, "rb") if local path
        file_upload = None
        if isinstance(file_path_or_bytes, (str, bytes)):
            # If string path, open as binary
            if isinstance(file_path_or_bytes, str):
                file_upload = client.files.create(
                    file=open(file_path_or_bytes, "rb"),
                    purpose=purpose
                )
            else:
                # raw bytes
                file_upload = client.files.create(
                    file=(file_name, file_path_or_bytes, mime_type),
                    purpose=purpose
                )
        else:
            raise ValueError("Unknown file content type. Must be path or bytes.")

        if purpose == "assistants" and vector_store_id:
            client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_upload.id
            )
        return file_upload
    except Exception as e:
        logging.error(f"Error uploading file {file_name}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


async def upload_file_openai(
    file_path_or_bytes: Any,
    file_name: str,
    mime_type: str,
    tool_config: Optional[List[Dict]] = None
):
    """
    Upload a file to OpenAI (not attached to a vector store).
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)

    purpose = "assistants"
    if mime_type in ["image/jpeg", "image/png"]:
        purpose = "vision"

    try:
        if isinstance(file_path_or_bytes, str):
            # treat as local path
            file_upload = client.files.create(
                file=open(file_path_or_bytes, "rb"),
                purpose=purpose
            )
        else:
            file_upload = client.files.create(
                file=(file_name, file_path_or_bytes, mime_type),
                purpose=purpose
            )
        return file_upload
    except Exception as e:
        logging.error(f"Error uploading file {file_name}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


async def attach_file_to_vector_store(
    file_id: str,
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None
):
    """
    Attach an already uploaded file to a vector store.
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)
    try:
        response = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        return response
    except Exception as e:
        logging.error(f"Error attaching file {file_id} to vector store {vector_store_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def delete_files(
    file_ids: List[str],
    vector_store_id: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Delete files from the vector store and from OpenAI's file storage.
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)
    for file_id in file_ids:
        try:
            if vector_store_id:
                client.vector_stores.files.delete(vector_store_id=vector_store_id, file_id=file_id)
            client.files.delete(file_id=file_id)
        except openai.NotFoundError:
            logging.warning(f"File not found: {file_id}")
        except Exception as e:
            logging.error(f"Error deleting file {file_id}: {e}\n{traceback.format_exc()}")


# -----------------------------------------------------------------------------
# Using File Search (RAG) with the Responses API
# -----------------------------------------------------------------------------

async def run_file_search(
    query: str,
    vector_store_id: str,
    model: str = "gpt-4o-mini",
    max_num_results: int = 5,
    store: bool = True,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Execute a single call to the new OpenAI Responses API, using the file_search tool.
    - 'query': user question
    - 'vector_store_id': the store where the PDFs are embedded
    - 'model': which model to use for generating the final answer
    - 'max_num_results': how many relevant chunks to retrieve
    - 'store': whether to store the response on the OpenAI side
    Returns a dict with:
      {
        "answer": str,            # the text answer from the LLM
        "retrieved_files": list,  # the top-k filenames used
        "annotations": list       # any chunk-level annotations
      }
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)

    try:
        response = client.responses.create(
            input=query,
            model=model,
            store=store,
            # Provide the file_search tool with vector_store_ids
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
                "max_num_results": max_num_results,
            }]
        )

        # By default, the file_search call is placed into output[1].
        # The first chunk in output[1].content can contain both text and annotations.
        if len(response.output) > 1 and response.output[1].content:
            # The text & annotations from the file_search step:
            fs_content = response.output[1].content[0]
            answer_text = fs_content.text
            annotations = fs_content.annotations  # chunk-level info (filename, snippet, etc.)

            retrieved_files = []
            if annotations:
                retrieved_files = list({result.filename for result in annotations})

            return {
                "answer": answer_text,
                "retrieved_files": retrieved_files,
                "annotations": annotations
            }
        else:
            # If for some reason no file_search step was generated:
            return {
                "answer": response.output_text,  # fallback
                "retrieved_files": [],
                "annotations": []
            }
    except Exception as e:
        logging.error(f"Error in run_file_search: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------------------------------
# Additional “Responses” Helpers (e.g., run_response_text, run_response_structured)
# -----------------------------------------------------------------------------

async def run_response_text(
    prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 2048,
    store: bool = True,
    tool_config: Optional[List[Dict]] = None
) -> (str, str):
    """
    Simple text completion with the new Responses API.
    Returns (answer, status).
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)

    try:
        response = client.responses.create(
            input=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            store=store
        )
        return response.output_text, "success"
    except Exception as e:
        logging.error(f"Error in run_response_text: {e}\n{traceback.format_exc()}")
        return (f"An error occurred: {e}", "error")


async def run_response_structured(
    prompt: str,
    response_format: dict,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1024,
    store: bool = True,
    tool_config: Optional[List[Dict]] = None
) -> (Any, str):
    """
    Structured output example. Provide a JSON schema or other format in text={"format": ...}.
    """
    openai_key = get_openai_access_token(tool_config)
    client = openai.OpenAI(api_key=openai_key)

    try:
        response = client.responses.create(
            input=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            store=store,
            text={"format": response_format}
        )
        # If we assume the JSON is in the first output chunk’s .text
        if response.output and len(response.output) > 0:
            raw_text = response.output[0].content[0].text
            try:
                parsed = json.loads(raw_text)
                return parsed, "success"
            except json.JSONDecodeError:
                # Possibly the model returned partial or invalid JSON
                return raw_text, "error"
        else:
            return "No output returned", "error"
    except Exception as e:
        logging.error(f"Error in run_response_structured: {e}\n{traceback.format_exc()}")
        return f"An error occurred: {e}", "error"
