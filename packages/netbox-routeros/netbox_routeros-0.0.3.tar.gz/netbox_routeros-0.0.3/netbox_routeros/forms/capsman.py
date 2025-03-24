from django import forms
from ipam.choices import VLANStatusChoices
from ipam.models import VLAN
from netbox.forms import NetBoxModelForm
from utilities.forms import fields

from netbox_routeros import models, validators
from netbox_routeros.models import proxy


class CapsmanInstanceForm(NetBoxModelForm):
    comments = fields.CommentField()
    routeros = forms.ModelChoiceField(
        queryset=models.RouterosInstance.objects.filter(capsman__isnull=True),
    )

    class Meta:
        model = models.CapsmanInstance
        fields = (
            "routeros",
            "description",
            "comments",
            "tags",
        )


class CapsmanServerConfigForm(NetBoxModelForm):
    comments = fields.CommentField()
    capsman = forms.ModelChoiceField(
        queryset=models.CapsmanInstance.objects.filter(server__isnull=True)
    )
    interface_lists = fields.DynamicModelMultipleChoiceField(
        queryset=models.InterfaceList.objects.all(),
        required=False,
        query_params={
            "capsman": "$capsman",
            "x_filter_fields": ("capsman",),
        },
    )
    interfaces = fields.DynamicModelMultipleChoiceField(
        queryset=proxy.Interface.objects.all(),  # TODO: try no proxy, override api url.
        required=False,
        query_params={
            "capsman": "$capsman",
            "x_filter_fields": ("capsman",),
        },
    )
    package_path = forms.CharField(
        max_length=255,
        required=False,
        validators=(validators.FilePathValidator(),),
    )

    class Meta:
        model = models.CapsmanServerConfig
        fields = (
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            self.fields["capsman"].queryset = models.CapsmanInstance.objects.filter(
                pk=self.instance.capsman.pk
            )
            self.fields["capsman"].disabled = True


class CapsmanChannelForm(NetBoxModelForm):
    comments = fields.CommentField()
    capsman = forms.ModelChoiceField(queryset=models.CapsmanInstance.objects.all())
    frequency = fields.NumericRangeArrayField(
        required=False,
        validators=[
            validators.ArrayValueValidator(
                validators.RangeValidator(validators.MinValueValidator(2300))
            ),
            validators.ArrayValueValidator(
                validators.RangeValidator(validators.MaxValueValidator(7300))
            ),
        ],
    )

    class Meta:
        model = models.CapsmanChannel
        fields = (
            "name",
            "capsman",
            "band",
            "channel_width",
            "frequency",
            "skip_dfs_channels",
            "description",
            "enabled",
            "comments",
            "tags",
        )


class CapsmanDatapathForm(NetBoxModelForm):
    comments = fields.CommentField()
    capsman = forms.ModelChoiceField(queryset=models.CapsmanInstance.objects.all())
    bridge = fields.DynamicModelChoiceField(
        queryset=proxy.Interface.objects.all(),  # TODO: try no proxy, override api url.
        required=False,
        query_params={
            "capsman": "$capsman",
            "type": "bridge",
            "x_filter_fields": ("capsman",),
        },
    )
    vlan = forms.ModelChoiceField(
        queryset=VLAN.objects.filter(status=VLANStatusChoices.STATUS_ACTIVE),
        required=False,
    )

    class Meta:
        model = models.CapsmanDatapath
        fields = (
            "name",
            "capsman",
            "bridge",
            "vlan",
            "description",
            "enabled",
            "comments",
            "tags",
        )
