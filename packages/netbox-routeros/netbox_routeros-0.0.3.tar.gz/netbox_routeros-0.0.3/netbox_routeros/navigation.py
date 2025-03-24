from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

routeros_menus = (
    PluginMenuItem(
        link_text="RouterOS Type",
        link="plugins:netbox_routeros:routerostype_list",
        auth_required=True,
        staff_only=True,
        permissions=["netbox_routeros.view_routerostype"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_routeros:routerostype_add",
                title="Add Type",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_routeros.add_routerostype"],
            ),
        ),
    ),
    PluginMenuItem(
        link_text="RouterOS Instance",
        link="plugins:netbox_routeros:routerosinstance_list",
        auth_required=True,
        staff_only=True,
        permissions=["netbox_routeros.view_routerosinstance"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_routeros:routerosinstance_add",
                title="Add Instance",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_routeros.add_routerosinstance"],
            ),
        ),
    ),
)

interfaces_menus = (
    PluginMenuItem(
        link_text="Interface List",
        link="plugins:netbox_routeros:interfacelist_list",
        auth_required=True,
        staff_only=True,
        permissions=["netbox_routeros.view_interfacelist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_routeros:interfacelist_add",
                title="Add Interface list",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_routeros.add_interfacelist"],
            ),
        ),
    ),
)

capsman_menus = (
    PluginMenuItem(
        link_text="Instance",
        link="plugins:netbox_routeros:capsmaninstance_list",
        auth_required=True,
        staff_only=True,
        permissions=["netbox_routeros.view_capsmaninstance"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_routeros:capsmaninstance_add",
                title="Add Instance",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_routeros.add_capsmaninstance"],
            ),
        ),
    ),
    PluginMenuItem(
        link_text="Server config",
        link="plugins:netbox_routeros:capsmanserverconfig_list",
        auth_required=True,
        staff_only=True,
        permissions=["netbox_routeros.view_capsmanserverconfig"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_routeros:capsmanserverconfig_add",
                title="Add Server config",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_routeros.add_capsmanserverconfig"],
            ),
        ),
    ),
    PluginMenuItem(
        link_text="Channels",
        link="plugins:netbox_routeros:capsmanchannel_list",
        auth_required=True,
        staff_only=True,
        permissions=["netbox_routeros.view_capsmanchannel"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_routeros:capsmanchannel_add",
                title="Add Channel",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_routeros.add_capsmanchannel"],
            ),
        ),
    ),
    PluginMenuItem(
        link_text="Datapath",
        link="plugins:netbox_routeros:capsmandatapath_list",
        auth_required=True,
        staff_only=True,
        permissions=["netbox_routeros.view_capsmandatapath"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_routeros:capsmandatapath_add",
                title="Add Datapath",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_routeros.add_capsmandatapath"],
            ),
        ),
    ),
)

menu = PluginMenu(
    label="RouterOS",
    groups=(
        ("RouterOS", routeros_menus),
        ("Interface", interfaces_menus),
        ("CapsMan", capsman_menus),
    ),
)
