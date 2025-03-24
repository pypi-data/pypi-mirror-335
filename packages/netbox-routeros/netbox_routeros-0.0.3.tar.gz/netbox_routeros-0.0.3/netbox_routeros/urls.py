from django.urls import include, path
from netbox.views.generic import ObjectChangeLogView
from utilities.urls import get_model_urls

from . import views  # noqa: F401 must be imported
from . import models

urlpatterns = [
    # --- Core ---
    path(
        "routeros/type/",
        include(get_model_urls("netbox_routeros", "routerostype", detail=False)),
    ),
    path(
        "routeros/type/<int:pk>/",
        include(get_model_urls("netbox_routeros", "routerostype")),
    ),
    path(
        "routeros/type/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="routerostype_changelog",
        kwargs={"model": models.RouterosType},
    ),
    path(
        "routeros/instance/",
        include(get_model_urls("netbox_routeros", "routerosinstance", detail=False)),
    ),
    path(
        "routeros/instance/<int:pk>/",
        include(get_model_urls("netbox_routeros", "routerosinstance")),
    ),
    path(
        "routeros/instance/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="routerosinstance_changelog",
        kwargs={"model": models.RouterosInstance},
    ),
    # --- Iterfaces ---
    # interface list
    path(
        "interfaces/interface-list/",
        include(get_model_urls("netbox_routeros", "interfacelist", detail=False)),
    ),
    path(
        "interfaces/interface-list/<int:pk>/",
        include(get_model_urls("netbox_routeros", "interfacelist")),
    ),
    path(
        "interfaces/interface-list/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="interfacelist_changelog",
        kwargs={"model": models.InterfaceList},
    ),
    # --- CapsMan ---
    # instance
    path(
        "capsman/instance/",
        include(get_model_urls("netbox_routeros", "capsmaninstance", detail=False)),
    ),
    path(
        "capsman/instance/<int:pk>/",
        include(get_model_urls("netbox_routeros", "capsmaninstance")),
    ),
    path(
        "capsman/instance/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="capsmaninstance_changelog",
        kwargs={"model": models.CapsmanInstance},
    ),
    # server config
    path(
        "capsman/server-config/",
        include(get_model_urls("netbox_routeros", "capsmanserverconfig", detail=False)),
    ),
    path(
        "capsman/server-config/<int:pk>/",
        include(get_model_urls("netbox_routeros", "capsmanserverconfig")),
    ),
    path(
        "capsman/server-config/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="capsmanserverconfig_changelog",
        kwargs={"model": models.CapsmanServerConfig},
    ),
    # channel
    path(
        "capsman/channel/",
        include(get_model_urls("netbox_routeros", "capsmanchannel", detail=False)),
    ),
    path(
        "capsman/channel/<int:pk>/",
        include(get_model_urls("netbox_routeros", "capsmanchannel")),
    ),
    path(
        "capsman/channel/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="capsmanchannel_changelog",
        kwargs={"model": models.CapsmanChannel},
    ),
    # datapath
    path(
        "capsman/datapath/",
        include(get_model_urls("netbox_routeros", "capsmandatapath", detail=False)),
    ),
    path(
        "capsman/datapath/<int:pk>/",
        include(get_model_urls("netbox_routeros", "capsmandatapath")),
    ),
    path(
        "capsman/datapath/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="capsmandatapath_changelog",
        kwargs={"model": models.CapsmanDatapath},
    ),
]
