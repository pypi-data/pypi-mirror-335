from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.profiles.base import AuthorizenetSubProfileBase


class PaymentProfile(AuthorizenetSubProfileBase):
    """An Authorizenet customer payment profile."""

    def create(
        self,
        billing_addr: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> int:
        """
        Creates an Authorizenet payment profile and returns its id.

        :param billing_addr: A billing address.
        :type billing_addr: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: A payment object.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :returns: The new payment profile's id.
        :rtype: :py:obj:`int`

        """
        response = self._authorizenet_create_payment_profile(billing_addr, payment)
        return int(response.customerPaymentProfileId)

    def update(
        self,
        billing_addr: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> dict:
        """Updates the Authorizenet payment profile."""
        return self._authorizenet_update_payment_profile(billing_addr, payment)

    def delete(self) -> dict:
        """Deletes the Authorizenet payment profile."""
        return self._authorizenet_delete_payment_profile()

    def get_details(self, issuer_info: bool = False) -> dict:
        return self._authorizenet_get_payment_profile(issuer_info)

    def _authorizenet_get_transaction_list_for_customer(
        self,
        limit: int = 100,
        ordering: str = "submitTimeUTC",
        offset: int = 1,
        descending: bool = False,
    ) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getTransactionListForCustomerRequest` using the Authorizenet API.

        :param limit: Total number of transactions to retrieve. Default is ``100``.
        :type limit: :py:obj:`int`
        :param ordering: A field to order the transactions by. Default is ``"submitTimeUTC"``.
        :type ordering: :py:obj:`str`
        :param offset: Page of the response to retrieve.
        :type offset: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param descending: Sort the results in descending order.
        :type descending: :py:obj:`bool`
        :raises ValueError: If ``ordering`` is invalid.
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        ordering_options: tuple[str, str] = ("id", "submitTimeUTC")
        if ordering not in ordering_options:
            raise ValueError(
                f"'ordering' must be one of {ordering_options}, got '{ordering}'."
            )

        request = apicontractsv1.getTransactionListForCustomerRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
            sorting={"orderBy": ordering, "orderDescending": str(descending).lower()},
            paging={"limit": str(limit), "offset": str(offset)},
        )
        controller = apicontrollers.getTransactionListForCustomerController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_create_payment_profile(
        self,
        billing_addr: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerPaymentProfileRequest` using the Authorizenet API.

        :param billing_addr: A customer address.
        :type billing_addr: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: A payment method.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises : If :py:attr:`id` wasn't set.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        request = apicontractsv1.createCustomerPaymentProfileRequest(
            customerProfileId=self.customerProfileId,
            merchantAuthentication=self.merchantAuthentication,
            paymentProfile=apicontractsv1.customerPaymentProfileType(
                billTo=billing_addr, payment=payment, defaultPaymentProfile=self.default
            ),
            validationMode=self.validationMode,
        )
        controller = apicontrollers.createCustomerPaymentProfileController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_get_payment_profile(self, issuer_info: bool = False) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerPaymentProfileRequest` using the Authorizenet API.

        :param issuer_info: Whether or not to include issuer information in the response.
        :type issuer_info: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.getCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
            includeIssuerInfo=str(issuer_info).lower(),
        )
        controller = apicontrollers.getCustomerPaymentProfileController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_update_payment_profile(
        self,
        billing_addr: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.validateCustomerPaymentProfileRequest` using the Authorizenet API.

        :param billing_addr: A customer address.
        :type billing_addr: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: A payment method.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.updateCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            paymentProfile=apicontractsv1.customerPaymentProfileType(
                billTo=billing_addr,
                payment=payment,
                defaultPaymentProfile=self.default,
                customerPaymentProfileId=self.id,
            ),
            validationMode=self.validationMode,
        )
        controller = apicontrollers.updateCustomerPaymentProfileController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_validate_payment_profile(self) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.validateCustomerPaymentProfileRequest` using the Authorizenet API.

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.validateCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
            validationMode=self.validationMode,
        )
        controller = apicontrollers.validateCustomerPaymentProfileController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_delete_payment_profile(self) -> dict:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerPaymentProfileRequest` using the Authorizenet API.

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :returns: An Authorizenet API response.
        :rtype: :py:obj:`dict`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
        )
        controller = apicontrollers.deleteCustomerPaymentProfileController(request)
        response = self.execute_controller(controller)
        return response
