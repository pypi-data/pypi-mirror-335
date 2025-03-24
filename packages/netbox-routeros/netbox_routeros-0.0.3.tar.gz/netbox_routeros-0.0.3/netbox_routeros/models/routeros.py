from django.db import models
from django.urls import reverse
from netbox.models import PrimaryModel


class RouterosType(PrimaryModel):
    platform = models.OneToOneField(
        to="dcim.platform",
        on_delete=models.CASCADE,
        related_name="routeros_type",
        unique=True,
    )

    class Meta:
        ordering = ("platform",)

    def __str__(self):
        return str(self.platform)

    def get_absolute_url(self):
        return reverse("plugins:netbox_routeros:routerostype", args=[self.pk])


class RouterosInstance(PrimaryModel):
    device = models.OneToOneField(
        to="dcim.device",
        on_delete=models.CASCADE,
        related_name="routeros",
        unique=True,
    )

    class Meta:
        ordering = ("device",)

    def __str__(self):
        return str(self.device)

    def get_absolute_url(self):
        return reverse("plugins:netbox_routeros:routerosinstance", args=[self.pk])
