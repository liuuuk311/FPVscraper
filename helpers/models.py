from django.db import models


class BaseModel(models.Model):
    """The base model that every other model should extends"""

    created_at = models.DateTimeField(auto_now=True, auto_created=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True