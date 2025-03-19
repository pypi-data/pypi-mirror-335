from typing import Dict, List, Optional
from pydantic import BaseModel
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.clean_properties import cleanup_email_context
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal

# --------------------------------------------
# LEAD-RELATED MODELS & FUNCTIONS (UNCHANGED)
# --------------------------------------------
class LeadResearchInformation(BaseModel):
    research_summary: str
    icp_match_score: int

@assistant_tool
async def research_lead_with_icp_ai(
    user_properties: dict, 
    icp: str, 
    instructions: str, 
    tool_config: Optional[List[Dict]] = None
):
    """
    Research on lead provided given input. Check how much it matches ICP.
    """
    instructions = f"""
    Give a deatiled research summary of the lead given the user information input.
    Make sure all the information about lead including experience, skills, education, etc. are included in the summary.   
    Have individual sections as in linkedin in like experience, education, skills, etc. 
    Have section with summary on what the current company that lead is working at does.
    Highlight how the lead matches the Ideal Customer Profile (ICP) provided.
    Research the lead based on the following information:
    {user_properties}
    
    Describe how the lead information matches the Ideal Customer Profile (ICP) provided:
    {icp}
    
    Custom insturctions for research
    {instructions}
    
    The output should be in JSON format with the following structure:
    {{
        "research_summary": "Short Summary of the research about lead. Include key insights and findings on how it matches the ICP. This value is neatly formmated Github Markdown.",
        "icp_match_score": "Score of how well the lead matches the ICP (0-5). 0 no match, 5 perfect match."
    }}
    """
    response, status = await get_structured_output_internal(
        instructions, 
        LeadResearchInformation, 
        tool_config=tool_config
    )
    return response.model_dump()

class LeadResearchInformation(BaseModel):
    research_summary: str

@assistant_tool
async def research_lead_with_full_info_ai(
    user_properties: dict, 
    instructions: str, 
    tool_config: Optional[List[Dict]] = None
):
    """
    Research on lead provided given input. Provide Detailed Summary.
    """
    user_properties = cleanup_email_context(user_properties)

    instructions = f"""
        Please read the following user information and instructions, then produce a detailed summary of the lead in the specified format.
        ---
        Lead Data:
        {user_properties}

        Instructions:
        {instructions}
        ---

        **Task**:
        Give a detailed summary of the lead based on the provided data. The summary should include the following sections (only if relevant data is present):

        1. About Lead 
        2. Experience
        3. Education
        4. Skills
        5. Recommendations
        6. Accomplishments
        7. Interests
        8. Connections
        9. Current Company Information
        10. Contact Information

        - In the **About** section, create a clear, concise description of the lead that can be used for sales prospecting.
        - In the **Current Company Information** section, summarize what the lead’s current company does. 
        - In **Current Company Information** include employee headcount, revenue, industry, HQ Location of the current company.
        - Have the above section headers even if section content is empty.
        - DO NOT include any ids, userIds or GUIDS in the output.

        **Output**:
        Return your final output as valid JSON with the following structure:
        {{
            "research_summary": "Detailed summary about lead. The summary should be neatly formatted in GitHub-Flavored Markdown, and include all the key information from the listed sections."
        }}
    """
    response, status = await get_structured_output_internal(
        instructions, 
        LeadResearchInformation, 
        model="gpt-4o-mini", 
        tool_config=tool_config
    )
    return response.model_dump()

# --------------------------------------------
# COMPANY-RELATED MODELS & FUNCTION (FIXED)
# --------------------------------------------
class CompanyResearchInformation(BaseModel):
    research_summary: str

@assistant_tool
async def research_company_with_full_info_ai(
    company_properties: dict, 
    instructions: str, 
    tool_config: Optional[List[Dict]] = None
):
    """
    Research on company provided given input. Provide a Detailed Summary.

    Parameters:
    company_properties (dict): Information about the company.
    instructions (str): Additional instructions for generating the detailed summary.
    tool_config (Optional[dict]): Configuration for the tool (default is None).

    Returns:
    dict: The JSON response containing the detailed research summary of the company.

    Raises:
    ValueError: If required parameters are missing.
    Exception: If there is an error in processing the request.
    """
    company_properties = cleanup_email_context(company_properties)

    # Build the LLM instructions for the company research
    instructions = f"""
        Please read the following company information and instructions, then produce a detailed summary of the company in the specified format.
        ---
        Company Data:
        {company_properties}

        Instructions:
        {instructions}
        ---

        **Task**:
        Give a detailed summary of the company based on the provided data. Include **firmographic details** if they are present. 
        The summary should have the following sections (only include them if there is relevant data):

        1. About Company
        2. Industry
        3. Location / HQ
        4. Employee Headcount
        5. Revenue
        6. Funding Information
        7. Additional Firmographics (e.g. markets, expansions, or any other relevant data)

        - In the **About Company** section, create a clear, concise description of what the company does (suitable for sales prospecting).
        - Do not include any IDs, userIds, or GUIDs in the output.
        Use web serach to find additional information abut the company including what it does, new and funding.

        **Output**:
        Return your final output as valid JSON with the following structure:
        {{
            "research_summary": "Detailed summary about the company. The summary should be neatly formatted in GitHub-Flavored Markdown, and include all the key information from the listed sections."
        }}
    """

    response, status = await get_structured_output_internal(
        instructions, 
        CompanyResearchInformation, 
        model="gpt-4o-mini", 
        use_web_search=True,
        tool_config=tool_config
    )
    return response.model_dump()
