from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms import fields

from netbox_routeros import models
from netbox_routeros.models import proxy


class InterfaceListForm(NetBoxModelForm):
    comments = fields.CommentField()
    routeros = forms.ModelChoiceField(queryset=models.RouterosInstance.objects.all())
    interfaces = fields.DynamicModelMultipleChoiceField(
        queryset=proxy.Interface.objects.all(),  # TODO: try no proxy, override api url.
        required=False,
        query_params={
            "routeros": "$routeros",
            "x_filter_fields": ("routeros",),
        },
    )

    class Meta:
        model = models.InterfaceList
        fields = (
            "routeros",
            "name",
            "interfaces",
            "description",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            self.fields["routeros"].queryset = models.RouterosInstance.objects.filter(
                pk=self.instance.routeros.pk
            )
            self.fields["routeros"].disabled = True
