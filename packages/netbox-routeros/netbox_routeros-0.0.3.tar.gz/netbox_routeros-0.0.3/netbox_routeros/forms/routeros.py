from dcim.models import Device, Platform
from django.db.models import Q
from django.forms import ModelChoiceField
from netbox.forms import NetBoxModelForm
from utilities.forms import fields

from netbox_routeros import models


class RouterosTypeForm(NetBoxModelForm):
    comments = fields.CommentField()
    platform = ModelChoiceField(
        queryset=Platform.objects.filter(routeros_type__isnull=True)
    )

    class Meta:
        model = models.RouterosType
        fields = (
            "platform",
            "description",
            "comments",
            "tags",
        )


class RouterosInstanceForm(NetBoxModelForm):
    comments = fields.CommentField()
    device = ModelChoiceField(
        queryset=Device.objects.filter(
            Q(platform__routeros_type__isnull=False) & Q(routeros__isnull=True)
        )
    )

    class Meta:
        model = models.RouterosInstance
        fields = (
            "device",
            "description",
            "comments",
            "tags",
        )
