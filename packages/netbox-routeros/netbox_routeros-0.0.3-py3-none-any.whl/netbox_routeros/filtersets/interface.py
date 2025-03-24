from netbox.filtersets import NetBoxModelFilterSet

from netbox_routeros import models


class InterfaceListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.InterfaceList
        fields = ("id", "routeros", "name")
