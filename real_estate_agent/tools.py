import requests

def detectar_ubicacion() -> dict:
    """Detecta el país del usuario basándose en su IP."""
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        data = response.json()
        return {
            "statuts": "success",
            "pais": data.get("country_name", "Desconocido"),
            "ciudad": data.get("city", "Desconocida")
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": "No se pudo detectar ubicación: " + str(e)
        }