from dcim.models import Interface
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import PrimaryModel
from utilities.choices import ChoiceSet

from netbox_routeros import validators

from .interface import InterfaceList
from .routeros import RouterosInstance


class CapsmanInstance(PrimaryModel):
    routeros = models.OneToOneField(
        to=RouterosInstance,
        on_delete=models.CASCADE,
        related_name="capsman",
    )

    class Meta:
        ordering = ("routeros",)

    def __str__(self):
        return str(self.routeros)

    def get_absolute_url(self):
        return reverse("plugins:netbox_routeros:capsmaninstance", args=[self.pk])


class PeerUpgradePolicyChoices(ChoiceSet):
    NONE = "none"
    REQUIRE_SAME_VERSION = "require same version"
    SUGGEST_SAME_VERSION = "suggest same version"

    CHOICES = (
        (NONE, _("none")),
        (REQUIRE_SAME_VERSION, _("require same version")),
        (SUGGEST_SAME_VERSION, _("suggest same version")),
    )


class CapsmanServerConfig(PrimaryModel):
    capsman = models.OneToOneField(
        to=CapsmanInstance,
        on_delete=models.CASCADE,
        related_name="server",
    )
    enabled = models.BooleanField(verbose_name=_("enabled"), default=True)
    interface_lists = models.ManyToManyField(
        to=InterfaceList,
        # TODO: limit_choices_to=
        related_name="+",
        blank=True,
        symmetrical=False,
    )
    interfaces = models.ManyToManyField(
        to=Interface,
        # TODO: limit_choices_to=
        related_name="+",
        blank=True,
        symmetrical=False,
    )
    # TODO: CA certificate
    # TODO: certificate
    # TODO: require peer certificate
    package_path = models.CharField(
        verbose_name=_("Package path"),
        max_length=255,
        validators=(validators.FilePathValidator(),),
        blank=True,
        null=True,
    )
    upgrade_policy = models.CharField(
        verbose_name=_("Upgrade policy"),
        max_length=50,
        choices=PeerUpgradePolicyChoices,
        default=PeerUpgradePolicyChoices.SUGGEST_SAME_VERSION,
    )

    class Meta:
        ordering = ("capsman",)

    def __str__(self):
        return str(self.capsman)

    def get_absolute_url(self):
        return reverse("plugins:netbox_routeros:capsmanserverconfig", args=[self.pk])


class CapsmanDatapath(PrimaryModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=64, db_collation="natural_sort"
    )
    capsman = models.ForeignKey(
        to=CapsmanInstance,
        on_delete=models.CASCADE,
        related_name="datapaths",
    )
    bridge = models.ForeignKey(
        to=Interface,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    vlan = models.ForeignKey(
        to="ipam.vlan",
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    enabled = models.BooleanField(verbose_name=_("enabled"), default=True)

    class Meta:
        ordering = ("capsman", "name")
        unique_together = ("capsman", "name")

    def __str__(self):
        return f"{self.name} at {self.capsman}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_routeros:capsmandatapath", args=[self.pk])


class WirelessBandChoices(ChoiceSet):
    BAND_2GHZ_AX = "2GHz AX"
    BAND_2GHZ_G = "2GHz G"
    BAND_2GHZ_N = "2GHz N"
    BAND_5GHZ_A = "5GHz A"
    BAND_5GHZ_A_N = "5GHz A/N"
    BAND_5GHZ_AC = "5GHz AC"
    BAND_5GHZ_AX = "5GHz AX"

    CHOICES = (
        (BAND_2GHZ_AX, _("2GHz AX")),
        (BAND_2GHZ_G, _("2GHz G")),
        (BAND_2GHZ_N, _("2GHz N")),
        (BAND_5GHZ_A, _("5GHz A")),
        (BAND_5GHZ_A_N, _("5GHz A/N")),
        (BAND_5GHZ_AC, _("5GHz AC")),
        (BAND_5GHZ_AX, _("5GHz AX")),
    )


class WirelessChannelWidthChoices(ChoiceSet):
    WIDTH_20MHZ = "20MHz"
    WIDTH_20_40MHZ = "20/40MHz"
    WIDTH_20_40MHZ_CE = "20/40MHz Ce"
    WIDTH_20_40MHZ_EC = "20/40MHz eC"
    WIDTH_20_40_80MHZ = "20/40/80MHz"
    WIDTH_20_40_80_160MHZ = "20/40/80/160MHz"
    WIDTH_20_40_80_80MHZ = "20/40/80+80MHz"

    CHOICES = (
        (WIDTH_20MHZ, _("20MHz")),
        (WIDTH_20_40MHZ, _("20/40MHz")),
        (WIDTH_20_40MHZ_CE, _("20/40MHz Ce")),
        (WIDTH_20_40MHZ_EC, _("20/40MHz eC")),
        (WIDTH_20_40_80MHZ, _("20/40/80MHz")),
        (WIDTH_20_40_80_160MHZ, _("20/40/80/160MHz")),
        (WIDTH_20_40_80_80MHZ, _("20/40/80+80MHz")),
    )


class SkipDFSChannelsChoices(ChoiceSet):
    SKIP_DFS_CHANNELS_DISABLED = "Disabled"
    SKIP_DFS_CHANNELS_ALL = "All"
    SKIP_DFS_CHANNELS_10_MIN_CAC = "10min CAC"

    CHOICES = (
        (SKIP_DFS_CHANNELS_DISABLED, _("Disabled")),
        (SKIP_DFS_CHANNELS_ALL, _("All")),
        (SKIP_DFS_CHANNELS_10_MIN_CAC, _("10min CAC")),
    )


class CapsmanChannel(PrimaryModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=64, db_collation="natural_sort"
    )
    capsman = models.ForeignKey(
        to=CapsmanInstance,
        on_delete=models.CASCADE,
        related_name="channels",
    )
    band = models.CharField(
        verbose_name=_("Band"),
        max_length=50,
        choices=WirelessBandChoices,
        blank=True,
        null=True,
    )
    channel_width = models.CharField(
        verbose_name=_("Channel width"),
        max_length=50,
        choices=WirelessChannelWidthChoices,
        blank=True,
        null=True,
    )
    frequency = ArrayField(
        IntegerRangeField(
            blank=True,
            null=True,
            validators=[
                validators.IncreasingRangeValidator(),
                validators.RangeValidator(validators.MinValueValidator(2300)),
                validators.RangeValidator(validators.MaxValueValidator(7300)),
            ],
        ),
        verbose_name=_("Frequency"),
        blank=True,
        null=True,
    )
    skip_dfs_channels = models.CharField(
        verbose_name=_("Skip DFS Channels"),
        max_length=50,
        choices=SkipDFSChannelsChoices,
        blank=True,
        null=True,
    )
    enabled = models.BooleanField(verbose_name=_("enabled"), default=True)

    class Meta:
        ordering = ("capsman", "name")
        unique_together = ("capsman", "name")

    def __str__(self):
        return f"{self.name} at {self.capsman}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_routeros:capsmanchannel", args=[self.pk])
