from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    """One to many relation, one user many items."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    item_name = models.CharField(max_length=250, null=False, blank=False)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        """Set as default item_name."""
        return self.item_name
