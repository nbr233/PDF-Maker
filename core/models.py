import uuid
import os
from django.db import models

class ProcessedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='processed/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    tool_used = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tool_used} - {self.original_name}"

    @property
    def filename(self):
        return os.path.basename(self.file.name)
