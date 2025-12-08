from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest

custom_personality = None

def set_personality(personality: str):
    """Allows the user to set a custom personality."""
    global custom_personality
    custom_personality = personality


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    """Runs before sending the request to the LLM."""
    global custom_personality

    if custom_personality:
         # Inyecta la personalidad al inicio del prompt
        personality_instruction = "PERSONALITY: " + custom_personality + "\n\n"
        
        # Agrega al system instruction existente
        if llm_request.config and llm_request.config.system_instruction:
            llm_request.config.system_instruction = personality_instruction + llm_request.config.system_instruction
    
    return None  # None = continuar normalmente