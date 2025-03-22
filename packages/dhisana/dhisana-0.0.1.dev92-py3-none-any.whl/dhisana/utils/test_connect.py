import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional

import aiohttp
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

###############################################################################
#                             HELPER FUNCTIONS
###############################################################################

async def safe_json(response: aiohttp.ClientResponse) -> Any:
    """
    Safely parse JSON from an aiohttp response.
    Returns None if parsing fails.
    """
    try:
        return await response.json()
    except Exception:
        return None

###############################################################################
#                         TOOL TEST FUNCTIONS
###############################################################################

async def test_zerobounce(api_key: str) -> Dict[str, Any]:
    url = f"https://api.zerobounce.net/v2/validate?api_key={api_key}&email=contact@dhisana.ai"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as response:
                status = response.status
                data = await safe_json(response)

                if status != 200:
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": f"Non-200 from ZeroBounce: {status}"
                    }
                # If the API key is invalid, ZeroBounce might return status=200 but "api_key_invalid"
                if data and data.get("status") == "invalid" and data.get("sub_status") == "api_key_invalid":
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": "ZeroBounce indicates invalid API key"
                    }
                return {"success": True, "status_code": status, "error_message": None}
    except Exception as e:
        logger.error(f"ZeroBounce test failed: {e}")
        return {"success": False, "status_code": 0, "error_message": str(e)}

