from netbox.filtersets import NetBoxModelFilterSet

from netbox_routeros import models


class CapsmanInstanceFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.CapsmanInstance
        fields = ("id", "routeros")


class CapsmanServerConfigFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.CapsmanServerConfig
        fields = ("id", "capsman", "enabled")


class CapsmanChannelFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.CapsmanChannel
        fields = (
            "id",
            "name",
            "capsman",
            "band",
            "channel_width",
            "skip_dfs_channels",
        )


class CapsmanDatapathFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.CapsmanDatapath
        fields = ("id", "name", "capsman", "bridge", "vlan")
