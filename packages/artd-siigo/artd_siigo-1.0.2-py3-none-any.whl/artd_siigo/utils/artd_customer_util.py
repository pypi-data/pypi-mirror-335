from artd_customer.models import Customer
from artd_partner.models import Partner


class CustomerUtil:
    def __init__(
        self,
        partner: Partner,
        document: str,
    ) -> None:
        self.__partner = partner
        self.__document = document

    def get_customer(self) -> Customer | None:
        if Customer.objects.filter(
            partner=self.__partner,
            document=self.__document,
        ).exists():
            return Customer.objects.filter(
                partner=self.__partner,
                document=self.__document,
            ).first()
        else:
            return None
