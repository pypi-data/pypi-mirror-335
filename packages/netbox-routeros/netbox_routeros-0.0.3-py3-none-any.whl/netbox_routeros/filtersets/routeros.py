from netbox.filtersets import NetBoxModelFilterSet

from netbox_routeros import models


class RouterosTypeFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.RouterosType
        fields = ("id", "platform")


class RouterosInstanceFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.RouterosInstance
        fields = ("id", "device")
