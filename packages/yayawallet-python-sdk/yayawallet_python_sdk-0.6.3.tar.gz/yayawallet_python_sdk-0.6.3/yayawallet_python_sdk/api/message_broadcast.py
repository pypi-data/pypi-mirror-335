from ..functions.api_request import api_request

async def send_email(obj, api_key: str = None):
  api_response = await api_request("POST", "/email", "", obj, api_key)
  return api_response

async def send_sms(obj, api_key: str = None):
  api_response = await api_request("POST", "/sms", "", obj, api_key)
  return api_response

async def push_app_notification(obj, api_key: str = None):
  api_response = await api_request("POST", "/app-notification", "", obj, api_key)
  return api_response