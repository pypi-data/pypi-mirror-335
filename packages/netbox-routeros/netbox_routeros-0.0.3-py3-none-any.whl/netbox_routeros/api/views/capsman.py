from netbox.api.viewsets import NetBoxModelViewSet

from netbox_routeros import filtersets, models
from netbox_routeros.api import serializers


class CapsmanInstanceViewSet(NetBoxModelViewSet):
    queryset = models.CapsmanInstance.objects.prefetch_related("routeros", "tags")
    serializer_class = serializers.CapsmanInstanceSerializer
    filterset_class = filtersets.CapsmanInstanceFilterSet


class CapsmanServerConfigViewSet(NetBoxModelViewSet):
    queryset = models.CapsmanServerConfig.objects.prefetch_related(
        "capsman", "interface_lists", "interfaces", "tags"
    )
    serializer_class = serializers.CapsmanServerConfigSerializer
    filterset_class = filtersets.CapsmanServerConfigFilterSet


class CapsmanChannelViewSet(NetBoxModelViewSet):
    queryset = models.CapsmanChannel.objects.prefetch_related("capsman", "tags")
    serializer_class = serializers.CapsmanChannelSerializer
    filterset_class = filtersets.CapsmanChannelFilterSet


class CapsmanDatapathViewSet(NetBoxModelViewSet):
    queryset = models.CapsmanDatapath.objects.prefetch_related(
        "capsman", "bridge", "vlan", "tags"
    )
    serializer_class = serializers.CapsmanDatapathSerializer
    filterset_class = filtersets.CapsmanDatapathFilterSet
