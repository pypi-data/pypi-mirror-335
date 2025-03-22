import asyncio
import json
import logging
import os
import aiohttp
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import retrieve_output, cache_output
import backoff


# This is google Custom Search API (Not SERP API)
# We use SERP API currently has it handles spell corrections etc correctly.
# TODO: Enhance Custom search to handle corner cases. Its much lower cost than SERP API.

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=60,
)
async def search_google_custom(
    query: str,
    number_of_results: int = 10
):
    """
    Search Google using the Google Custom Search JSON API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - **query** (*str*): The search query.
    - **number_of_results** (*int*): The number of results to return.
    """

    API_KEY = os.environ.get('GOOGLE_SEARCH_KEY')
    CX = os.environ.get('GOOGLE_SEARCH_CX')  # Custom Search Engine ID
    if not API_KEY or not CX:
        return {'error': "Google Custom Search API key or CX not found in environment variables"}

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": number_of_results
    }

    try:
        cached_response = retrieve_output("search_google_custom", query)
        if cached_response is not None:
            return cached_response
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    serialized_results = []
                    
                    # Check for spelling corrections in the response
                    if "spelling" in result and "correctedQuery" in result["spelling"]:
                        corrected_query = result["spelling"]["correctedQuery"]
                        logging.warning(f"Spelling suggestion detected: {corrected_query}. Retrying with original query.")

                        # Re-run query using original terms
                        params["q"] = query  # Explicitly force the original query
                        params["spell"] = query
                        async with session.get(url, params=params) as retry_response:
                            if retry_response.status == 200:
                                retry_result = await retry_response.json()
                                serialized_results = [json.dumps(item) for item in retry_result.get('items', [])]
                    else:
                        serialized_results = [json.dumps(item) for item in result.get('items', [])]
                    cached_response = cache_output("search_google_custom", query, serialized_results)
                    await asyncio.sleep(1)  # Wait for 3 seconds before sending the response
                    return serialized_results
                elif response.status == 429:
                    logging.warning("search_google_custom Rate limit hit")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message="Rate limit exceeded",
                        headers=response.headers
                    )
                else:
                    result = await response.json()
                    logging.warning(f"search_google_custom Failed to run assistant: {result}")
                    return {'error': result}                       
    except aiohttp.ClientResponseError as e:
        raise  # Allow backoff to handle this exception
    except Exception as e:
        return {'error': str(e)}

@assistant_tool
async def search_google_places(
    query: str,
    location_bias: dict = None,
    number_of_results: int = 3
):
    """
    Search Google Places API (New) and return the results as an array of serialized JSON strings.

    Parameters:
    - **query** (*str*): The search query.
    - **location_bias** (*dict*): Optional. A dictionary with 'latitude', 'longitude', and 'radius' (in meters) to bias the search.
    - **number_of_results** (*int*): The number of results to return.
    """
    GOOGLE_SEARCH_KEY = os.environ.get('GOOGLE_SEARCH_KEY')
    if not GOOGLE_SEARCH_KEY:
        return {'error': "Google Places API key not found in environment variables"}

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_SEARCH_KEY,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.websiteUri,places.rating,places.reviews'
    }

    request_body = {
        "textQuery": query
    }

    if location_bias:
        request_body["locationBias"] = {
            "circle": {
                "center": {
                    "latitude": location_bias.get("latitude"),
                    "longitude": location_bias.get("longitude")
                },
                "radius": location_bias.get("radius", 5000)  # Default to 5 km if radius not provided
            }
        }

    # Create a cache key that includes query, number_of_results, and location_bias
    location_bias_str = json.dumps(location_bias, sort_keys=True) if location_bias else "None"
    cache_key = f"{query}:{number_of_results}:{location_bias_str}"
    cached_response = retrieve_output("search_google_places", cache_key)
    if cached_response is not None:
        return cached_response

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=request_body) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result.get('error', {}).get('message', 'Unknown error')}

                # Extract the required number of results
                places = result.get('places', [])[:number_of_results]

                # Serialize each place result to JSON string
                serialized_results = [json.dumps(place) for place in places]

                # Cache the response
                cache_output("search_google_places", cache_key, serialized_results)

                return serialized_results
    except Exception as e:
        return {'error': str(e)}

