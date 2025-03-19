import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import urllib

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.web_download_parse_tools import fetch_html_content, get_html_content_from_url

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_serp_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the SERPAPI_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The SERPAPI_KEY access token.

    Raises:
        ValueError: If the access token is not found in the tool configuration or environment variable.
    """
    logger.info("Entering get_serp_api_access_token")
    SERPAPI_KEY = None

    if tool_config:
        logger.debug(f"Tool config provided: {tool_config}")
        serpapi_config = next(
            (item for item in tool_config if item.get("name") == "serpapi"), None
        )
        if serpapi_config:
            config_map = {
                item["name"]: item["value"]
                for item in serpapi_config.get("configuration", [])
                if item
            }
            SERPAPI_KEY = config_map.get("apiKey")
        else:
            logger.warning("No 'serpapi' config item found in tool_config.")
    else:
        logger.debug("No tool_config provided or it's None.")

    SERPAPI_KEY = SERPAPI_KEY or os.getenv("SERPAPI_KEY")
    if not SERPAPI_KEY:
        logger.error("SERPAPI_KEY not found in configuration or environment.")
        raise ValueError("SERPAPI_KEY access token not found in tool_config or environment variable")

    logger.info("Retrieved SERPAPI_KEY successfully.")
    return SERPAPI_KEY


@assistant_tool
async def search_google(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,  
    tool_config: Optional[List[Dict]] = None,
    as_oq: Optional[str] = None  # <-- NEW PARAM for optional keywords
) -> List[str]:
    """
    Search Google using SERP API, supporting pagination and an explicit 'offset'
    parameter to start from a specific result index. 
    Now also supports 'as_oq' for optional query terms in SERP API.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The total number of results to return. Default is 10.
    - offset (int): The starting index for the first result returned (Google pagination).
    - tool_config (Optional[List[Dict]]): Configuration containing SERP API token, etc.
    - as_oq (Optional[str]): Optional query terms for SerpAPI (if supported).
    
    Returns:
    - List[str]: A list of organic search results, each serialized as a JSON string.
    """
    logger.info("Entering search_google")
    if not query:
        logger.warning("Empty query string provided.")
        return []

    # Use 'as_oq' in the cache key too, so different optional terms don't conflict
    cache_key = f"{query}_{number_of_results}_{offset}_{as_oq or ''}"
    cached_response = retrieve_output("search_google_serp", cache_key)
    if cached_response is not None:
        logger.info("Cache hit for search_google.")
        return cached_response

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    url = "https://serpapi.com/search"

    page_size = 100
    all_results: List[Dict[str, Any]] = []
    start_index = offset

    logger.debug(f"Requesting up to {number_of_results} results for '{query}' starting at offset {offset}.")

    async with aiohttp.ClientSession() as session:
        while len(all_results) < number_of_results:
            to_fetch = min(page_size, number_of_results - len(all_results))
            params = {
                "q": query,
                "num": to_fetch,
                "start": start_index,
                "api_key": SERPAPI_KEY,
                "location": "United States"
            }

            # If we have optional terms, add them
            if as_oq:
                params["as_oq"] = as_oq

            logger.debug(f"SERP API GET request with params: {params}")

            try:
                async with session.get(url, params=params) as response:
                    logger.debug(f"Received response status: {response.status}")
                    if response.status != 200:
                        try:
                            error_content = await response.json()
                        except Exception:
                            error_content = await response.text()
                        logger.warning(f"Non-200 response from SERP API: {error_content}")
                        return [json.dumps({"error": error_content})]

                    result = await response.json()
            except Exception as e:
                logger.exception("Exception during SERP API request.")
                return [json.dumps({"error": str(e)})]

            organic_results = result.get('organic_results', [])
            if not organic_results:
                logger.debug("No more organic results returned; stopping.")
                break

            all_results.extend(organic_results)
            start_index += to_fetch

            if len(all_results) >= number_of_results:
                break

    all_results = all_results[:number_of_results]
    logger.info(f"Found {len(all_results)} results for query '{query}'.")

    serialized_results = [json.dumps(item) for item in all_results]
    cache_output("search_google_serp", cache_key, serialized_results)
    return serialized_results


@assistant_tool
async def search_google_maps(
    query: str,
    number_of_results: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google Maps using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_maps")
    if not query:
        logger.warning("Empty query string provided for search_google_maps.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_maps"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Maps with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('local_results', [])]
                logger.info(f"Returning {len(serialized_results)} map results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_maps request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_google_news(
    query: str,
    number_of_results: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google News using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_news")
    if not query:
        logger.warning("Empty query string provided for search_google_news.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_news"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google News with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('news_results', [])]
                logger.info(f"Returning {len(serialized_results)} news results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_news request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_job_postings(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search for job postings using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_job_postings")
    if not query:
        logger.warning("Empty query string provided for search_job_postings.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_jobs"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Jobs with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('jobs_results', [])]
                logger.info(f"Returning {len(serialized_results)} job posting results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_job_postings request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_google_images(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google Images using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_images")
    if not query:
        logger.warning("Empty query string provided for search_google_images.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_images"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Images with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('images_results', [])]
                logger.info(f"Returning {len(serialized_results)} image results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_images request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_google_videos(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google Videos using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_videos")
    if not query:
        logger.warning("Empty query string provided for search_google_videos.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_videos"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Videos with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('video_results', [])]
                logger.info(f"Returning {len(serialized_results)} video results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_videos request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def get_company_domain_from_google_search(
    company_name: str,
    location: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Tries to find the company domain from the company name using Google search.

    Args:
        company_name (str): The name of the company to search for.
        location (str, optional): A location to include in the query.

    Returns:
        str: The domain of the company's official website if found, otherwise an empty string.
    """
    logger.info("Entering get_company_domain_from_google_search")

    company_name_no_spaces = company_name.replace(" ", "")
    if not company_name_no_spaces or company_name.lower() in ["none", "freelance"]:
        logger.debug("Invalid or excluded company_name provided.")
        return ""

    exclude_company_names = ["linkedin", "wikipedia", "facebook", "instagram", "twitter", "youtube", "netflix", "zoominfo", "reditt"]
    query = f"\"{company_name}\" official website"
    if location:
        query = f"\"{company_name}\" official website, {location}"

    try:
        logger.debug(f"Performing search with query: {query}")
        result = await search_google(query, 1, tool_config=tool_config)
        if not isinstance(result, list) or len(result) == 0:
            logger.debug("No results for first attempt, retrying with fallback query.")
            query = f"{company_name} official website"
            result = await search_google(query, 1, tool_config=tool_config)
            if not isinstance(result, list) or len(result) == 0:
                logger.debug("No results from fallback query either.")
                return ''
    except Exception as e:
        logger.exception("Exception during get_company_domain_from_google_search.")
        return ''

    exclude_compan_names = ["linkedin", "wikipedia", "facebook", "instagram", "twitter", "youtube", "netflix"]
    if any(exclude_name in company_name.lower() for exclude_name in exclude_compan_names):
        logger.debug("Company name is in excluded list, returning empty domain.")
        return ""

    try:
        result_json = json.loads(result[0])
    except (json.JSONDecodeError, IndexError) as e:
        logger.debug(f"Failed to parse the JSON from the result: {str(e)}")
        return ''

    link = result_json.get('link', '')
    if not link:
        logger.debug("No link found in the first search result.")
        return ''

    parsed_url = urlparse(link)
    domain = parsed_url.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]

    excluded_domains = [
        "linkedin.com", "wikipedia.org", "usa.gov", "facebook.com",
        "instagram.com", "twitter.com", "x.com", "google.com", "youtube.com",
        "netflix.com", "freelance.com", "zoominfo.com", "reditt.com"
    ]
    excluded_domains_lower = [d.lower() for d in excluded_domains]

    if any(domain == d or domain.endswith(f".{d}") for d in excluded_domains_lower):
        logger.debug(f"Domain {domain} is in the excluded list.")
        return ""

    logger.info(f"Found domain {domain}")
    return domain


