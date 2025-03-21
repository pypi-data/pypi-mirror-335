from abc import abstractmethod

from authorizenet.apicontractsv1 import merchantAuthenticationType
from authorizenet.apicontrollersbase import APIOperationBase

from ..auth import get_merchant_auth, get_environment, get_validation_mode


class AuthorizenetProfileBase:
    def __init__(
        self, merchant_id: int | str, id: int | str | None = None, **kwargs
    ) -> None:
        self._merchantCustomerId = merchant_id
        self._id = str(id) if id else self.create(**kwargs)

    def __str__(self) -> str:
        return f"#{self.id}"

    def execute_controller(self, controller: APIOperationBase) -> dict:
        """
        Executes an Authorize.NET controller and returns its response.

        :param controller: An Authorize.NET API controller.
        :raises ValueError: If the API call fails.
        :returns: The Authorize.NET API response.
        :rtype: :py:obj:`dict`

        """
        controller.setenvironment(self.environment)
        controller.execute()
        response = controller.getresponse()

        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return response

    @property
    def merchantCustomerId(self) -> str:
        """
        An internally designated customer id.

        :type: :py:obj:`str`

        """
        return str(self._merchantCustomerId)

    @property
    def id(self) -> str:
        """
        An Authorizenet generated id.

        :type: :py:obj:`str`

        """
        return str(self._id)

    @property
    def merchantAuthentication(self) -> merchantAuthenticationType:
        """
        Merchant authentication for Authorizenet API calls.

        :type: :py:obj:`~authorizenet.apicontractsv1.merchantAuthenticationType`

        """
        return get_merchant_auth()

    @property
    def environment(self) -> str:
        """
        Environment for Authorizenet API calls to execute within.

        :type: :py:obj:`str`

        """
        return get_environment()

    @abstractmethod
    def create(self, **kwargs) -> int:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def update(self, *args, **kwargs) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def delete(self, *args, **kwargs) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")


class AuthorizenetSubProfileBase(AuthorizenetProfileBase):
    def __init__(
        self, customer_profile_id: int | str, default: bool, *args, **kwargs
    ) -> None:
        self._customerProfileId = customer_profile_id
        self._default = default
        return super().__init__(*args, **kwargs)

    @property
    def validationMode(self) -> str:
        """
        The validation mode for Authorizenet API calls.

        :type: :py:obj:`str`

        """
        return get_validation_mode()

    @property
    def default(self) -> str:
        """
        Whether or not the sub profile is set as default in Authorizenet.

        :type: :py:obj:`str`

        """
        return str(self._default).lower()

    @property
    def customerProfileId(self) -> str:
        """
        An Authorizenet generated customer profile id.

        :py:obj:`str`

        """
        return str(self._customerProfileId)
