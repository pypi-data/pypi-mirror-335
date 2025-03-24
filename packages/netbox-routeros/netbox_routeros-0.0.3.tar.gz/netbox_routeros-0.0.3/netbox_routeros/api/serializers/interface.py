from dcim.api.serializers import InterfaceSerializer
from netbox.api.serializers import NetBoxModelSerializer

from netbox_routeros import models

from .routeros import RouterosInstanceSerializer


class InterfaceListSerializer(NetBoxModelSerializer):
    routeros = RouterosInstanceSerializer(nested=True)
    interfaces = InterfaceSerializer(nested=True, many=True)

    class Meta:
        model = models.InterfaceList
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "routeros",
            "name",
            "interfaces",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "routeros",
            "name",
            "description",
        )
