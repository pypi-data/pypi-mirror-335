from netbox.api.viewsets import NetBoxModelViewSet

from netbox_routeros import filtersets, models
from netbox_routeros.api import serializers


class InterfaceListViewSet(NetBoxModelViewSet):
    queryset = models.InterfaceList.objects.prefetch_related(
        "routeros", "interfaces", "tags"
    )
    serializer_class = serializers.InterfaceListSerializer
    filterset_class = filtersets.InterfaceListFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        filter_fields = self.request.query_params.getlist("x_filter_fields", [])
        capsman = self.request.query_params.get("capsman", None)
        if capsman is not None:
            qs = qs.filter(routeros__capsman=capsman)
        elif "capsman" in filter_fields:
            return qs.none()
        return qs
