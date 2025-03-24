from netbox.api.routers import NetBoxRouter

from netbox_routeros.api import views
from netbox_routeros.api.views import proxy as proxy_views
from netbox_routeros.models import proxy

router = NetBoxRouter()
# Core
router.register("routeros/instance", views.RouterosInstanceViewSet)
router.register("routeros/type", views.RouterosTypeViewSet)
# Proxy
router.register(
    "proxy/dcim/interface",
    proxy_views.InterfaceViewSet,
    basename=proxy.Interface._meta.object_name.lower(),
)
# Interfaces
router.register("interfaces/interface-list", views.InterfaceListViewSet)
# CapsMan
router.register("capsman/instance", views.CapsmanInstanceViewSet)
router.register("capsman/server-config", views.CapsmanServerConfigViewSet)
router.register("capsman/channel", views.CapsmanChannelViewSet)
router.register("capsman/datapath", views.CapsmanDatapathViewSet)

urlpatterns = router.urls
