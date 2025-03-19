import os
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp

from dhisana.schemas.sales import HubSpotLeadInformation
from dhisana.utils.field_validators import validate_and_clean_email
from dhisana.utils.hubspot_crm_tools import lookup_contact_by_name_and_domain

logger = logging.getLogger(__name__)
from dhisana.utils.apollo_tools import enrich_user_info_with_apollo
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

# --------------------------------------------------------------------------------
# 1. Access Token Helpers
# --------------------------------------------------------------------------------

def get_zero_bounce_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the ZeroBounce access token from the provided tool configuration or environment.
    """
    if tool_config:
        zerobounce_config = next(
            (item for item in tool_config if item.get("name") == "zerobounce"), None
        )
        if zerobounce_config:
            config_map = {
                c["name"]: c["value"]
                for c in zerobounce_config.get("configuration", [])
                if c
            }
            ZERO_BOUNCE_API_KEY = config_map.get("apiKey")
        else:
            logger.warning("ZeroBounce config not provided or missing 'apiKey'.")
            ZERO_BOUNCE_API_KEY = None
    else:
        logger.warning("ZeroBounce config not provided or missing 'apiKey'.")
        ZERO_BOUNCE_API_KEY = None

    ZERO_BOUNCE_API_KEY = ZERO_BOUNCE_API_KEY or os.getenv("ZERO_BOUNCE_API_KEY")
    if not ZERO_BOUNCE_API_KEY:
        logger.warning("ZERO_BOUNCE_API_KEY not found in config or env.")
        return ""  # Return empty so we don't break

    return ZERO_BOUNCE_API_KEY


def get_hunter_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the Hunter.io access token from the provided tool configuration or environment.
    """
    if tool_config:
        hunter_config = next(
            (item for item in tool_config if item.get("name") == "hunter"), None
        )
        if hunter_config:
            config_map = {
                c["name"]: c["value"]
                for c in hunter_config.get("configuration", [])
                if c
            }
            HUNTER_API_KEY = config_map.get("apiKey")
        else:
            logger.warning("Hunter config not provided or missing 'apiKey'.")
            HUNTER_API_KEY = None
    else:
        logger.warning("Hunter config not provided or missing 'apiKey'.")
        HUNTER_API_KEY = None

    HUNTER_API_KEY = HUNTER_API_KEY or os.getenv("HUNTER_API_KEY")
    if not HUNTER_API_KEY:
        logger.warning("HUNTER_API_KEY not found in config or env.")
        return ""  # Return empty so we don't break

    return HUNTER_API_KEY


# --------------------------------------------------------------------------------
# 2. Provider-Specific Validation Functions
# --------------------------------------------------------------------------------

def _map_zerobounce_status_to_confidence(status: str) -> str:
    """
    Map ZeroBounce's status string to "high", "medium", or "low" confidence.
    """
    status = status.lower()
    if status == "valid":
        return "high"
    elif status in ["catch-all", "unknown"]:
        return "medium"
    elif status in ["spamtrap", "invalid"]:
        return "low"
    return "low"


