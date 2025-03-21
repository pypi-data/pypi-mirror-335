from typing import Any

import asyncio
import twilio.rest

from django.conf import settings
from twilio.http.async_http_client import AsyncTwilioHttpClient


class TwilioCaller:
    def __init__(self) -> None:
        self.client_sid = settings.TWILIO_SID
        self.client_token = settings.TWILIO_TOKEN
        self.from_number = settings.TWILIO_FROM_NUMBER
        self.messaging_sid = settings.TWILIO_MESSAGING_SID

    def __enter__(self) -> "TwilioCaller":
        self.client = twilio.rest.Client(
            self.client_sid, self.client_token, http_client=AsyncTwilioHttpClient()
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        return None

    async def create_notification(
        self, to_number: str, message: str, method: str = "sms"
    ) -> asyncio.Task[Any]:
        match method:
            case "sms":
                task = asyncio.create_task(
                    self.create_sms(to_number=to_number, message=message)
                )
            case "call" | "phone":
                task = asyncio.create_task(
                    self.create_call(to_number=to_number, message=message)
                )
            case _:
                raise ValueError(f"Unsupported TwilioCaller method '{method}'.")
        return task

    async def create_call(self, to_number: str, message: str) -> None:
        await self.client.calls.create_async(
            to=to_number,
            from_=self.from_number,
            twiml=f"<Response><Say>{message}</Say></Response>",
        )

    async def create_sms(self, to_number: str, message: str) -> None:
        await self.client.messages.create_async(
            to=to_number,
            from_=self.from_number,
            body=message,
            messaging_service_sid=self.messaging_sid,
        )
