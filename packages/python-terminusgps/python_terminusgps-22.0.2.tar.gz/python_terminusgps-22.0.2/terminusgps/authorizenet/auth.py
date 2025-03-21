from authorizenet.apicontractsv1 import merchantAuthenticationType
from authorizenet.constants import constants

from django.conf import settings


def get_merchant_auth() -> merchantAuthenticationType:
    return merchantAuthenticationType(
        name=str(settings.MERCHANT_AUTH_LOGIN_ID),
        transactionKey=str(settings.MERCHANT_AUTH_TRANSACTION_KEY),
    )


def get_environment() -> str:
    return constants.SANDBOX if settings.DEBUG else constants.PRODUCTION


def get_validation_mode() -> str:
    return "testMode" if settings.DEBUG else "liveMode"
