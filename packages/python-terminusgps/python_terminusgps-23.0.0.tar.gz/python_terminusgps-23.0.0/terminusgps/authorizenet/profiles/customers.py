from authorizenet import apicontractsv1, apicontrollers
from authorizenet.apicontractsv1 import customerProfileType

from terminusgps.authorizenet.profiles.base import AuthorizenetProfileBase
from terminusgps.authorizenet.utils import get_customer_profile_ids


class CustomerProfile(AuthorizenetProfileBase):
    """An Authorizenet customer profile."""

    def create(self, email: str, desc: str | None = None) -> int:
        """
        Creates a customer profile using the Authorizenet API and returns its id.

        :param email: An email address.
        :type email: :py:obj:`str`
        :param desc: An optional description.
        :type desc: :py:obj:`str` | :py:obj:`None`
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: The new customer profile id.
        :rtype: :py:obj:`int`

        """
        response = self._authorizenet_create_customer_profile(email=email, desc=desc)
        return int(response.customerProfileId)

    def update(self, email: str, desc: str = "") -> None:
        """
        Updates the customer profile.

        :param email: An email address.
        :type email: :py:obj:`str`
        :param desc: An optional description. Default is ``""``
        :type desc: :py:obj:`str`
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self._authorizenet_update_customer_profile(email, desc)

    def delete(self) -> None:
        """
        Deletes the customer profile.

        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self._authorizenet_delete_customer_profile()

    def get_payment_profiles(self) -> list[dict] | None:
        """
        Returns a list of the customer's payment profiles.

        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: A list of customer payment profiles, if they exist.
        :rtype: :py:obj:`list` | :py:obj:`None`

        """
        response = self._authorizenet_get_customer_profile(issuer_info=False)
        return response.get("paymentProfiles") if response else None

    def get_addresses(self) -> list[dict] | None:
        """
        Returns a list of the customer's address profiles.

        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: A list of customer shipping addresses, if they exist.
        :rtype: :py:obj:`list` | :py:obj:`None`

        """
        response = self._authorizenet_get_customer_profile(issuer_info=False)
        return response.get("shipToList") if response else None

    @property
    def exists(self) -> bool:
        """Whether or not the customer profile exists in Authorizenet."""
        profile_ids = get_customer_profile_ids()
        return int(self.id) in profile_ids if self.id is not None else False

    def _authorizenet_get_customer_profile_ids(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerProfileIdsRequest` using the Authorizenet API.

        `getCustomerProfileIdsRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile-ids>`_

        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        request = apicontractsv1.getCustomerProfileIdsRequest(
            merchantAuthentication=self.merchantAuthentication
        )
        controller = apicontrollers.getCustomerProfileIdsController(request)
        return self.execute_controller(controller)

    def _authorizenet_create_customer_profile(
        self, email: str, desc: str = ""
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerProfileRequest` using the Authorizenet API.

        `createCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-profile>`_

        :param email: An email address.
        :type email: :py:obj:`str`
        :param desc: An optional description.
        :type desc: :py:obj:`str`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        request = apicontractsv1.createCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=customerProfileType(
                merchantCustomerId=self.merchantCustomerId,
                email=email,
                description=desc,
            ),
        )
        controller = apicontrollers.createCustomerProfileController(request)
        return self.execute_controller(controller)

    def _authorizenet_get_customer_profile(
        self, issuer_info: bool = True
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerProfileRequest` using the Authorizenet API.

        `getCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile>`_

        :param issuer_info: Whether or not to include issuer info in the response.
        :type issuer_info: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`id` was not set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.getCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.id,
            includeIssuerInfo=str(issuer_info).lower(),
        )
        controller = apicontrollers.getCustomerProfileController(request)
        return self.execute_controller(controller)

    def _authorizenet_update_customer_profile(
        self, email: str, desc: str = ""
    ) -> dict | None:
        """
        Executes an :py:obj:`~authorizenet.apicontractsv1.updateCustomerProfileRequest` using the Authorizenet API.

        `updateCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-profile>`_

        :param email: An email address.
        :type email: :py:obj:`str`
        :param desc: An optional description.
        :type desc: :py:obj:`str`
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.updateCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=customerProfileType(
                merchantCustomerId=self.merchantCustomerId,
                email=email,
                description=desc,
                customerProfileId=self.id,
            ),
        )
        controller = apicontrollers.updateCustomerProfileController(request)
        return self.execute_controller(controller)

    def _authorizenet_delete_customer_profile(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerProfileRequest` using the Authorizenet API.

        `deleteCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-profile>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.id,
        )
        controller = apicontrollers.deleteCustomerProfileController(request)
        return self.execute_controller(controller)
