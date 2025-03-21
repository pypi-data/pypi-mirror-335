from authorizenet import apicontractsv1, apicontrollers
from authorizenet.apicontractsv1 import customerAddressType

from terminusgps.authorizenet.profiles.base import AuthorizenetSubProfileBase


class AddressProfile(AuthorizenetSubProfileBase):
    def create(self, **kwargs) -> int:
        """
        Creates an Authorize.NET address profile.

        :param shipping_addr: An Authorize.NET customer address.
        :type shipping_addr: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :raises ValueError: If no customer address was provided.
        :raises TypeError: If the customer address is not a :py:obj:`~authorizenet.apicontractsv1.customerAddressType` object.
        :returns: The new address profile's id.
        :rtype: :py:obj:`int`

        """
        shipping_addr = kwargs.get("shipping_addr")

        if not shipping_addr:
            raise ValueError("'shipping_addr' is required on creation.")

        if not isinstance(shipping_addr, customerAddressType):
            raise TypeError(
                f"'shipping_addr' must be customerAddressType, got '{type(shipping_addr)}'."
            )

        response = self._authorizenet_create_shipping_address(shipping_addr)
        return int(response.customerAddressId)

    def update(self, shipping_addr: customerAddressType) -> dict:
        """Updates the Authorize.NET payment profile."""
        return self._authorizenet_update_shipping_address(shipping_addr)

    def delete(self) -> dict:
        """Deletes the Authorize.NET payment profile."""
        return self._authorizenet_delete_shipping_address()

    def get_details(self) -> dict:
        return self._authorizenet_get_shipping_address()

    def _authorizenet_get_shipping_address(self) -> dict:
        assert self.id, "'id' was not set."

        request = apicontractsv1.getCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerAddressId=self.id,
        )
        controller = apicontrollers.getCustomerShippingAddressController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_create_shipping_address(self, addr: customerAddressType) -> dict:
        request = apicontractsv1.createCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            address=addr,
            defaultShippingAddress=self.default,
        )
        controller = apicontrollers.createCustomerShippingAddressController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_update_shipping_address(self, addr: customerAddressType) -> dict:
        assert self.id, "'id' was not set."
        addr.customerAddressId = self.id

        request = apicontractsv1.updateCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            address=addr,
            default=self.default,
        )
        controller = apicontrollers.updateCustomerShippingAddressController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_delete_shipping_address(self) -> dict:
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerAddressId=self.id,
        )
        controller = apicontrollers.deleteCustomerShippingAddressController(request)
        response = self.execute_controller(controller)
        return response
