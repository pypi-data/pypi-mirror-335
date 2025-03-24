from dcim.api import views


class InterfaceViewSet(views.InterfaceViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        filter_fields = self.request.query_params.getlist("x_filter_fields", [])
        capsman = self.request.query_params.get("capsman", None)
        if capsman is not None:
            qs = qs.filter(device__routeros__capsman=capsman)
        elif "capsman" in filter_fields:
            return qs.none()
        routeros = self.request.query_params.get("routeros", None)
        if routeros is not None:
            qs = qs.filter(device__routeros=routeros)
        elif "routeros" in filter_fields:
            return qs.none()
        return qs
