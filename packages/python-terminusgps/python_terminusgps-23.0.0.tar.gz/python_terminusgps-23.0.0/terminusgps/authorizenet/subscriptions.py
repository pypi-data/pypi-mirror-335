from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.authorizenet.utils import ControllerExecutionMixin


class Subscription(ControllerExecutionMixin):
    def __init__(self, id: str | int | None = None, *args, **kwargs) -> None:
        if id and isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit, got '{id}'.")
        self.id = int(id) if id else self.create(*args, **kwargs)

    def create(
        self,
        name: str,
        amount: str,
        schedule: apicontractsv1.paymentScheduleType,
        payment: apicontractsv1.paymentType,
        address: apicontractsv1.customerAddressType,
        trial_amount: str = "0.00",
    ) -> int:
        request = apicontractsv1.ARBCreateSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscription=apicontractsv1.ARBSubscriptionType(
                name=name,
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
