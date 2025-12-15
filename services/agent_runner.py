# Servicio para ejecutar el agente y procesar respuestas

import json
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from real_estate_agent.agent import real_estate_agent
from models.payloads import AgentResponse

APP_NAME = "real_estate_agent"

# Servicios (en producción es con persistencia real)
session_service = InMemorySessionService()

runner = Runner(
    agent=real_estate_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def get_or_create_session(phone_number: str):
    """
    Obtiene o crea una sesión para el número de teléfono.
    Mantiene el contexto de la conversación.
    """
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=phone_number,
            session_id=phone_number
        )
        if not session:
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=phone_number,
                session_id=phone_number,
                state={"user_id": phone_number}
            )
        return session
    except Exception:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=phone_number,
            session_id=phone_number,
            state={"user_id": phone_number}
        )
        return session


def parse_agent_response(response_text: str) -> AgentResponse:
    """
    Parsea la respuesta JSON del agente.
    Limpia backticks de markdown si existen.
    """
    clean_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(clean_text)
        return AgentResponse(
            message=data.get("message", response_text),
            should_escalate=data.get("should_escalate", False)
        )
    except json.JSONDecodeError:
        return AgentResponse(
            message=response_text,
            should_escalate=False
        )


async def process_message(phone_number: str, message_text: str) -> AgentResponse:
    """
    Procesa un mensaje del usuario con el agente.
    
    Args:
    phone_number: Número de teléfono del usuario
    message_text: Texto del mensaje
        
    Returns:
        AgentResponse con message y should_escalate
    """
    # Obtener o crear sesion
    await get_or_create_session(phone_number)
    
    # Preparar mensaje para el agente
    content = Content(
        role="user",
        parts=[Part(text=message_text)]
    )
    
    # Ejecutar el agente
    events = runner.run(
        user_id=phone_number,
        session_id=phone_number,
        new_message=content
    )
    # Obtener final response
    for event in events:
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text
            return parse_agent_response(response_text)
    # Si no hubo respuesta:
    return AgentResponse(
        message="Lo siento, no pude procesar tu mensaje. ¿Podrías intentar de nuevo?",
        should_escalate=False
    )