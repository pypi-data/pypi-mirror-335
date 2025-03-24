from netbox.views import generic
from utilities.views import register_model_view

from netbox_routeros import filtersets, forms, models, tables


@register_model_view(models.CapsmanInstance, "list", path="", detail=False)
class CapsmanInstanceListView(generic.ObjectListView):
    queryset = models.CapsmanInstance.objects.prefetch_related("routeros", "tags")
    table = tables.CapsmanInstanceTable
    filterset = filtersets.CapsmanInstanceFilterSet


@register_model_view(models.CapsmanInstance)
class CapsmanInstanceView(generic.ObjectView):
    queryset = models.CapsmanInstance.objects.prefetch_related("routeros", "tags")
    template_name = "netbox_routeros/core/generic-object.html"


@register_model_view(models.CapsmanInstance, "add", detail=False)
@register_model_view(models.CapsmanInstance, "edit")
class CapsmanInstanceEditView(generic.ObjectEditView):
    queryset = models.CapsmanInstance.objects.prefetch_related("routeros", "tags")
    form = forms.CapsmanInstanceForm


@register_model_view(models.CapsmanInstance, "delete")
class CapsmanInstanceDeleteView(generic.ObjectDeleteView):
    queryset = models.CapsmanInstance.objects.prefetch_related("routeros", "tags")


@register_model_view(models.CapsmanServerConfig, "list", path="", detail=False)
class CapsmanServerConfigListView(generic.ObjectListView):
    queryset = models.CapsmanServerConfig.objects.prefetch_related(
        "capsman", "interface_lists", "interfaces", "tags"
    )
    table = tables.CapsmanServerConfigTable
    filterset = filtersets.CapsmanServerConfigFilterSet


@register_model_view(models.CapsmanServerConfig)
class CapsmanServerConfigView(generic.ObjectView):
    queryset = models.CapsmanServerConfig.objects.prefetch_related(
        "capsman", "interface_lists", "interfaces", "tags"
    )
    template_name = "netbox_routeros/core/generic-object.html"


@register_model_view(models.CapsmanServerConfig, "add", detail=False)
@register_model_view(models.CapsmanServerConfig, "edit")
class CapsmanServerConfigEditView(generic.ObjectEditView):
    queryset = models.CapsmanServerConfig.objects.prefetch_related(
        "capsman", "interface_lists", "interfaces", "tags"
    )
    form = forms.CapsmanServerConfigForm


@register_model_view(models.CapsmanServerConfig, "delete")
class CapsmanServerConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.CapsmanServerConfig.objects.prefetch_related(
        "capsman", "interface_lists", "interfaces", "tags"
    )


@register_model_view(models.CapsmanChannel, "list", path="", detail=False)
class CapsmanChannelListView(generic.ObjectListView):
    queryset = models.CapsmanChannel.objects.prefetch_related("capsman", "tags")
    table = tables.CapsmanChannelTable
    filterset = filtersets.CapsmanChannelFilterSet


@register_model_view(models.CapsmanChannel)
class CapsmanChannelView(generic.ObjectView):
    queryset = models.CapsmanChannel.objects.prefetch_related("capsman", "tags")
    template_name = "netbox_routeros/core/generic-object.html"


@register_model_view(models.CapsmanChannel, "add", detail=False)
@register_model_view(models.CapsmanChannel, "edit")
class CapsmanChannelEditView(generic.ObjectEditView):
    queryset = models.CapsmanChannel.objects.prefetch_related("capsman", "tags")
    form = forms.CapsmanChannelForm


@register_model_view(models.CapsmanChannel, "delete")
class CapsmanChannelDeleteView(generic.ObjectDeleteView):
    queryset = models.CapsmanChannel.objects.prefetch_related("capsman", "tags")


@register_model_view(models.CapsmanDatapath, "list", path="", detail=False)
class CapsmanDatapathListView(generic.ObjectListView):
    queryset = models.CapsmanDatapath.objects.prefetch_related(
        "capsman", "bridge", "vlan", "tags"
    )
    table = tables.CapsmanDatapathTable
    filterset = filtersets.CapsmanDatapathFilterSet


@register_model_view(models.CapsmanDatapath)
class CapsmanDatapathView(generic.ObjectView):
    queryset = models.CapsmanDatapath.objects.prefetch_related(
        "capsman", "bridge", "vlan", "tags"
    )
    template_name = "netbox_routeros/core/generic-object.html"


@register_model_view(models.CapsmanDatapath, "add", detail=False)
@register_model_view(models.CapsmanDatapath, "edit")
class CapsmanDatapathEditView(generic.ObjectEditView):
    queryset = models.CapsmanDatapath.objects.prefetch_related(
        "capsman", "bridge", "vlan", "tags"
    )
    form = forms.CapsmanDatapathForm


@register_model_view(models.CapsmanDatapath, "delete")
class CapsmanDatapathDeleteView(generic.ObjectDeleteView):
    queryset = models.CapsmanDatapath.objects.prefetch_related(
        "capsman", "bridge", "vlan", "tags"
    )
