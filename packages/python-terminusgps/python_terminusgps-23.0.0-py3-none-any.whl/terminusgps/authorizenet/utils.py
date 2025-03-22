from authorizenet import apicontractsv1, apicontrollers
from authorizenet.apicontrollersbase import APIOperationBase

from .auth import get_environment, get_merchant_auth


class ControllerExecutionError(Exception):
    """Raised when an Authorizenet API controller fails to execute."""

    def __init__(self, message: str, code: str, *args, **kwargs) -> None:
        self.code = code
        super().__init__(message, *args, **kwargs)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class ControllerExecutionMixin:
    @staticmethod
    def execute_controller(controller: APIOperationBase) -> dict | None:
        """
        Executes an Authorizenet controller and returns its response.

        :param controller: An Authorizenet API controller.
        :type controller: :py:obj:`~authorizenet.apicontrollersbase.APIOperationBase`
        :raises ControllerExecutionError: If the API call fails.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()

        if response is not None and response.messages.resultCode != "Ok":
            raise ControllerExecutionError(
                message=response.messages.message[0]["text"].text,
                code=response.messages.message[0]["code"].text,
            )
        return response


def get_customer_profile_ids() -> list[int]:
    """
    Returns a list of all customer profile ids in Authorizenet.

    :raises ValueError: If something goes wrong calling the Authorizenet API.
    :returns: A list of all customer profile ids in Authorizenet.
    :rtype: :py:obj:`list`

    """
    request = apicontractsv1.getCustomerProfileIdsRequest(
        merchantAuthentication=get_merchant_auth()
    )
    controller = apicontrollers.getCustomerProfileIdsController(request)
    controller.execute()
    response = controller.getresponse()

    if response is not None and response.messages.resultCode != "Ok":
        raise ValueError(response.messages.message["text"].text)
    return [int(id) for id in response.ids.getchildren()]
