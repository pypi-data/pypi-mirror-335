from netbox.views import generic
from utilities.views import register_model_view

from netbox_routeros import filtersets, forms, models, tables


@register_model_view(models.InterfaceList, "list", path="", detail=False)
class InterfaceListListView(generic.ObjectListView):
    queryset = models.InterfaceList.objects.prefetch_related("routeros", "tags")
    table = tables.InterfaceListTable
    filterset = filtersets.InterfaceListFilterSet


@register_model_view(models.InterfaceList)
class InterfaceListView(generic.ObjectView):
    queryset = models.InterfaceList.objects.prefetch_related("routeros", "tags")
    template_name = "netbox_routeros/core/generic-object.html"


@register_model_view(models.InterfaceList, "add", detail=False)
@register_model_view(models.InterfaceList, "edit")
class InterfaceListEditView(generic.ObjectEditView):
    queryset = models.InterfaceList.objects.prefetch_related("routeros", "tags")
    form = forms.InterfaceListForm


@register_model_view(models.InterfaceList, "delete")
class InterfaceListDeleteView(generic.ObjectDeleteView):
    queryset = models.InterfaceList.objects.prefetch_related("routeros", "tags")
