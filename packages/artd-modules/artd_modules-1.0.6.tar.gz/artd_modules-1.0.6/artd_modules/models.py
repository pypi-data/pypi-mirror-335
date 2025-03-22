from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    created_at = models.DateTimeField(
        help_text=_("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        help_text=_("Updated at"),
        auto_now=True,
    )
    status = models.BooleanField(
        _("Status"),
        help_text=_("Status"),
        default=True,
    )

    class Meta:
        abstract = True

class Module(BaseModel):
    """Model definition for Module."""

    name = models.CharField(
        _("Name"),
        help_text=_("Name"),
        max_length=50,
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_("Slug"),
        max_length=50,
    )
    description = models.TextField(
        _("Description"),
        help_text=_("Description"),
        blank=True,
        null=True,
    )
    version = models.CharField(
        _("Version"),
        help_text=_("Version"),
        max_length=50,
    )
    is_plugin = models.BooleanField(
        _("Is plugin"),
        help_text=_("Is plugin"),
        default=False,
    )

    class Meta:
        """Meta definition for Module."""

        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

    def __str__(self):
        """Unicode representation of Module."""
        return self.name

