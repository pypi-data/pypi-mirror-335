from dcim.api.serializers import InterfaceSerializer
from ipam.api.serializers import VLANSerializer
from netbox.api.fields import IntegerRangeSerializer
from netbox.api.serializers import NetBoxModelSerializer

from netbox_routeros import models

from .interface import InterfaceListSerializer
from .routeros import RouterosInstanceSerializer


class CapsmanInstanceSerializer(NetBoxModelSerializer):
    routeros = RouterosInstanceSerializer(nested=True)

    class Meta:
        model = models.CapsmanInstance
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "routeros",
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
            "description",
        )


class CapsmanServerConfigSerializer(NetBoxModelSerializer):
    capsman = CapsmanInstanceSerializer(nested=True)
    interface_lists = InterfaceListSerializer(nested=True, many=True)
    interfaces = InterfaceSerializer(nested=True, many=True)

    class Meta:
        model = models.CapsmanServerConfig
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "capsman",
            "enabled",
            "interface_lists",
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
            "capsman",
            "enabled",
            "description",
        )


class CapsmanChannelSerializer(NetBoxModelSerializer):
    capsman = CapsmanInstanceSerializer(nested=True)
    frequency = IntegerRangeSerializer(many=True, required=False)

    class Meta:
        model = models.CapsmanChannel
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "name",
            "capsman",
            "band",
            "channel_width",
            "frequency",
            "skip_dfs_channels",
            "description",
            "enabled",
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
            "capsman",
            "name",
            "band",
            "channel_width",
            "frequency",
            "description",
        )


class CapsmanDatapathSerializer(NetBoxModelSerializer):
    capsman = CapsmanInstanceSerializer(nested=True)
    bridge = InterfaceSerializer(nested=True, allow_null=True)
    vlan = VLANSerializer(nested=True, allow_null=True)

    class Meta:
        model = models.CapsmanDatapath
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "name",
            "capsman",
            "bridge",
            "vlan",
            "description",
            "enabled",
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
            "capsman",
            "name",
            "bridge",
            "vlan",
            "description",
        )