@assistant_tool
async def check_email_validity_with_zero_bounce(
    email_id: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Validate a single email address using the ZeroBounce API, with caching.
    Returns: {
      "email": str,
      "confidence": "high"|"medium"|"low",
      "is_valid": bool
    }
    """
    logger.info("Entering check_email_validity_with_zero_bounce for email_id: %s", email_id)
    import re
    if not email_id or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email_id):
        return {
            "email": email_id,
            "confidence": "low",
            "is_valid": False
        }

    cache_key = f"{email_id}"
    cached_response = retrieve_output("zerobounce_validate", cache_key)
    if cached_response is not None:
        logger.info("Cache hit for ZeroBounce validate.")
        if not cached_response:
            return {
                "email": email_id,
                "confidence": "low",
                "is_valid": False
            }
        return json.loads(cached_response[0])

    # Get API key
    ZERO_BOUNCE_API_KEY = get_zero_bounce_access_token(tool_config)
    if not ZERO_BOUNCE_API_KEY:
        logger.warning("No ZeroBounce API key available. Returning low confidence.")
        return {
            "email": email_id,
            "confidence": "low",
            "is_valid": False
        }

    url = (
        "https://api.zerobounce.net/v2/validate"
        f"?api_key={ZERO_BOUNCE_API_KEY}&email={email_id}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    content = await safe_read_json_or_text(response)
                    logger.warning(
                        f"[ZeroBounce] Non-200 status: {response.status} => {content}"
                    )
                    # Return fallback instead of raising
                    final_response = {
                        "email": email_id,
                        "confidence": "low",
                        "is_valid": False
                    }
                    cache_output("zerobounce_validate", cache_key, [json.dumps(final_response)])
                    return final_response

                result = await response.json()
    except Exception as ex:
        logger.warning(f"[ZeroBounce] Exception occurred => {ex}")
        return {
            "email": email_id,
            "confidence": "low",
            "is_valid": False
        }

    zb_status = result.get("status", "").lower()  # e.g. "valid", "invalid"
    confidence = _map_zerobounce_status_to_confidence(zb_status)
    is_valid = (confidence == "high")

    final_response = {
        "email": email_id,
        "confidence": confidence,
        "is_valid": is_valid
    }
    cache_output("zerobounce_validate", cache_key, [json.dumps(final_response)])
    logger.info("Exiting check_email_validity_with_zero_bounce.")
    return final_response


def _map_hunter_status_to_confidence(hunter_result: str) -> str:
    """
    Map Hunter's email verifier result to "high", "medium", or "low" confidence.
    Possible results: deliverable, undeliverable, risky, unknown, accept_all.
    """
    val = hunter_result.lower()
    if val == "deliverable":
        return "high"
    elif val in ["unknown", "accept_all"]:
        return "medium"
    elif val in ["risky", "undeliverable"]:
        return "low"
    return "low"


@assistant_tool
async def check_email_validity_with_hunter(
    email_id: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Validate a single email address using Hunter.io's email verification API.
    Returns: {
      "email": str,
      "confidence": "high"|"medium"|"low",
      "is_valid": bool
    }
    """
    logger.info("Entering check_email_validity_with_hunter for email_id: %s", email_id)
    import re
    if not email_id or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email_id):
        return {
            "email": email_id,
            "confidence": "low",
            "is_valid": False
        }

    HUNTER_API_KEY = get_hunter_access_token(tool_config)
    if not HUNTER_API_KEY:
        logger.warning("No Hunter API key available. Returning low confidence.")
        return {
            "email": email_id,
            "confidence": "low",
            "is_valid": False
        }

    url = (
        "https://api.hunter.io/v2/email-verifier"
        f"?email={email_id}&api_key={HUNTER_API_KEY}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    content = await safe_read_json_or_text(response)
                    logger.warning(f"[Hunter] Non-200 status: {response.status} => {content}")
                    return {
                        "email": email_id,
                        "confidence": "low",
                        "is_valid": False
                    }

                result = await response.json()
    except Exception as ex:
        logger.warning(f"[Hunter] Exception occurred => {ex}")
        return {
            "email": email_id,
            "confidence": "low",
            "is_valid": False
        }

    data = result.get("data", {})
    verifier_result = data.get("result", "")  # "deliverable", "undeliverable", etc.
    confidence = _map_hunter_status_to_confidence(verifier_result)
    is_valid = (confidence == "high")

    final_response = {
        "email": email_id,
        "confidence": confidence,
        "is_valid": is_valid
    }
    logger.info("Exiting check_email_validity_with_hunter.")
    return final_response


# --------------------------------------------------------------------------------
# 3. Provider-Specific Guessing Functions
# --------------------------------------------------------------------------------

@assistant_tool
async def guess_email_with_zero_bounce(
    first_name: str,
    last_name: str,
    domain: str,
    user_linkedin_url: Optional[str] = None,  # Ignored by ZeroBounce
    middle_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Attempt to guess the email using ZeroBounce's guessFormat endpoint, with caching.
    We assume the API returns an "email" and an "email_confidence" field.
    """
    logger.info("Entering guess_email_with_zero_bounce.")
    if not first_name or not last_name or not domain:
        logger.error("Required parameters first_name, last_name, and domain must be provided.")
        return {"email": "", "email_confidence": "low"}

    cache_key = f"{first_name}_{last_name}_{domain}_{middle_name or ''}"
    cached_response = retrieve_output("zerobounce_guess", cache_key)
    if cached_response is not None:
        logger.info("Cache hit for ZeroBounce guess.")
        return json.loads(cached_response[0]) if cached_response else {"email": "", "email_confidence": "low"}

    ZERO_BOUNCE_API_KEY = get_zero_bounce_access_token(tool_config)
    if not ZERO_BOUNCE_API_KEY:
        logger.warning("No ZeroBounce API key available. Returning low confidence guess.")
        return {"email": "", "email_confidence": "low"}

    base_url = "https://api.zerobounce.net/v2/guessformat"
    query_params = (
        f"?api_key={ZERO_BOUNCE_API_KEY}"
        f"&domain={domain}"
        f"&first_name={first_name}"
        f"&middle_name={middle_name or ''}"
        f"&last_name={last_name}"
    )
    url = base_url + query_params

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    content = await safe_read_json_or_text(response)
                    logger.warning(f"[ZeroBounce] guessFormat error: {response.status} => {content}")
                    return {"email": "", "email_confidence": "low"}
                result = await response.json()
    except Exception as ex:
        logger.warning(f"[ZeroBounce] Exception => {ex}")
        return {"email": "", "email_confidence": "low"}

    # If the API doesn't provide "email_confidence", you can supply a fallback:
    if "email_confidence" not in result:
        result["email_confidence"] = "medium" if result.get("email") else "low"

    cache_output("zerobounce_guess", cache_key, [json.dumps(result)])
    logger.info("Exiting guess_email_with_zero_bounce.")
    return result


@assistant_tool
async def guess_email_with_hunter(
    first_name: str,
    last_name: str,
    domain: str,
    user_linkedin_url: Optional[str] = None,  # Ignored by Hunter
    middle_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Attempt to guess the email using Hunter.io's email-finder endpoint.
    We'll interpret the "score" (0-100) from the response and map it to "email_confidence".
    """
    logger.info("Entering guess_email_with_hunter.")
    if not first_name or not last_name or not domain:
        logger.error("Required parameters first_name, last_name, and domain must be provided.")
        return {"email": "", "email_confidence": "low"}

    HUNTER_API_KEY = get_hunter_access_token(tool_config)
    if not HUNTER_API_KEY:
        logger.warning("No Hunter API key available. Returning low-confidence guess.")
        return {"email": "", "email_confidence": "low"}

    url = (
        "https://api.hunter.io/v2/email-finder"
        f"?domain={domain}"
        f"&first_name={first_name}"
        f"&last_name={last_name}"
        f"&api_key={HUNTER_API_KEY}"
    )
    # If needed, you could pass middle_name, e.g. "&middle_name={middle_name}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    content = await safe_read_json_or_text(response)
                    logger.warning(f"[Hunter] email-finder error: {response.status} => {content}")
                    return {"email": "", "email_confidence": "low"}

                result = await response.json()
    except Exception as ex:
        logger.warning(f"[Hunter] Exception => {ex}")
        return {"email": "", "email_confidence": "low"}

    data = result.get("data", {})
    found_email = data.get("email", "")

    # Safely parse numeric score
    raw_score = data.get("score")  # might be int, float, None, or not present
    try:
        score = float(raw_score) if raw_score is not None else 0.0
    except (ValueError, TypeError):
        score = 0.0

    if score >= 80:
        confidence = "high"
    elif score >= 50:
        confidence = "medium"
    else:
        confidence = "low"

    output = {
        "email": found_email,
        "email_confidence": confidence
    }
    logger.info("Exiting guess_email_with_hunter.")
    return output


@assistant_tool
async def guess_email_with_apollo(
    first_name: str,
    last_name: str,
    domain: str,
    user_linkedin_url: Optional[str] = None,
    middle_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Attempt to guess/enrich an email using Apollo, then re-check with ZeroBounce
    to ensure we have acceptable confidence.
    """
    logger.info("Entering guess_email_with_apollo.")
    if not first_name or not last_name or not domain:
        logger.error("Required parameters first_name, last_name, and domain must be provided.")
        return {"email": "", "email_confidence": "low"}

    # If Apollo config is absent, return low
    apollo_config = next((item for item in tool_config or [] if item.get("name") == "apollo"), None)
    if not apollo_config:
        logger.warning("No Apollo config found; cannot enrich with Apollo.")
        return {"email": "", "email_confidence": "low"}

    input_lead_info = {
        "first_name": first_name,
        "last_name": last_name,
        "primary_domain_of_organization": domain,
        "user_linkedin_url": user_linkedin_url or ""
    }

    try:
        # Attempt to enrich
        response = await enrich_user_info_with_apollo(input_lead_info, tool_config)
    except Exception as ex:
        logger.warning(f"[Apollo] Exception => {ex}")
        return {"email": "", "email_confidence": "low"}

    apollo_email = response.get("email", "")
    if not apollo_email:
        # No email found
        return {"email": "", "email_confidence": "low"}

    # Now re-check with ZeroBounce for final confidence
    zb_result = await check_email_validity_with_hunter(apollo_email, tool_config)
    # If ZeroBounce says "high" or "medium" => we keep it, else "low"
    zb_conf = zb_result.get("confidence", "low")
    if zb_conf in ["high", "medium"]:
        return {
            "email": apollo_email,
            "email_confidence": zb_conf
        }
    else:
        return {
            "email": apollo_email,
            "email_confidence": "low"
        }

GUESS_EMAIL_TOOL_MAP = {
    "zerobounce": guess_email_with_zero_bounce,
    "hunter": guess_email_with_hunter,
    "apollo": guess_email_with_apollo,
}


# --------------------------------------------------------------------------------
# 4. Aggregators (High-Level Validation + Guess)
# --------------------------------------------------------------------------------

@assistant_tool
async def check_email_validity(
    email_id: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Validate an email address by checking each provider in priority order:
      1) ZeroBounce
      2) Hunter
    If a provider returns high confidence, we stop. Otherwise we continue.
    """
    logger.info("Entering check_email_validity method.")
    if not tool_config:
        logger.warning("No tool configuration found; returning low confidence.")
        return {
            "email": email_id,
            "confidence": "low",
            "is_valid": False
        }

    provider_names = [item.get("name") for item in tool_config if item.get("name")]
    # No mention of Apollo for direct validation, so keep the same priority:
    priority = ["hunter", "zerobounce"]

    final_result = {
        "email": email_id,
        "confidence": "low",
        "is_valid": False
    }

    for provider in priority:
        if provider in provider_names:
            if provider == "zerobounce":
                result = await check_email_validity_with_zero_bounce(email_id, tool_config)
            elif provider == "hunter":
                result = await check_email_validity_with_hunter(email_id, tool_config)
            else:
                continue

            final_result = result
            # If "high" or "low" confidence, stop
            if result["confidence"] == "high"  or result["confidence"] == "low":
                logger.info(f"{provider} gave high confidence. Stopping further checks.")
                break

    logger.info("Exiting check_email_validity method with result: %s", final_result)
    return final_result


@assistant_tool
async def guess_email(
    first_name: str,
    last_name: str,
    domain: str,
    middle_name: Optional[str] = None,
    user_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Attempt to guess/enrich the email using provider(s) indicated in the tool_config,
    in the priority order:
      1) Hunter
      2) ZeroBounce
      3) Apollo  (last resort, re-check with ZeroBounce)
    If the first guess is "high" confidence, we stop. Otherwise move on, etc.
    """
    logger.info("Entering guess_email method.")
    if not tool_config:
        logger.warning("No tool configuration found; returning low-confidence guess.")
        return {"email": "", "email_confidence": "low"}

    provider_names = [item.get("name") for item in tool_config if item.get("name")]
    priority = ["hunter", "zerobounce",  "apollo"]
    final_result = {"email": "", "email_confidence": "low"}

    for provider in priority:
        if provider in provider_names:
            guess_func = GUESS_EMAIL_TOOL_MAP[provider]
            result = await guess_func(
                first_name,
                last_name,
                domain,
                user_linkedin_url,
                middle_name,
                tool_config
            )

            final_result = result
            if result.get("email_confidence") == "high":
                logger.info(f"{provider} gave high confidence on guess. Stopping further guesses.")
                break
            # If you want to stop at "medium" as well, you could:
            # if result.get("email_confidence") in ["high", "medium"]:
            #    break

    logger.info("Exiting guess_email method with result: %s", final_result)
    return final_result


# --------------------------------------------------------------------------------
# 5. Orchestrating everything in a single function
# --------------------------------------------------------------------------------

@assistant_tool
async def process_email_properties(
    input_properties: Dict[str, Any],
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    logger.info("Entering process_email_properties.")

    first_name = input_properties.get("first_name", "")
    last_name = input_properties.get("last_name", "")
    email = input_properties.get("email", "")
    email = validate_and_clean_email(email)
    additional_properties = input_properties.get("additional_properties", {})
    user_linkedin_url = input_properties.get("user_linkedin_url", "")
    domain = input_properties.get("primary_domain_of_organization", "")

    if email:
        # Validate existing email
        val_result = await check_email_validity(email, tool_config)
        is_valid = val_result.get("is_valid", False)
        confidence = val_result.get("confidence", "").lower()  # e.g. 'high', 'medium', 'low'

        if is_valid and confidence == "high":
            # Already good
            input_properties["email_validation_status"] = "valid"
        else:
            # Invalid or medium/low -> mark invalid
            input_properties["email_validation_status"] = "invalid"

    else:
        # No existing email -> must guess if domain is present
        if not domain:
            logger.info("No primary domain found; cannot guess.")
            additional_properties["guessed_email"] = ""
            input_properties["email"] = ""
            input_properties["email_validation_status"] = "invalid"
        else:
            # --- FIX STARTS HERE ---
            hubspot_lead_info = None
            #TODO: test more and enable
            # hubspot_lead_info = await lookup_contact_by_name_and_domain(
            #     first_name,
            #     last_name,
            #     domain,
            #     tool_config=tool_config
            # )
            if (
                hubspot_lead_info
                and isinstance(hubspot_lead_info, HubSpotLeadInformation)
                and hubspot_lead_info.email
            ):
                # We found a HubSpot email; validate it
                hubspot_email = hubspot_lead_info.email
                val_result = await check_email_validity(hubspot_email, tool_config)
                is_valid = val_result.get("is_valid", False)
                confidence = val_result.get("confidence", "").lower()
                input_properties["email"] = hubspot_email
                if is_valid and confidence == "high":
                    # Accept HubSpot email
                    input_properties["email"] = hubspot_email
                    input_properties["email_validation_status"] = "valid"
                else:
                    # HubSpot email is not high-confidence => guess
                    guessed_result = await guess_email(
                        first_name,
                        last_name,
                        domain,
                        "",
                        user_linkedin_url,
                        tool_config
                    )
                    if is_guess_usable(guessed_result):
                        if guessed_result.get("email_confidence", "").lower() == "high":
                            input_properties["email"] = guessed_result["email"]
                            input_properties["email_validation_status"] = "valid"
                        else:
                            additional_properties["guessed_email"] = guessed_result.get("email", "")
                            input_properties["email"] = guessed_result.get("email", "")
                            input_properties["email_validation_status"] = "invalid"
                    else:
                        additional_properties["guessed_email"] = guessed_result.get("email", "")
                        input_properties["email"] = guessed_result.get("email", "")
                        input_properties["email_validation_status"] = "invalid"
            else:
                # No valid HubSpot match => guess
                guessed_result = await guess_email(
                    first_name,
                    last_name,
                    domain,
                    "",
                    user_linkedin_url,
                    tool_config
                )
                if is_guess_usable(guessed_result):
                    if guessed_result.get("email_confidence", "").lower() == "high":
                        input_properties["email"] = guessed_result["email"]
                        input_properties["email_validation_status"] = "valid"
                    else:
                        additional_properties["guessed_email"] = guessed_result.get("email", "")
                        input_properties["email"] = guessed_result["email"]
                        input_properties["email_validation_status"] = "invalid"
                else:
                    additional_properties["guessed_email"] = guessed_result.get("email", "")
                    input_properties["email"] = guessed_result.get("email", "")
                    input_properties["email_validation_status"] = "invalid"
            # --- FIX ENDS HERE ---

    input_properties["additional_properties"] = additional_properties
    logger.info("Exiting process_email_properties.")
    return input_properties

# --------------------------------------------------------------------------------
# 6. Helper Functions
# --------------------------------------------------------------------------------

async def safe_read_json_or_text(response: aiohttp.ClientResponse) -> Any:
    """
    Safely attempts to parse an aiohttp response as JSON, else returns text.
    """
    try:
        return await response.json()
    except Exception:
        return await response.text()


def extract_domain(email: str) -> str:
    """Extract domain from email ( user@domain.com -> domain.com )."""
    if "@" not in email:
        return ""
    return email.split("@")[-1].strip()


def is_guess_usable(guess_result: Dict[str, Any]) -> bool:
    """
    Decide if a guessed email is "usable".
    Here we treat "high" or "medium" as usable.
    Adjust as needed.
    """
    if not guess_result:
        return False
    email_confidence = guess_result.get("email_confidence", "").lower()
    return email_confidence in ["high", "medium"]