@assistant_tool
async def get_signal_strength(
    domain_to_search: str,
    keywords: List[str],
    in_title: List[str] = [],
    not_in_title: List[str] = [],
    negative_keywords: List[str] = [],
    tool_config: Optional[List[Dict]] = None
) -> int:
    """
    Find how strong a match for the keywords in search is by checking
    how many search results contain all desired keywords in the snippet.

    Args:
        domain_to_search (str): The domain to search inside.
        keywords (List[str]): The keywords to search for.
        in_title (List[str]): Keywords that must appear in the title.
        not_in_title (List[str]): Keywords that must not appear in the title.
        negative_keywords (List[str]): Keywords to exclude from results.

    Returns:
        int: A strength score on a scale of 0 to 5.
    """
    logger.info("Entering get_signal_strength")

    if not keywords and not domain_to_search:
        logger.warning("No domain to search or keywords provided.")
        return 0

    query_parts = []
    if domain_to_search:
        query_parts.append(f"site:{domain_to_search}")
    for kw in keywords:
        query_parts.append(f"\"{kw}\"")
    for kw in in_title:
        query_parts.append(f'intitle:"{kw}"')
    for kw in not_in_title:
        query_parts.append(f'-intitle:"{kw}"')
    for kw in negative_keywords:
        query_parts.append(f'-"{kw}"')

    final_query = " ".join(query_parts).strip()
    if not final_query:
        logger.debug("Constructed query is empty, returning score=0.")
        return 0

    logger.debug(f"Performing get_signal_strength search with query: {final_query}")
    try:
        results = await search_google(final_query, 5, tool_config=tool_config)
    except Exception as e:
        logger.exception("Exception occurred while searching for signal strength.")
        return 0

    if not isinstance(results, list) or len(results) == 0:
        logger.debug("No results found; returning 0.")
        return 0

    score = 0
    for result in results:
        try:
            result_json = json.loads(result)
            snippet_text = result_json.get('snippet', '').lower()
            if all(kw.lower() in snippet_text for kw in keywords):
                logger.debug(f"Found match in snippet: {snippet_text[:60]}...")
                score += 1
            if score == 5:
                break
        except (json.JSONDecodeError, KeyError):
            logger.debug("Failed to decode or parse snippet from a result.")
            continue

    logger.info(f"Final signal strength score: {score}")
    return score


