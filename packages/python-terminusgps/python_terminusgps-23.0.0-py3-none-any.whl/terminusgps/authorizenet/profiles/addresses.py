from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.profiles.base import AuthorizenetSubProfileBase


class AddressProfile(AuthorizenetSubProfileBase):
    """An Authorizenet customer address profile."""

    def create(self, shipping_addr: apicontractsv1.customerAddressType) -> int:
        """
        Creates an Authorizenet address profile.

        :param shipping_addr: An Authorizenet customer address.
        :type shipping_addr: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: A new address profile id.
        :rtype: :py:obj:`int`

        """
        response = self._authorizenet_create_shipping_address(shipping_addr)
        return int(response.customerAddressId)

    def update(self, shipping_addr: apicontractsv1.customerAddressType) -> dict:
        """
        Updates the Authorizenet address profile.

        :param shipping_addr: A customer shipping address.
        :type shipping_addr: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        return self._authorizenet_update_shipping_address(shipping_addr)

    def delete(self) -> dict:
        """
        Deletes the Authorizenet address profile.

        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict`

        """
        return self._authorizenet_delete_shipping_address()

    def _authorizenet_get_shipping_address(self) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerShippingAddressRequest` using the Authorizenet API.

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.getCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerAddressId=self.id,
        )
        controller = apicontrollers.getCustomerShippingAddressController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_create_shipping_address(
        self, addr: apicontractsv1.customerAddressType
    ) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerShippingAddressRequest` using the Authorizenet API.

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        request = apicontractsv1.createCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            address=addr,
            defaultShippingAddress=self.default,
        )
        controller = apicontrollers.createCustomerShippingAddressController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_update_shipping_address(
        self, addr: apicontractsv1.customerAddressType
    ) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.updateCustomerShippingAddressRequest` using the Authorizenet API.

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        assert self.id, "'id' was not set."

        addr.customerAddressId = self.id
        request = apicontractsv1.updateCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            address=addr,
            default=self.default,
        )
        controller = apicontrollers.updateCustomerShippingAddressController(request)
        return self.execute_controller(controller)

    def _authorizenet_delete_shipping_address(self) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerShippingAddressRequest` using the Authorizenet API.

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerAddressId=self.id,
        )
        controller = apicontrollers.deleteCustomerShippingAddressController(request)
        response = self.execute_controller(controller)
        return response
