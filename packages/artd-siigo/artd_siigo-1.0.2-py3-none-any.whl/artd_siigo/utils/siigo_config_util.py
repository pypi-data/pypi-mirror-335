from artd_customer.models import Customer
from artd_partner.models import Partner
from artd_siigo.models import SiigoConfig


def update_tax_segment(
    partner: Partner,
    customer: Customer,
):
    if SiigoConfig.objects.filter(
        partner=partner,
    ).exists():
        if customer.tax_segment is None:
            siigo_config = SiigoConfig.objects.filter(
                partner=partner,
            ).first()
            customer.tax_segment = siigo_config.tax_segment
            customer.save()
