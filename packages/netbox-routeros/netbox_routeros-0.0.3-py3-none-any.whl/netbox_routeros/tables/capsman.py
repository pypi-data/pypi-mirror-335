import django_tables2 as django_tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns
from netbox.tables.columns import ArrayColumn

from netbox_routeros import models


class CapsmanInstanceTable(NetBoxTable):
    routeros = django_tables.Column(verbose_name=_("RouterOS"), linkify=True)
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_routeros:capsmaninstance_list")

    class Meta(NetBoxTable.Meta):
        model = models.CapsmanInstance
        fields = (
            "pk",
            "id",
            "routeros",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "pk",
            "routeros",
            "description",
        )


class CapsmanServerConfigTable(NetBoxTable):
    capsman = django_tables.Column(verbose_name=_("CapsMan"), linkify=True)
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name="plugins:netbox_routeros:capsmanserverconfig_list"
    )

    class Meta(NetBoxTable.Meta):
        model = models.CapsmanServerConfig
        fields = (
            "pk",
            "id",
            "capsman",
            "enabled",
            "interface_lists",
            "interfaces",
            "upgrade_policy",
            "package_path",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "pk",
            "capsman",
            "enabled",
            "interface_lists",
            "interfaces",
            "description",
        )


def get_range_text(range):
    lower = range.lower
    upper = range.upper
    if not range.lower_inc:
        lower += 1
    if not range.upper_inc:
        upper -= 1
    return f"{lower}-{upper}"


class CapsmanChannelTable(NetBoxTable):
    name = django_tables.Column(linkify=True)
    capsman = django_tables.Column(verbose_name=_("CapsMan"), linkify=True)
    frequency = ArrayColumn(
        verbose_name=_("Frequency"), func=get_range_text, orderable=False
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_routeros:capsmanchannel_list")

    class Meta(NetBoxTable.Meta):
        model = models.CapsmanChannel
        fields = (
            "pk",
            "id",
            "name",
            "capsman",
            "band",
            "channel_width",
            "frequency",
            "skip_dfs_channels",
            "enabled",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "pk",
            "name",
            "capsman",
            "band",
            "channel_width",
            "frequency",
            "enabled",
            "description",
        )


class CapsmanDatapathTable(NetBoxTable):
    name = django_tables.Column(linkify=True)
    capsman = django_tables.Column(verbose_name=_("CapsMan"), linkify=True)
    bridge = django_tables.Column(verbose_name=_("Bridge"), linkify=True)
    vlan = django_tables.Column(verbose_name=_("VLAN"), linkify=True)
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_routeros:capsmandatapath_list")

    class Meta(NetBoxTable.Meta):
        model = models.CapsmanDatapath
        fields = (
            "pk",
            "id",
            "name",
            "capsman",
            "bridge",
            "vlan",
            "enabled",
            "description",
            "comments",
            "tags",
        )
        default_columns = (
            "pk",
            "name",
            "capsman",
            "bridge",
            "enabled",
            "vlan",
            "description",
        )
