from dotenv import load_dotenv
load_dotenv(override=True)

from real_estate_agent.tools.crm import list_contacts

result = list_contacts()
print(result)

# from dotenv import load_dotenv
# import os

# load_dotenv(override=True)

# token = os.getenv("SPICY_API_TOKEN")
# print("Token:", token)
# print("Longitud:", len(token) if token else 0)