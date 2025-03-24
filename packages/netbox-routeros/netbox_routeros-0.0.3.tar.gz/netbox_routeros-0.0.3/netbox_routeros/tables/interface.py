import django_tables2 as django_tables
from netbox.tables import NetBoxTable, columns

from netbox_routeros import models


class InterfaceListTable(NetBoxTable):
    routeros = django_tables.Column(linkify=True)
    name = django_tables.Column(linkify=True)
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_routeros:interfacelist_list")

    class Meta(NetBoxTable.Meta):
        model = models.InterfaceList
        fields = (
            "pk",
            "id",
            "routeros",
            "name",
            "interfaces",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "pk",
            "routeros",
            "name",
            "interfaces",
            "description",
        )
