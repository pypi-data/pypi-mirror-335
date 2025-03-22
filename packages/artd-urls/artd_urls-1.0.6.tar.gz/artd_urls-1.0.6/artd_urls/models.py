from django.db import models
from django.utils.translation import gettext_lazy as _
from artd_partner.models import Partner


class UrlBaseModel(models.Model):

    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )
    status = models.BooleanField(
        _("status"),
        default=True,
    )

    class Meta:
        abstract = True


class UrlConfiguration(UrlBaseModel):
    """Model definition for Url Configuration."""

    partner = models.OneToOneField(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
    )
    include_admin_urls = models.BooleanField(
        _("Include Admin URLs"),
        help_text=_("Include the admin urls in the list"),
        default=True,
    )
    include_dinamic_urls = models.BooleanField(
        _("Include Dinamic URLs"),
        help_text=_("Include the dinamic urls in the list"),
        default=True,
    )

    class Meta:
        """Meta definition for Url Configuration."""

        verbose_name = _("Url Configuration")
        verbose_name_plural = _("Url Configurations")

    def __str__(self):
        """Unicode representation of Url Configuration."""
        return self.partner.name


class Url(UrlBaseModel):
    """Model definition for Url."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Select the partner"),
        on_delete=models.CASCADE,
    )
    url = models.CharField(
        _("Url"),
        help_text=_("Enter the url of the product"),
        max_length=250,
        null=True,
        blank=True,
    )
    module = models.CharField(
        _("Module"),
        help_text=_("Enter the module of the product"),
        max_length=250,
        null=True,
        blank=True,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Enter the name of the product"),
        max_length=250,
        null=True,
        blank=True,
    )
    decorators = models.CharField(
        _("Decorator"),
        help_text=_("Enter the decorator of the product"),
        max_length=250,
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for Url."""

        verbose_name = _("Url")
        verbose_name_plural = _("Urls")

    def __str__(self):
        """Unicode representation of Url."""
        return self.name
