import base64
import datetime
from typing import Any, Dict, List, Optional
import aiohttp
from pydantic import BaseModel

from dhisana.schemas.sales import (
    ContentGenerationContext,
    MessageItem,
    MessageResponse,
    MessageGenerationInstructions
)
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.generate_structured_output_internal import (
    get_structured_output_with_assistant_and_vector_store,
    get_structured_output_internal
)

# ---------------------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------------------
class InboundEmailTriageResponse(BaseModel):
    """
    Model representing the structured response for an inbound email triage.
    - triage_status: "AUTOMATIC" or "REQUIRES_APPROVAL"
    - triage_reason: Reason text if triage_status == "REQUIRES_APPROVAL"
    - response_action_to_take: The recommended next action (e.g. SCHEDULE_MEETING, SEND_REPLY, etc.)
    - response_message: The actual body of the email response to be sent or used for approval.
    """
    triage_status: str  # "AUTOMATIC" or "REQUIRES_APPROVAL"
    triage_reason: Optional[str]
    response_action_to_take: str
    response_message: str


# ---------------------------------------------------------------------------------------
# HELPER FUNCTION TO CLEAN CONTEXT
# ---------------------------------------------------------------------------------------
def cleanup_reply_campaign_context(campaign_context: ContentGenerationContext) -> ContentGenerationContext:
    clone_context = campaign_context.copy(deep=True)
    clone_context.lead_info.task_ids = None
    clone_context.lead_info.email_validation_status = None
    clone_context.lead_info.linkedin_validation_status = None
    clone_context.lead_info.research_status = None
    clone_context.lead_info.enchrichment_status = None
    return clone_context


# ---------------------------------------------------------------------------------------
# CORE FUNCTION TO GENERATE SINGLE RESPONSE (ONE VARIATION)
# ---------------------------------------------------------------------------------------
async def generate_inbound_email_response_copy(
    campaign_context: ContentGenerationContext,
    variation: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Generate a single inbound email triage response based on the provided context and
    a specific variation prompt.
    """
    allowed_actions = [
        "SCHEDULE_MEETING",
        "SEND_REPLY",
        "UNSUBSCRIBE",
        "OOF_MESSAGE",
        "NOT_INTERESTED",
        "NEED_MORE_INFO",
        "FORWARD_TO_OTHER_USER",
        "NO_MORE_IN_ORGANIZATION",
        "OBJECTION_RAISED",
        "OTHER"
    ]
    current_date_iso = datetime.datetime.now().isoformat()
    cleaned_context = cleanup_reply_campaign_context(campaign_context)
    if not cleaned_context.current_conversation_context.current_email_thread:
        cleaned_context.current_conversation_context.current_email_thread = []

    prompt = f"""
    You are a specialized email assistant. 
    Your task is to analyze the user's email thread, the user/company info,
    and the provided triage guidelines to craft a response.

    Follow these instructions to generate the reply: 
    {variation}

    1. Understand the email thread or conversation to respond to:
       {[thread_item.model_dump() for thread_item in cleaned_context.current_conversation_context.current_email_thread] if cleaned_context.current_conversation_context.current_email_thread else []}

    2. User & Company (Lead) Info:
       {cleaned_context.model_dump()}

    3. Triage Guidelines:
       {cleaned_context.campaign_context.email_triage_guidelines}

       - If the request is standard, simple, or obviously handled by standard processes,
         set triage_status to "AUTOMATIC".
       - If the request is complex, sensitive, or needs special input,
         set triage_status to "REQUIRES_APPROVAL" and provide triage_reason.

    4. Choose one action from this list: {allowed_actions}

    5. Provide your recommended email body that best addresses the user's message.
    DO NOT reply to any PII or financial information requests; triage them as "REQUIRES_APPROVAL".
    DO NOT replay anything negative about my product or company {campaign_context.lead_info.organization_name}; triage them as "REQUIRES_APPROVAL".
    current date is : {current_date_iso}
    DO NOT share any link to internal or made up doucment. You can attach or send any document.
    If the user is asking for any document point them to organization's website found in sender information if available:
    {campaign_context.sender_info.model_dump()} 

    Your final output must be valid JSON with the structure:
    {{
      "triage_status": "AUTOMATIC" or "REQUIRES_APPROVAL",
      "triage_reason": "<reason if requires approval; otherwise null>",
      "response_action_to_take": "<chosen action>",
      "response_message": "<the email body to respond with>"
    }}
    """

    # If there's a vector store ID, use that approach
    if (
        cleaned_context.external_known_data
        and cleaned_context.external_known_data.external_openai_vector_store_id
    ):
        initial_response, status = await get_structured_output_with_assistant_and_vector_store(
            prompt=prompt,
            response_format=InboundEmailTriageResponse,
            vector_store_id=cleaned_context.external_known_data.external_openai_vector_store_id,
            tool_config=tool_config
        )
    else:
        initial_response, status = await get_structured_output_internal(
            prompt=prompt,
            response_format=InboundEmailTriageResponse,
            tool_config=tool_config
        )

    if status != "SUCCESS":
        raise Exception("Error in generating the inbound email triage response.")

    response_item = MessageItem(
        message_id="",  # or generate one if appropriate
        sender_name=campaign_context.sender_info.sender_full_name or "",
        sender_email=campaign_context.sender_info.sender_email or "",
        receiver_name=campaign_context.lead_info.full_name or "",
        receiver_email=campaign_context.lead_info.email or "",
        iso_datetime=datetime.datetime.utcnow().isoformat(),
        subject="",  # or set some triage subject if needed
        body=initial_response.response_message
    )

    # Build a MessageResponse that includes triage metadata plus your message item
    response_message = MessageResponse(
        triage_status=initial_response.triage_status,
        triage_reason=initial_response.triage_reason,
        message_item=response_item,
        response_action_to_take=initial_response.response_action_to_take
    )
    return response_message.model_dump()


# ---------------------------------------------------------------------------------------
# MAIN ENTRY POINT - GENERATE MULTIPLE VARIATIONS
# ---------------------------------------------------------------------------------------
@assistant_tool
async def generate_inbound_email_response_variations(
    campaign_context: ContentGenerationContext,
    number_of_variations: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Generate multiple inbound email triage responses, each with a different 'variation'
    unless user instructions are provided. Returns a list of dictionaries conforming
    to InboundEmailTriageResponse.
    """
    # Default variation frameworks
    variation_specs = [
        "Short and friendly response focusing on quick resolution.",
        "More formal tone referencing user’s key points in the thread.",
        "Meeting-based approach if user needs further discussion or demo.",
        "Lean approach focusing on clarifying user’s questions or concerns.",
        "Solution-driven approach referencing a relevant product or case study."
    ]

    # Check if the user provided custom instructions
    message_instructions = campaign_context.message_instructions or MessageGenerationInstructions()
    user_instructions = (message_instructions.instructions_to_generate_message or "").strip()
    user_instructions_exist = bool(user_instructions)

    all_variations = []
    for i in range(number_of_variations):
        # If user instructions exist, use them for every variation
        if user_instructions_exist:
            variation_text = user_instructions
        else:
            # Otherwise, fallback to variation_specs
            variation_text = variation_specs[i % len(variation_specs)]

        try:
            triaged_response = await generate_inbound_email_response_copy(
                campaign_context=campaign_context,
                variation=variation_text,
                tool_config=tool_config
            )
            all_variations.append(triaged_response)
        except Exception as e:
            raise e

    return all_variations