def extract_user_linkedin_page(url: str) -> str:
    """
    Extracts and returns the user page part of a LinkedIn URL.
    Ensures the domain is www.linkedin.com and removes any suffix path or query parameters.
    """
    logger.debug(f"Entering extract_user_linkedin_page with URL: {url}")
    if not url:
        return ""

    normalized_url = re.sub(r"(https?://)?([\w\-]+\.)?linkedin\.com", "https://www.linkedin.com", url)
    match = re.match(r"https://www.linkedin.com/in/([\w\-]+)", normalized_url)
    if match:
        page = f"https://www.linkedin.com/in/{match.group(1)}"
        logger.debug(f"Extracted user LinkedIn page: {page}")
        return page

    logger.debug("No valid LinkedIn user page found.")
    return ""


@assistant_tool
async def find_user_linkedin_url_google(
    user_name: str,
    user_title: str,
    user_location: str,
    user_company: str,
    user_company_domain: str = "",
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Find the LinkedIn URL for a user based on their name, title, location, and company.

    Args:
        user_name (str): The name of the user.
        user_title (str): The title of the user.
        user_location (str): The location of the user.
        user_company (str): The company of the user.
        use_strict_check (bool): Whether to use a strict single query or a series of relaxed queries.

    Returns:
        str: The LinkedIn URL if found, otherwise an empty string.
    """
    logger.info("Entering find_user_linkedin_url_google")

    if not user_name:
        logger.warning("No user_name provided.")
        return ""

    if use_strict_check:
        queries = [
            f'site:linkedin.com/in ("{user_name}" at company "{user_company}" | {user_company_domain}) ( "{user_title}" | ) intitle:"{user_name}" -intitle:"profiles" '
        ]
    else:
        queries = [
            f'site:linkedin.com/in "{user_name}" "{user_location}" "{user_title}" "{user_company}" intitle:"{user_name}" -intitle:"profiles" ',
            f'site:linkedin.com/in "{user_name}" "{user_location}" "{user_company}" intitle:"{user_name}" -intitle:"profiles" ',
            f'site:linkedin.com/in "{user_name}", {user_location} intitle:"{user_name}" -intitle:"profiles" ',
            f'site:linkedin.com/in "{user_name}" intitle:"{user_name}"'
        ]

    async with aiohttp.ClientSession() as session:  # Not strictly necessary here, but kept for parallel structure
        for query in queries:
            if not query.strip():
                continue
            logger.debug(f"Searching with query: {query}")
            try:
                results = await search_google(query.strip(), 1, tool_config=tool_config)
            except Exception as e:
                logger.exception("Error searching for LinkedIn user URL.")
                continue

            if not isinstance(results, list) or len(results) == 0:
                logger.debug("No results for this query, moving to next.")
                continue

            try:
                result_json = json.loads(results[0])
            except (json.JSONDecodeError, IndexError):
                logger.debug("Failed to parse JSON from the search result.")
                continue

            link = result_json.get('link', '')
            if not link:
                logger.debug("No link in first search result.")
                continue

            parsed_url = urlparse(link)
            if 'linkedin.com/in' in (parsed_url.netloc + parsed_url.path):
                link = extract_user_linkedin_page(link)
                logger.info(f"Found LinkedIn user page: {link}")
                return link

    logger.info("No matching LinkedIn user page found.")
    return ""


@assistant_tool
async def find_user_linkedin_url_by_job_title_google(
    user_title: str,
    user_location: str,
    user_company: str,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Find the LinkedIn URL for a user based on their job_title, location, and company.

    Args:
        user_title (str): The title of the user.
        user_location (str): The location of the user.
        user_company (str): The company of the user.

    Returns:
        str: The LinkedIn URL if found, otherwise an empty string.
    """
    logger.info("Entering find_user_linkedin_url_by_job_title_google")

    queries = [
        f'site:linkedin.com/in "{user_company}" AND "{user_title}" -intitle:"profiles" ',
    ]

    async with aiohttp.ClientSession() as session:  
        for query in queries:
            if not query.strip():
                continue
            logger.debug(f"Searching with query: {query}")

            try:
                results = await search_google(query.strip(), 1, tool_config=tool_config)
            except Exception as e:
                logger.exception("Error searching for LinkedIn URL by job title.")
                continue

            if not isinstance(results, list) or len(results) == 0:
                logger.debug("No results for this query, moving to next.")
                continue

            try:
                result_json = json.loads(results[0])
            except (json.JSONDecodeError, IndexError):
                logger.debug("Failed to parse JSON from the search result.")
                continue

            link = result_json.get('link', '')
            if not link:
                logger.debug("No link in the first search result.")
                continue

            parsed_url = urlparse(link)
            if 'linkedin.com/in' in (parsed_url.netloc + parsed_url.path):
                link = extract_user_linkedin_page(link)
                logger.info(f"Found LinkedIn user page by job title: {link}")
                return link

    logger.info("No matching LinkedIn user page found by job title.")
    return ""


@assistant_tool
async def find_user_linkedin_url_by_google_search(
    queries: List[str],
    number_of_results: int = 5,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Find LinkedIn user URLs based on provided Google search queries.
    
    Args:
        queries (List[str]): A list of Google search queries.
        number_of_results (int): Number of results to return from each query (default is 5).
        tool_config (Optional[List[Dict]]): Optional configuration for the SERP API.

    Returns:
        List[str]: A list of matching LinkedIn user URLs found, or an empty list if none.
    """
    logger.info("Entering find_user_linkedin_url_by_google_search")
    found_urls = []

    for query in queries:
        if not query.strip():
            continue
        logger.debug(f"Searching with query: {query}")

        try:
            results = await search_google(query.strip(), number_of_results, tool_config=tool_config)
        except Exception as e:
            logger.exception("Error searching for LinkedIn URL using Google search.")
            continue

        if not isinstance(results, list) or len(results) == 0:
            logger.debug("No results for this query, moving to next.")
            continue

        try:
            result_json = json.loads(results[0])
        except (json.JSONDecodeError, IndexError):
            logger.debug("Failed to parse JSON from the search result.")
            continue

        link = result_json.get('link', '')
        if not link:
            logger.debug("No link in the first search result.")
            continue

        parsed_url = urlparse(link)
        if 'linkedin.com/in' in (parsed_url.netloc + parsed_url.path):
            link = extract_user_linkedin_page(link)
            logger.info(f"Found LinkedIn user page: {link}")
            found_urls.append(link)

    if not found_urls:
        logger.info("No matching LinkedIn user page found based on provided queries.")
    return found_urls


def extract_company_page(url: str) -> str:
    """
    Extracts and returns the company page part of a LinkedIn URL.
    Ensures the domain is www.linkedin.com and removes any suffix path or query parameters.
    """
    logger.debug(f"Entering extract_company_page with URL: {url}")
    if not url:
        return ""

    normalized_url = re.sub(r"(https?://)?([\w\-]+\.)?linkedin\.com", "https://www.linkedin.com", url)
    match = re.match(r"https://www.linkedin.com/company/([\w\-]+)", normalized_url)
    if match:
        company_page = f"https://www.linkedin.com/company/{match.group(1)}"
        logger.debug(f"Extracted LinkedIn company page: {company_page}")
        return company_page

    logger.debug("No valid LinkedIn company page found.")
    return ""


@assistant_tool
async def find_organization_linkedin_url_with_google_search(
    company_name: str,
    company_location: Optional[str] = None,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict]] = None,
) -> str:
    """
    Find the LinkedIn URL for a company based on its name and optional location using Google search.

    Args:
        company_name (str): The name of the company.
        company_location (str, optional): The location of the company.
        use_strict_check (bool): Whether to use stricter or multiple queries.

    Returns:
        str: The LinkedIn URL if found, otherwise an empty string.
    """
    logger.info("Entering find_organization_linkedin_url_with_google_search")

    if not company_name:
        logger.warning("No company_name provided.")
        return ""

    if use_strict_check:
        queries = [f'site:linkedin.com/company "{company_name}" {company_location} -intitle:"jobs" ']
    else:
        if company_location:
            queries = [
                f'site:linkedin.com/company "{company_name}" {company_location} -intitle:"jobs" ',
                f'site:linkedin.com/company "{company_name}" -intitle:"jobs" ',
                f'site:linkedin.com/company {company_name} {company_location} -intitle:"jobs" ',
            ]
        else:
            queries = [
                f'site:linkedin.com/company "{company_name}" -intitle:"jobs" ',
                f'site:linkedin.com/company {company_name} -intitle:"jobs" '
            ]

    async with aiohttp.ClientSession() as session:
        for query in queries:
            if not query.strip():
                continue

            logger.debug(f"Searching with query: {query}")
            try:
                results = await search_google(query.strip(), 1, tool_config=tool_config)
            except Exception as e:
                logger.exception("Error searching for organization LinkedIn URL.")
                continue

            if not isinstance(results, list) or len(results) == 0:
                logger.debug("No results for this query, moving to next.")
                continue

            try:
                result_json = json.loads(results[0])
            except (json.JSONDecodeError, IndexError):
                logger.debug("Failed to parse JSON from the search result.")
                continue

            link = result_json.get('link', '')
            if not link:
                logger.debug("No link found in the first result.")
                continue

            parsed_url = urlparse(link)
            if 'linkedin.com/company' in (parsed_url.netloc + parsed_url.path):
                link = extract_company_page(link)
                logger.info(f"Found LinkedIn company page: {link}")
                return link

    logger.info("No matching LinkedIn company page found.")
    return ""


async def get_external_links(url: str) -> List[str]:
    """
    Fetch external links from a given URL by parsing its HTML content.
    """
    logger.debug(f"Entering get_external_links for URL: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True) as response:
                logger.debug(f"Received status for external links: {response.status}")
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    external_links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('http') and not href.startswith(url):
                            external_links.append(href)
                    logger.debug(f"Found {len(external_links)} external links.")
                    return external_links
                else:
                    logger.warning(f"Non-200 status ({response.status}) while fetching external links.")
                    return []
    except Exception as e:
        logger.exception("Exception occurred while fetching external links.")
        return []


async def get_resolved_linkedin_links(url: str) -> List[str]:
    """
    Fetch HTML content from a URL and return any LinkedIn.com/company links found.
    """
    logger.debug(f"Entering get_resolved_linkedin_links for URL: {url}")
    try:
        content = await fetch_html_content(url)
    except Exception as e:
        logger.exception("Exception occurred while fetching HTML content.")
        return []

    linkedin_links = re.findall(r'https://www\.linkedin\.com/company/[^\s]+', content)
    unique_links = list(set(linkedin_links))
    logger.debug(f"Found {len(unique_links)} LinkedIn links.")
    return unique_links


@assistant_tool
async def get_company_website_from_linkedin_url(linkedin_url: str) -> str:
    """
    Attempt to extract a company's website from its LinkedIn URL by 
    scanning external links that contain "trk=about_website".
    """
    logger.info("Entering get_company_website_from_linkedin_url")

    if not linkedin_url:
        logger.debug("Empty LinkedIn URL provided, returning empty string.")
        return ""

    try:
        links = await get_external_links(linkedin_url)
    except Exception as e:
        logger.exception("Exception occurred while getting external links for LinkedIn URL.")
        return ""

    for link in links:
        if 'trk=about_website' in link:
            parsed_link = urllib.parse.urlparse(link)
            query_params = urllib.parse.parse_qs(parsed_link.query)
            if 'url' in query_params:
                encoded_url = query_params['url'][0]
                company_website = urllib.parse.unquote(encoded_url)
                logger.info(f"Extracted company website: {company_website}")
                return company_website
    logger.debug("No company website link found with 'trk=about_website'.")
    return ""
