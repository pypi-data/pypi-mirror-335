from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Abstract base model that includes `status`, `created_at`,
    and `updated_at` fields for any Django model that inherits
    from this class.

    Attributes:
        status (bool): Boolean field indicating if the
            record is active or not.
        created_at (datetime): Automatically stores the
            datetime when the record is created.
        updated_at (datetime): Automatically stores the
            datetime when the record is updated.
    """

    status: bool = models.BooleanField(
        _("Status"),
        help_text=_("Status of the record"),
        default=True,
    )
    created_at: models.DateTimeField = models.DateTimeField(
        _("Created at"),
        help_text=_("Date and time when the record was created"),
        auto_now_add=True,
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        _("Updated at"),
        help_text=_("Date and time when the record was updated"),
        auto_now=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("Base Model")
        verbose_name_plural = _("Base Models")
