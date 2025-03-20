"""
This module provides a set of functions to enrich lead and organization information
using various enrichment tools such as Apollo or ProxyCurl. It also allows
extraction and validation of domains from user-provided links or company websites.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import tldextract

from dhisana.utils.check_email_validity_tools import process_email_properties
from dhisana.utils.company_utils import normalize_company_name
from dhisana.utils.field_validators import (
    normalize_linkedin_url, normalize_linkedin_company_url, normalize_salesnav_url, normalize_linkedin_company_salesnav_url)
from dhisana.utils.apollo_tools import enrich_user_info_with_apollo
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.domain_parser import get_domain_from_website, is_excluded_domain
from dhisana.utils.proxy_curl_tools import (
    enrich_job_info_from_proxycurl,
    enrich_organization_info_from_proxycurl,
    enrich_user_info_with_proxy_curl,
)
from dhisana.utils.research_lead import research_company_with_full_info_ai, research_lead_with_full_info_ai
from dhisana.utils.serpapi_search_tools import (
    find_organization_linkedin_url_with_google_search,
    find_user_linkedin_url_google,
    get_company_domain_from_google_search,
    get_company_website_from_linkedin_url,
)
from dhisana.utils.field_validators import (
    validate_and_clean_email, 
    validation_organization_domain,
    validate_website_url
    )

# The enrichment tools that are permissible for usage.
ALLOWED_ENRICHMENT_TOOLS = ["proxycurl", "apollo", "zoominfo"]

# A map from tool name to the corresponding function that will enrich user info.
USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP = {
    "apollo": enrich_user_info_with_apollo,
    "proxycurl": enrich_user_info_with_proxy_curl,
}

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_user_name(cloned_properties: dict) -> dict:
    """
    Cleans up user name fields: 'full_name', 'first_name', 'last_name'.
    Returns the updated dictionary. If values are invalid or placeholders, sets them to ''.
    """

    if not isinstance(cloned_properties, dict):
        return {}

    def normalize(name) -> str:
        if not name or not isinstance(name, str):
            return ""
        # Common placeholders or invalid tokens
        invalid_tokens = [
            "null", "none", "na", "n.a", "notfound", "error", 
            "na.", "na,", "notavilable", "notavailable", ""
        ]
        stripped = name.strip().lower()
        if stripped in invalid_tokens:
            return ""

        # Remove anything in parentheses
        stripped = re.sub(r"\(.*?\)", "", stripped)
        # Remove anything after '|'
        stripped = stripped.split("|", 1)[0]
        # Remove extra non-alphanumeric characters (but allow whitespace)
        stripped = re.sub(r"[^a-zA-Z0-9\s]", "", stripped)
        # Capitalize first letter, lowercase the rest
        return stripped.strip().capitalize()

    full_name = normalize(cloned_properties.get("full_name"))
    first_name = normalize(cloned_properties.get("first_name"))
    last_name  = normalize(cloned_properties.get("last_name"))

    # If full_name is empty, build from first_name + last_name
    if first_name and last_name:
        full_name = (first_name + " " + last_name).strip()

    cloned_properties["full_name"] = full_name
    cloned_properties["first_name"] = first_name
    cloned_properties["last_name"] = last_name
    return cloned_properties


def validate_and_cleanup(cloned_properties: dict) -> dict:
    """
    Wrapper to validate & normalize various properties in a dictionary.
    Safe against None, non-dict, or missing keys. Returns a cleaned dict.
    """

    if not isinstance(cloned_properties, dict):
        return {}

    # Safely fetch each key, process, and reassign
    cloned_properties["user_linkedin_url"] = normalize_linkedin_url(
        cloned_properties.get("user_linkedin_url")
    )
    cloned_properties["user_linkedin_salesnav_url"] = normalize_salesnav_url(
        cloned_properties.get("user_linkedin_salesnav_url")
    )
    cloned_properties["organization_linkedin_url"] = normalize_linkedin_company_url(
        cloned_properties.get("organization_linkedin_url")
    )
    cloned_properties["organization_linkedin_salesnav_url"] = normalize_linkedin_company_salesnav_url(
        cloned_properties.get("organization_linkedin_salesnav_url")
    )
    cloned_properties["email"] = validate_and_clean_email(
        cloned_properties.get("email")
    )
    cloned_properties["primary_domain_of_organization"] = validation_organization_domain(
        cloned_properties.get("primary_domain_of_organization")
    )
    cloned_properties["organization_website"] = validate_website_url(
        cloned_properties.get("organization_website")
    )
    cloned_properties["organization_name"] = normalize_company_name(
        cloned_properties.get("organization_name")
    )

    # Clean up user name fields
    cloned_properties = cleanup_user_name(cloned_properties)

    return cloned_properties


@assistant_tool
async def enrich_lead_information(
    user_properties: Dict[str, Any],
    use_strict_check: bool = True,
    get_valid_email: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Enrich lead information including company details and LinkedIn URL.
    Steps performed:
      1) Enrich organization information (primary domain, LinkedIn URL, website).
      2) Attempt to fix/find user LinkedIn URL if not present.
      3) Enrich with additional provider data and validate matches (e.g., Apollo).

    :param user_properties: Dictionary containing user/lead details to be enriched.
    :param use_strict_check: Whether to use strict matching in certain search functions.
    :param tool_config: Optional list of tool configuration dicts (e.g., [{"name": "apollo"}, ...]).
    :return: Enriched user_properties dictionary.
    """
    logger.debug("Starting enrich_lead_information with user_properties: %s", user_properties)
    cloned_properties = dict(user_properties)

    cloned_properties = validate_and_cleanup(cloned_properties)
    
    cloned_properties = await enrich_user_info(
        input_properties=cloned_properties,
        use_strict_check=use_strict_check,
        tool_config=tool_config,
    )

    cloned_properties = await enrich_with_provider(cloned_properties, tool_config)

    await set_organization_domain(
        row=cloned_properties,
        use_strict_check=use_strict_check,
        tool_config=tool_config,
    )
    
    if get_valid_email:
        await process_email_properties(cloned_properties, tool_config)
    
    cloned_properties = validate_and_cleanup(cloned_properties)
    summary = await research_lead_with_full_info_ai(cloned_properties, "", tool_config=tool_config)
    if summary:
        cloned_properties["research_summary"] = summary.get("research_summary", "")
    return cloned_properties


