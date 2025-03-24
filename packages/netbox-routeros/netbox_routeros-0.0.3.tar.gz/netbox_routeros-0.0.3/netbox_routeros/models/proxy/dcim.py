from dcim import models


class Interface(models.Interface):
    class Meta:
        proxy = True
