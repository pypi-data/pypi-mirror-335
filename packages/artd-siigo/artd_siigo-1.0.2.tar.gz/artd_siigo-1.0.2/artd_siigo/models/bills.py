from artd_partner.models import Partner
from django.db import models
from django.utils.translation import gettext_lazy as _
from artd_siigo.models.catalogs import SiigoDocumentType
from artd_siigo.models.base_models import BaseModel
from artd_order.models import Order

ARTD_DOCUMENT_TYPE = (
    ("order", _("Order")),
    ("credit_note", _("Credit Note")),
    ("debit_note", _("Debit Note")),
)


class BillType(BaseModel):
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
    )
    code = models.CharField(
        max_length=100,
        verbose_name=_("Code"),
    )

    class Meta:
        verbose_name = _("Bill Type")
        verbose_name_plural = _("Bill Types")
        unique_together = ("partner", "code")

    def __str__(self):
        return f"{self.name} {self.partner.name}"


class BillConfig(BaseModel):
    partner = models.OneToOneField(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
    )
    siigo_document_type = models.ForeignKey(
        SiigoDocumentType,
        on_delete=models.PROTECT,
        verbose_name=_("Siigo Document Type"),
    )
    bill_type = models.ForeignKey(
        BillType,
        on_delete=models.PROTECT,
        verbose_name=_("Bill Type"),
    )
    generate_electronic_document = models.BooleanField(
        default=False,
        verbose_name=_("Generate Electronic Document"),
    )
    artd_document_type = models.CharField(
        max_length=100,
        choices=ARTD_DOCUMENT_TYPE,
        verbose_name=_("ARTD Document Type"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Bill Config")
        verbose_name_plural = _("Bill Configs")
        unique_together = ("partner", "siigo_document_type")

    def __str__(self):
        return f"{self.partner.name} {self.siigo_document_type.name}"


class SiigoInvoice(BaseModel):
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("Order"),
        null=True,
        blank=True,
    )
    siigo_id = models.CharField(
        max_length=100,
        verbose_name=_("Siigo ID"),
    )
    number = models.PositiveIntegerField(
        verbose_name=_("Number"),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
    )
    date = models.DateField(
        verbose_name=_("Date"),
    )
    customer = models.JSONField(
        verbose_name=_("Customer"),
        default=dict,
    )
    cost_center = models.PositiveIntegerField(
        verbose_name=_("Cost Center"),
    )
    currency = models.JSONField(
        verbose_name=_("Currency"),
        default=dict,
    )
    total = models.FloatField(
        verbose_name=_("Total"),
    )
    balance = models.FloatField(
        verbose_name=_("Balance"),
    )
    seller = models.PositiveIntegerField(
        verbose_name=_("Seller"),
    )
    stamp = models.JSONField(
        verbose_name=_("Stamp"),
        default=dict,
    )
    mail = models.JSONField(
        verbose_name=_("Mail"),
        default=dict,
    )
    observations = models.TextField(
        verbose_name=_("Observations"),
        blank=True,
        null=True,
    )
    items = models.JSONField(
        verbose_name=_("Items"),
        default=dict,
    )
    payments = models.JSONField(
        verbose_name=_("Payments"),
        default=dict,
    )
    public_url = models.TextField(
        verbose_name=_("Public URL"),
        blank=True,
        null=True,
    )
    global_discounts = models.JSONField(
        verbose_name=_("Global Discounts"),
        default=dict,
    )
    additional_fields = models.JSONField(
        verbose_name=_("Additional Fields"),
        default=dict,
    )
    metadata = models.JSONField(
        verbose_name=_("Metadata"),
        default=dict,
    )
    json_data = models.JSONField(
        verbose_name=_("JSON Data"),
        default=dict,
    )

    class Meta:
        verbose_name = _("Siigo Invoice")
        verbose_name_plural = _("Siigo Invoices")

    def __str__(self):
        return f"{self.partner.name} {self.siigo_id}"