async def test_openai(api_key: str, model_name: str, reasoning_effort: str) -> Dict[str, Any]:
    """
    Tests OpenAI API key by making a simple chat completion request.
    - If the model name starts with 'o3-', includes 'reasoning_effort' in the request.
    - Otherwise, uses the model name as is.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Base request body
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hello, world!"}],
        "max_completion_tokens": 5
    }

    # Only apply the reasoning parameter if it's an o3 series model
    if model_name.startswith("o3-"):
        data["reasoning_effort"] = reasoning_effort

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(url, headers=headers, json=data) as response:
                status = response.status
                resp_data = await response.json()

                if status != 200:
                    err_message = resp_data.get("error", {}).get("message", f"Non-200 from OpenAI: {status}")
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": err_message
                    }

                # Check if "error" is present in the response
                if "error" in resp_data:
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": resp_data["error"].get("message", "OpenAI error returned")
                    }

                return {"success": True, "status_code": status, "error_message": None}

    except Exception as e:
        logger.error(f"OpenAI test failed: {e}")
        return {"success": False, "status_code": 0, "error_message": str(e)}


async def test_google_workspace(api_key: str, subject: str) -> Dict[str, Any]:
    """
    Tests Google Workspace by listing Gmail messages using domain-wide delegation.
    Requires subject (email) to impersonate. 'me' then refers to that user mailbox.
    """
    try:
        creds_info = json.loads(api_key)
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://mail.google.com/"]
        )

        # Domain-wide delegation requires specifying the email to impersonate
        delegated_creds = creds.with_subject(subject)

        service = build("gmail", "v1", credentials=delegated_creds)

        # Execute synchronous call in a background thread to avoid blocking
        def _list_messages():
            return service.users().messages().list(userId="me").execute()

        response = await asyncio.to_thread(_list_messages)

        if "messages" in response:
            return {"success": True, "status_code": 200, "error_message": None}
        return {
            "success": False,
            "status_code": 200,
            "error_message": "API responded but no 'messages' key found"
        }
    except Exception as e:
        logger.error(f"Google Workspace test failed: {e}")
        return {"success": False, "status_code": 0, "error_message": str(e)}

async def test_serpapi(api_key: str) -> Dict[str, Any]:
    url = f"https://serpapi.com/search?engine=google&q=hello+world&api_key={api_key}"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as response:
                status = response.status
                data = await safe_json(response)

                if status != 200:
                    err_message = None
                    if data and isinstance(data, dict):
                        err_message = data.get("error")
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": err_message or f"Non-200 from SERPAPI: {status}"
                    }
                # Some SERP API errors might still be 200 but contain an 'error' field
                if data and "error" in data:
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": data["error"]
                    }
                return {"success": True, "status_code": status, "error_message": None}
    except Exception as e:
        logger.error(f"SERP API test failed: {e}")
        return {"success": False, "status_code": 0, "error_message": str(e)}

async def test_proxycurl(api_key: str) -> Dict[str, Any]:
    url = "https://nubela.co/proxycurl/api/v2/linkedin"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"linkedin_profile_url": "https://www.linkedin.com/in/satyanadella"}
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url, headers=headers, params=params) as response:
                status = response.status
                data = await safe_json(response)

                if status != 200:
                    err_message = None
                    if data and isinstance(data, dict):
                        err_message = data.get("message") or data.get("detail")
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": err_message or f"Non-200 from Proxycurl: {status}"
                    }
                return {"success": True, "status_code": status, "error_message": None}
    except Exception as e:
        logger.error(f"Proxycurl test failed: {e}")
        return {"success": False, "status_code": 0, "error_message": str(e)}

async def test_apollo(api_key: str) -> Dict[str, Any]:
    organization_domain = 'microsoft.com'
    url = f'https://api.apollo.io/api/v1/organizations/enrich?domain={organization_domain}'
    logger.debug(f"Making GET request to Apollo for domain: {organization_domain}")
    headers = {"X-Api-Key": api_key}

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url, headers=headers) as response:
                status = response.status
                if status == 200:
                    result = await response.json()
                    logger.info("Successfully retrieved organization info from Apollo.")
                    return {"success": True, "status_code": status}

                elif status == 429:
                    msg = "Rate limit exceeded"
                    logger.warning(msg)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=429,
                        message=msg
                    )
                else:
                    err_message = None
                    if response.content_type == "application/json":
                        data = await response.json()
                        err_message = data.get("message")
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": err_message or f"Non-200 from Apollo: {status}"
                    }
    except Exception as e:
        logger.error(f"Apollo test failed: {e}")
        return {"success": False, "status_code": 0, "error_message": str(e)}

async def test_hubspot(api_key: str) -> Dict[str, Any]:
    url = "https://api.hubapi.com/account-info/v3/details"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with session.get(url, headers=headers) as response:
                status = response.status
                data = await safe_json(response)

                if status != 200:
                    err_message = None
                    if data and isinstance(data, dict):
                        err_message = data.get("message") or data.get("error")
                    return {
                        "success": False,
                        "status_code": status,
                        "error_message": err_message or f"Non-200 from HubSpot: {status}"
                    }
                if data and "portalId" in data:
                    return {"success": True, "status_code": status, "error_message": None}

                return {
                    "success": False,
                    "status_code": status,
                    "error_message": "Did not find 'portalId' in the response."
                }
    except Exception as e:
        logger.error(f"HubSpot test failed: {e}")
        return {"success": False, "status_code": 0, "error_message": str(e)}

###############################################################################
#                         MAIN CONNECTIVITY FUNCTION
###############################################################################

async def test_connectivity(tool_config: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Checks API key connectivity for multiple tools and returns a dictionary
    with the result for each. 
    We now also handle:
      - 'modelName' and 'reasoningEffort' for OpenAI
      - 'subjectEmail' for Google Workspace
    """
    # Map tool names to test functions
    # Note: We will handle special parameters for openai / google in code below
    test_mapping = {
        "zerobounce": test_zerobounce,
        "openai": test_openai,                   # updated signature
        "googleworkspace": test_google_workspace, # updated signature
        "serpapi": test_serpapi,
        "proxycurl": test_proxycurl,
        "apollo": test_apollo,
        "hubspot": test_hubspot,
    }

    results = {}
    for tool in tool_config:
        tool_name = tool.get("name")
        config_entries = tool.get("configuration", [])
        if not tool_name:
            logger.warning("Tool entry missing 'name' field.")
            results["unknown_tool"] = {
                "success": False,
                "status_code": 0,
                "error_message": "Tool entry missing 'name'."
            }
            continue

        if tool_name not in test_mapping:
            logger.warning(f"No test function found for tool: {tool_name}")
            results[tool_name] = {
                "success": False,
                "status_code": 0,
                "error_message": f"No test function for tool '{tool_name}'"
            }
            continue

        # Common config param: apiKey
        api_key = next((c["value"] for c in config_entries if c["name"] == "apiKey"), None)
        if not api_key:
            logger.warning(f"Tool '{tool_name}' missing 'apiKey' in configuration.")
            results[tool_name] = {
                "success": False,
                "status_code": 0,
                "error_message": "Missing apiKey"
            }
            continue

        logger.info(f"Testing connectivity for {tool_name}...")

        # Special handling for openai
        if tool_name == "openai":
            model_name = next((c["value"] for c in config_entries if c["name"] == "modelName"), "gpt-4o")
            reasoning_effort = next((c["value"] for c in config_entries if c["name"] == "reasoningEffort"), "medium")
            results[tool_name] = await test_openai(api_key, model_name, reasoning_effort)

        # Special handling for googleworkspace
        elif tool_name == "googleworkspace":
            subject_email = next((c["value"] for c in config_entries if c["name"] == "subjectEmail"), None)
            if not subject_email:
                results[tool_name] = {
                    "success": False,
                    "status_code": 0,
                    "error_message": "Missing subjectEmail for Google Workspace"
                }
            else:
                results[tool_name] = await test_google_workspace(api_key, subject_email)

        # All other tools
        else:
            # Directly call the mapped test function with just api_key
            results[tool_name] = await test_mapping[tool_name](api_key)

    return results
