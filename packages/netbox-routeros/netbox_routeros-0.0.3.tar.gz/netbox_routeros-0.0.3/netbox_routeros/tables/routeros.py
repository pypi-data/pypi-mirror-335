import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from netbox_routeros import models


class RouterosTypeTable(NetBoxTable):
    platform = tables.Column(verbose_name=_("Platform"), linkify=True)
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_routeros:routerostype_list")

    class Meta(NetBoxTable.Meta):
        model = models.RouterosType
        fields = (
            "pk",
            "id",
            "platform",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "pk",
            "platform",
            "description",
        )


class RouterosInstanceTable(NetBoxTable):
    device = tables.Column(verbose_name=_("Device"), linkify=True)
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_routeros:routerosinstance_list")

    class Meta(NetBoxTable.Meta):
        model = models.RouterosInstance
        fields = (
            "pk",
            "id",
            "device",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "pk",
            "device",
            "description",
        )
