from dcim.models import Interface
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import PrimaryModel

from .routeros import RouterosInstance


class InterfaceList(PrimaryModel):
    routeros = models.ForeignKey(
        verbose_name=_("RouterOS"),
        to=RouterosInstance,
        on_delete=models.CASCADE,
        related_name="interface_lists",
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64,
        db_collation="natural_sort",
    )
    interfaces = models.ManyToManyField(
        verbose_name=_("Interfaces"),
        to=Interface,  # TODO: predefined interface lists
        # TODO: limit_choices_to=
        related_name="+",
        blank=True,
        symmetrical=False,
    )

    class Meta:
        ordering = ("routeros", "name")

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("plugins:netbox_routeros:interfacelist", args=[self.pk])
