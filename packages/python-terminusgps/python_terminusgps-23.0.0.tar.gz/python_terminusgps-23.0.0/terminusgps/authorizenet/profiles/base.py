from abc import abstractmethod
from typing import override

from authorizenet import apicontractsv1

from terminusgps.authorizenet.auth import get_merchant_auth, get_validation_mode
from terminusgps.authorizenet.utils import ControllerExecutionMixin


class AuthorizenetProfileBase(ControllerExecutionMixin):
    def __init__(
        self, merchant_id: int | str, id: int | str | None = None, *args, **kwargs
    ) -> None:
        self._merchantCustomerId = merchant_id
        self._id = int(id) if id else self.create(*args, **kwargs)

    @override
    def __str__(self) -> str:
        return f"#{self.id}"

    @property
    def merchantCustomerId(self) -> str:
        """An internally designated customer id."""
        return str(self._merchantCustomerId)

    @property
    def id(self) -> str:
        """An Authorizenet generated id."""
        return str(self._id)

    @property
    def merchantAuthentication(self) -> apicontractsv1.merchantAuthenticationType:
        """Merchant authentication for Authorizenet API calls."""
        return get_merchant_auth()

    @abstractmethod
    def create(self, *args, **kwargs) -> int:
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
        super().__init__(*args, **kwargs)

    @property
    def validationMode(self) -> str:
        """The validation mode for Authorizenet API calls."""
        return get_validation_mode()

    @property
    def default(self) -> str:
        """Whether or not the sub profile is set as default in Authorizenet."""
        return str(self._default).lower()

    @property
    def customerProfileId(self) -> str:
        """An Authorizenet generated customer profile id."""
        return str(self._customerProfileId)