async def enrich_user_info(
    input_properties: Dict[str, Any],
    use_strict_check: bool,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Attempt to find or fix a user's LinkedIn URL using name, title, location, and company information.

    :param input_properties: Dictionary containing user/lead details.
    :param use_strict_check: Whether to use strict matching during searches.
    :param tool_config: Optional list of tool configurations dicts.
    :return: Updated dictionary with user LinkedIn URL if found.
    """
    logger.debug("Starting enrich_user_info for: %s", input_properties.get("full_name"))
    user_linkedin_url = (input_properties.get("user_linkedin_url") or "").strip()
    input_properties["linkedin_url_match"] = False

    if not user_linkedin_url:
        full_name = (input_properties.get("full_name") or "").strip()
        if not full_name:
            first_name = (input_properties.get("first_name", "") or "").strip()
            last_name = (input_properties.get("last_name", "") or "").strip()
            full_name = f"{first_name} {last_name}".strip()

        title = input_properties.get("job_title", "") or ""
        location = input_properties.get("lead_location", "") or ""
        org_name = (input_properties.get("organization_name", "") or "").strip()
        org_domain = (input_properties.get("primary_domain_of_organization", "") or "").strip()
        if full_name and org_name:
            user_linkedin_url = await find_user_linkedin_url_google(
                user_name=full_name,
                user_title=title,
                user_location=location,
                user_company=org_name,
                user_company_domain= org_domain,
                use_strict_check=use_strict_check,
                tool_config=tool_config,
            )
            input_properties["user_linkedin_url"] = user_linkedin_url

    return input_properties


async def enrich_with_provider(
    cloned_properties: Dict[str, Any],
    tool_config: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Enrich user/lead data using one of the allowed provider tools (e.g., Apollo, ZoomInfo).
    The tool_config should specify which tool(s) to use.

    :param cloned_properties: Dictionary containing user/lead details to be enriched.
    :param tool_config: List of tool configuration dicts, e.g. [{"name": "apollo"}, ...].
    :return: The updated dictionary after enrichment.
    :raises ValueError: If no tool_config is provided or no suitable enrichment tool is found.
    """
    if not tool_config:
        raise ValueError("No tool configuration found.")

    chosen_tool_func = None
    for allowed_tool_name in ALLOWED_ENRICHMENT_TOOLS:
        for item in tool_config:
            logger.debug("Selected tool: %s", item.get("name"))
            if item.get("name") == allowed_tool_name and allowed_tool_name in USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP:
                chosen_tool_func = USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP[allowed_tool_name]
                break
        if chosen_tool_func:
            break

    if not chosen_tool_func:
        raise ValueError("No suitable email validation tool found in tool_config.")

    return await chosen_tool_func(cloned_properties, tool_config)


async def enrich_organization_info_from_name(
    row: Dict[str, str],
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Given a dictionary (treated like a CSV row) containing 'organization_name',
    'organization_linkedin_url', and 'website' keys, enrich the row only if the
    domain and website are currently empty.

    :param row: Dictionary representing a lead or company record.
    :param use_strict_check: Whether to use strict matching for searches.
    :param tool_config: Optional list of tool configuration dicts.
    """
    org_name_key = "organization_name"
    org_domain_key = "primary_domain_of_organization"
    linkedin_url_key = "organization_linkedin_url"
    website_key = "organization_website"

    org_name = (row.get(org_name_key) or "").strip()
    logger.debug("Enriching organization info from name: %s", org_name)
    if org_name.lower() in ["none", "freelance"]:
        row[org_name_key] = ""
        org_name = ""

    if not org_name:
        return

    if row.get(org_domain_key) or row.get(website_key):
        return

    linkedin_url = row.get(linkedin_url_key, "").strip()
    if not linkedin_url:
        linkedin_url = await find_organization_linkedin_url_with_google_search(
            org_name,
            company_location="US",
            use_strict_check=use_strict_check,
            tool_config=tool_config,
        )

    if linkedin_url:
        row[linkedin_url_key] = linkedin_url
        await set_organization_domain(row, use_strict_check, tool_config)
    else:
        row[org_domain_key] = ""


async def set_organization_domain(
    row: Dict[str, str],
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Update the row with a 'primary_domain_of_organization' based on 'website' or
    search results if the domain is absent.

    :param row: Dictionary representing a lead or company record.
    :param use_strict_check: Whether to use strict matching for searches.
    :param tool_config: Optional list of tool configuration dicts.
    """
    org_name_key = "organization_name"
    org_domain_key = "primary_domain_of_organization"
    website_key = "organization_website"
    linkedin_url_key = "organization_linkedin_url"

    existing_domain = (row.get(org_domain_key) or "").strip()
    org_name = (row.get(org_name_key) or "").strip()
    logger.debug("Setting organization domain for organization: %s", org_name)
    logger.debug("Check existing_domain: %s", existing_domain)
    logger.debug("Check org_name: %s", org_name)

    if not existing_domain:
        company_website = (row.get(website_key) or "").strip()
        logger.debug("Check company_website: %s", company_website)
        extracted_domain = ""
        logger.debug("Initial extracted_domain: %s", extracted_domain)
        if not company_website and row.get(linkedin_url_key):
            company_website = await get_company_website_from_linkedin_url(row.get(linkedin_url_key))
            if company_website:
                logger.debug("Found company website from LinkedIn URL: %s", company_website)
                row[website_key] = company_website

        if company_website:
            extracted_domain = get_domain_from_website(company_website)
            logger.debug("extracted domain from website: %s", extracted_domain)
            if extracted_domain and is_excluded_domain(extracted_domain):
                extracted_domain = ""
                company_website = ""

        if not extracted_domain and not use_strict_check and org_name:
            logger.debug("Performing Google search to find domain for org_name: %s", org_name)
            extracted_domain = await get_company_domain_from_google_search(
                org_name,
                "US",
                tool_config=tool_config,
            )
            logger.debug("Found domain from Google search: %s", extracted_domain)

        row[org_domain_key] = extracted_domain or ""
        logger.debug("Final domain selected: %s", row[org_domain_key])
        row[website_key] = company_website or ""
    company_website = (row.get(website_key) or "").strip()
    if existing_domain and not company_website:
        row[website_key] = f"https://www.{existing_domain}"

async def get_organization_linkedin_url(lead: Dict[str, Any], tools: Optional[List[Dict[str, Any]]]) -> str:
    """
    Retrieve the organization's LinkedIn URL using the company name, domain, and search tools.
    Returns an empty string if the organization name is missing.
    """
    name = lead.get("organization_name", "").strip()
    if not name:
        return ""

    linkedin_url = await find_organization_linkedin_url_with_google_search(
        name,
        company_location="US",
        company_domain=lead.get("primary_domain_of_organization"),
        use_strict_check=True,
        tool_config=tools,
    )
    return linkedin_url
    
async def enrich_organization_info_from_company_url(
    organization_linkedin_url: str,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Given an organization LinkedIn URL, attempt to enrich its data (e.g. name, website)
    via ProxyCurl. If data is found, return the dict with domain set. Otherwise, return {}.
    """

    # Call ProxyCurl to enrich
    company_data = await enrich_organization_info_from_proxycurl(
        organization_linkedin_url=organization_linkedin_url,
        tool_config=tool_config
    )

    # If ProxyCurl returned any data, set domain, then return
    if company_data and isinstance(company_data, dict):
        await set_organization_domain(company_data, use_strict_check, tool_config)
        summary = await research_company_with_full_info_ai(company_data, "", tool_config=tool_config)
        if summary:
            company_data["organization_details"] = summary.get("research_summary", "")
        return company_data

    return {}


async def enrich_organization_info_from_job_url(
    job_url: str,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Given a LinkedIn job posting URL, fetch job details using Proxycurl.
    If job details are successfully retrieved, extract organization information
    (organization_name, organization_linkedin_url, primary_domain_of_organization, organization_website)
    and return them in a dictionary. If not found, return {}.
    """
    # Validate the job URL.
    if "linkedin.com/jobs/view/" not in job_url:
        logger.debug("URL is not a valid LinkedIn job posting; skipping enrichment.")
        return {}

    # Normalize the job URL to use 'www.linkedin.com'
    parsed = urlparse(job_url)
    normalized_job_url = parsed._replace(netloc="www.linkedin.com").geturl()

    logger.debug(f"Fetching job info from Proxycurl for URL: {normalized_job_url}")
    try:
        job_info = await enrich_job_info_from_proxycurl(
            normalized_job_url, tool_config=tool_config
        )
    except Exception as e:
        logger.exception("Exception occurred while fetching job info from Proxycurl.")
        return {}

    if not job_info:
        logger.debug("No job info returned from Proxycurl; skipping enrichment.")
        return {}

    # Extract organization details from the 'company' key.
    company_data = job_info.get("company", {})

    # Make sure we have a company name before proceeding
    if company_data and company_data.get("name", ""):
        result = {
            "organization_name": company_data.get("name", ""),
            "organization_linkedin_url": company_data.get("url", ""),
            # Include the website if provided
            "organization_website": company_data.get("website", "")
        }

        # Refine domain and possibly fix the website
        await set_organization_domain(result, use_strict_check, tool_config)
        return result

    return {}
