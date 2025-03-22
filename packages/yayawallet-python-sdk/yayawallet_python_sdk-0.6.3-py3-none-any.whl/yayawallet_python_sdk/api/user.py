from ..functions.api_request import api_request

from rest_framework import status

from django.http import StreamingHttpResponse

from ..serializers.user_serializers import CustomerUserSerializer, BusinessUserSerializer

import json

from typing import Optional

async def get_organization(api_key = None):
  api_response = await api_request("GET", "/user/organization", "", None, api_key)
  return api_response

async def get_profile(api_key = None):
  api_response = await api_request("GET", "/user/profile", "", None, api_key)
  return api_response

async def search_profile(account_name: str, api_key: str = None):
  api_response = await api_request("POST", "/user/profile", "", { "account_name": account_name }, api_key)
  return api_response

async def search_user(query: str, api_key: str = None):
  api_response = await api_request("POST", "/user/search", "", { "query": query }, api_key)
  return api_response

async def get_balance(api_key: str = None):
  api_response = await api_request("GET", "/user/balance", "", None, api_key)
  return api_response

async def create_customer_user(data, api_key = None):
  serializer = CustomerUserSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/user/register", "", validated_data, api_key)
      return api_response
  else:
      errors = serializer.errors
      json_errors = json.dumps(errors)

      def error_generator():
          yield json_errors

      return StreamingHttpResponse(
        error_generator(),
        content_type='application/json',
        status=status.HTTP_400_BAD_REQUEST,
      )

async def create_business_user(data, api_key = None):
  serializer = BusinessUserSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/user/register-business", "", validated_data, api_key)
      return api_response
  else:
      errors = serializer.errors
      json_errors = json.dumps(errors)

      def error_generator():
          yield json_errors

      return StreamingHttpResponse(
        error_generator(),
        content_type='application/json',
        status=status.HTTP_400_BAD_REQUEST,
      )

async def update_user(
      account_name: Optional[str] = None,
      name: Optional[str] = None,
      gender: Optional[str] = None,
      region: Optional[str] = None,
      location: Optional[str] = None,
      date_of_birth: Optional[str] = None,
      notes: Optional[str] = None,
      photo_base64: Optional[str] = None,
      id_front_base64: Optional[str] = None,
      id_back_base64: Optional[str] = None,
      sms_notification_enable: Optional[bool] = None,
      email_notification_enable: Optional[bool] = None,
      app_notification_enable: Optional[bool] = None,
      block_incoming_transfer: Optional[bool] = None,
      block_outgoing_transfer: Optional[bool] = None,
      block_incoming_transaction: Optional[bool] = None,
      block_outgoing_transaction: Optional[bool] = None,
      tin_doc_base64: Optional[str] = None,
      trade_license_doc_base64: Optional[str] = None,
      aoa_doc_base64: Optional[str] = None,
      moa_doc_base64: Optional[str] = None,
      meta_data: Optional[str] = None,
      api_key: str = None
  ):
  payload = {
    **{
      key: value for key, value in {
        "account_name": account_name,
        "name": name,
        "gender": gender,
        "region": region,
        "location": location,
        "date_of_birth": date_of_birth,
        "notes": notes,
        'photo_base64': photo_base64,
        'id_front_base64': id_front_base64,
        'id_back_base64': id_back_base64,
        "sms_notification_enable": sms_notification_enable,
        "email_notification_enable": email_notification_enable,
        "app_notification_enable": app_notification_enable,
        "block_incoming_transfer": block_incoming_transfer,
        "block_outgoing_transfer": block_outgoing_transfer,
        "block_incoming_transaction": block_incoming_transaction,
        "block_outgoing_transaction": block_outgoing_transaction,
        "tin_doc_base64": tin_doc_base64,
        "trade_license_doc_base64": trade_license_doc_base64,
        "aoa_doc_base64": aoa_doc_base64,
        "moa_doc_base64": moa_doc_base64,
        "meta_data": meta_data
      }.items() if value is not None
    }
  }
  api_response = await api_request("POST", "/user/update", "", payload, api_key)
  return api_response

async def document_actions(action: str, document: str, account_name: str, meta_data: Optional[str] = None, api_key: str = None):
  api_response = await api_request("POST", f"/user/documents/{action}/{document}", "", { "account_name": account_name, "meta_data": meta_data  }, api_key)
  return api_response

async def send_new_pin(account_name: str, meta_data: Optional[str] = None, api_key: str = None):
  api_response = await api_request("POST", "/user/send-new-pin", "", { "account_name": account_name, "meta_data": meta_data }, api_key)
  return api_response

async def pending_approval(account_type: str, api_key: str = None):
  api_response = await api_request("POST", f"/user/pending-approval/{account_type}", "", None, api_key)
  return api_response

async def get_otp(country: str, phone: str, api_key = None):
  api_response = await api_request("POST", "/user/otp", "", {"country": country,"phone": phone}, api_key)
  return api_response


async def verify_otp(phone: str, otp: str, api_key: str = None):
    """
    Verify the OTP sent to the user's phone.

    :param phone: The phone number to verify.
    :param otp: The OTP code to verify.
    :param api_key: The API key for authentication (optional).
    :return: The API response.
    """
    payload = {
        "int_phone": phone,
        "otp": otp
    }
    api_response = await api_request("POST", "/phone-otp/verify", "", payload, api_key)
    return api_response