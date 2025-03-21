from authorizenet import apicontractsv1, apicontrollers, apicontrollersbase
from terminusgps.authorizenet.auth import get_merchant_auth, get_environment


class Subscription:
    def __init__(self, name: str, id: str | int | None = None, **kwargs) -> None:
        if id is not None and isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit, got '{id}'.")
        self.name = name
        self.id = str(id if id else self.create(**kwargs))

    @property
    def merchantAuthentication(self) -> apicontractsv1.merchantAuthenticationType:
        return get_merchant_auth()

    @property
    def environment(self) -> str:
        return get_environment()

    def execute_controller(
        self, controller: apicontrollersbase.APIOperationBase
    ) -> dict:
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

    def create(
        self,
        schedule: apicontractsv1.paymentScheduleType,
        amount: str,
        payment: apicontractsv1.paymentType,
        address: apicontractsv1.customerAddressType,
        trial_amount: str = "0.00",
    ) -> int:
        request = apicontractsv1.ARBCreateSubscriptionRequest(
            merchantAuthentication=self.merchantAuthentication,
            subscription=apicontractsv1.ARBSubscriptionType(
                name=self.name,
                paymentSchedule=schedule,
                amount=amount,
                trialAmount=trial_amount,
                payment=payment,
                bill_to=address,
            ),
        )
        controller = apicontrollers.ARBCreateSubscriptionController(request)
        response = self.execute_controller(controller)
        return int(response.subscriptionId)
