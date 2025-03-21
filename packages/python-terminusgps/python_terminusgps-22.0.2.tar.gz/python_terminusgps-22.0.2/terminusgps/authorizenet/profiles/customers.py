from authorizenet import apicontractsv1, apicontrollers
from authorizenet.apicontractsv1 import customerProfileType

from terminusgps.authorizenet.profiles.base import AuthorizenetProfileBase


class CustomerProfile(AuthorizenetProfileBase):
    def create(self, **kwargs) -> int:
        """
        Creates the customer profile.

        :param email: An email address for the customer profile.
        :type email: :py:obj:`str`
        :param desc: A description describing the customer profile. Optional.
        :type desc: :py:obj:`str` | :py:obj:`None`
        :returns: The new customer profile id.
        :rtype: :py:obj:`int`

        """
        if not kwargs.get("email"):
            raise ValueError("'email' is required for creation.")

        response = self._authorizenet_create_customer_profile(
            email=kwargs["email"], desc=kwargs.get("desc", "")
        )
        return int(response.customerProfileId)

    def update(self, email: str, desc: str = "") -> dict:
        """Updates the customer profile."""
        return self._authorizenet_update_customer_profile(email, desc)

    def delete(self) -> dict:
        """Deletes the customer profile."""
        return self._authorizenet_delete_customer_profile()

    def get_payment_profiles(self) -> list[dict] | None:
        """Retrieves the customer profile's payment profiles list."""
        profiles = self._authorizenet_get_customer_profile(issuer_info=False).get(
            "paymentProfiles"
        )
        return profiles if profiles else None

    def get_shipping_addresses(self) -> list[dict] | None:
        """Retrieves the customer profile's shipping address list."""
        addresses = self._authorizenet_get_customer_profile(issuer_info=False).get(
            "shipToList"
        )
        return addresses if addresses else None

    def _authorizenet_create_customer_profile(
        self, email: str, desc: str = ""
    ) -> dict[str, str]:
        """Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerProfileRequest` using the Authorize.NET API."""
        request = apicontractsv1.createCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=customerProfileType(
                merchantCustomerId=self.merchantCustomerId,
                email=email,
                description=desc,
            ),
        )
        controller = apicontrollers.createCustomerProfileController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_get_customer_profile(self, issuer_info: bool = True) -> dict:
        """Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerProfileRequest` using the Authorize.NET API."""
        assert self.id, "'id' was not set."

        request = apicontractsv1.getCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.id,
            includeIssuerInfo=str(issuer_info).lower(),
        )
        controller = apicontrollers.getCustomerProfileController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_update_customer_profile(self, email: str, desc: str = "") -> dict:
        """Executes an :py:obj:`~authorizenet.apicontractsv1.updateCustomerProfileRequest` using the Authorize.NET API."""
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
        response = self.execute_controller(controller)
        return response

    def _authorizenet_delete_customer_profile(self) -> dict:
        """Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerProfileRequest` using the Authorize.NET API."""
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.id,
        )
        controller = apicontrollers.deleteCustomerProfileController(request)
        response = self.execute_controller(controller)
        return response
