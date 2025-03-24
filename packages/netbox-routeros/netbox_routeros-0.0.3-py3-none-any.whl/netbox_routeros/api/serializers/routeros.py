from dcim.api.serializers import DeviceSerializer, PlatformSerializer
from netbox.api.serializers import NetBoxModelSerializer

from netbox_routeros import models


class RouterosTypeSerializer(NetBoxModelSerializer):
    platform = PlatformSerializer(nested=True)

    class Meta:
        model = models.RouterosType
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "platform",
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
            "platform",
            "description",
        )


class RouterosInstanceSerializer(NetBoxModelSerializer):
    device = DeviceSerializer(nested=True)

    class Meta:
        model = models.RouterosInstance
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "device",
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
            "device",
            "description",
        )
