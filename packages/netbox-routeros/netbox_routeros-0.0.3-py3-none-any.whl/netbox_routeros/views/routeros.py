from netbox.views import generic
from utilities.views import register_model_view

from netbox_routeros import filtersets, forms, models, tables


@register_model_view(models.RouterosType, "list", path="", detail=False)
class RouterosTypeListView(generic.ObjectListView):
    queryset = models.RouterosType.objects.prefetch_related("platform", "tags")
    table = tables.RouterosTypeTable
    filterset = filtersets.RouterosTypeFilterSet


@register_model_view(models.RouterosType)
class RouterosTypeView(generic.ObjectView):
    queryset = models.RouterosType.objects.prefetch_related("platform", "tags")
    template_name = "netbox_routeros/core/generic-object.html"


@register_model_view(models.RouterosType, "add", detail=False)
@register_model_view(models.RouterosType, "edit")
class RouterosTypeEditView(generic.ObjectEditView):
    queryset = models.RouterosType.objects.prefetch_related("platform", "tags")
    form = forms.RouterosTypeForm


@register_model_view(models.RouterosType, "delete")
class RouterosTypeDeleteView(generic.ObjectDeleteView):
    queryset = models.RouterosType.objects.prefetch_related("platform", "tags")


@register_model_view(models.RouterosInstance, "list", path="", detail=False)
class RouterosInstanceListView(generic.ObjectListView):
    queryset = models.RouterosInstance.objects.prefetch_related("device", "tags")
    table = tables.RouterosInstanceTable
    filterset = filtersets.RouterosInstanceFilterSet


@register_model_view(models.RouterosInstance)
class RouterosInstanceView(generic.ObjectView):
    queryset = models.RouterosInstance.objects.prefetch_related("device", "tags")
    template_name = "netbox_routeros/core/generic-object.html"


@register_model_view(models.RouterosInstance, "add", detail=False)
@register_model_view(models.RouterosInstance, "edit")
class RouterosInstanceEditView(generic.ObjectEditView):
    queryset = models.RouterosInstance.objects.prefetch_related("device", "tags")
    form = forms.RouterosInstanceForm


@register_model_view(models.RouterosInstance, "delete")
class RouterosInstanceDeleteView(generic.ObjectDeleteView):
    queryset = models.RouterosInstance.objects.prefetch_related("device", "tags")
