from authorizenet import apicontractsv1, apicontrollers
from authorizenet.apicontractsv1 import (
    customerAddressType,
    customerPaymentProfileType,
    paymentType,
)

from terminusgps.authorizenet.profiles.base import AuthorizenetSubProfileBase


class PaymentProfile(AuthorizenetSubProfileBase):
    def create(self, **kwargs) -> int:
        """
        Creates an Authorize.NET payment profile.

        :param billing_addr: An Authorize.NET customer address.
        :type billing_addr: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: An Authorize.NET API payment.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :returns: The new payment profile's id.
        :rtype: :py:obj:`int`

        """
        billing_addr = kwargs.get("billing_addr")
        payment = kwargs.get("payment")
        if not billing_addr:
            raise ValueError("'billing_addr' is required on creation.")
        if not payment:
            raise ValueError("'payment' is required on creation.")

        if not isinstance(billing_addr, customerAddressType):
            raise TypeError(
                f"'billing_addr' must be customerAddressType, got '{type(billing_addr)}'"
            )
        if not isinstance(payment, paymentType):
            raise TypeError(
                f"'payment' must be customerAddressType, got '{type(payment)}'"
            )

        response = self._authorizenet_create_payment_profile(billing_addr, payment)
        return int(response.customerPaymentProfileId)

    def update(self, billing_addr: customerAddressType, payment: paymentType) -> dict:
        """Updates the Authorize.NET payment profile."""
        return self._authorizenet_update_payment_profile(billing_addr, payment)

    def delete(self) -> dict:
        """Deletes the Authorize.NET payment profile."""
        return self._authorizenet_delete_payment_profile()

    def get_details(self, issuer_info: bool = False) -> dict:
        return self._authorizenet_get_payment_profile(issuer_info)

    def _authorizenet_create_payment_profile(
        self, billing_addr: customerAddressType, payment: paymentType
    ) -> dict:
        request = apicontractsv1.createCustomerPaymentProfileRequest(
            customerProfileId=self.customerProfileId,
            merchantAuthentication=self.merchantAuthentication,
            paymentProfile=customerPaymentProfileType(
                billTo=billing_addr, payment=payment, defaultPaymentProfile=self.default
            ),
            validationMode=self.validationMode,
        )
        controller = apicontrollers.createCustomerPaymentProfileController(request)
        response = self.execute_controller(controller)
        return response

    def _authorizenet_get_payment_profile(self, issuer_info: bool = False) -> dict:
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
        self, billing_addr: customerAddressType, payment: paymentType
    ) -> dict:
        assert self.id, "'id' was not set."

        request = apicontractsv1.updateCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            paymentProfile=customerPaymentProfileType(
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
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
        )
        controller = apicontrollers.deleteCustomerPaymentProfileController(request)
        response = self.execute_controller(controller)
        return response
