from django.db import models
from django.contrib.auth import get_user_model


class RequestLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    ip_addr = models.GenericIPAddressField()
    url = models.TextField()
    session_key = models.CharField(max_length=40, null=True)
    method = models.CharField(max_length=16)
    headers = models.JSONField(null=True)
    query = models.JSONField(null=True)
    body = models.BinaryField(null=True)
    body_parsed = models.JSONField(null=True)
    cookies = models.JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField(null=True)
    response_snippet = models.CharField(max_length=256, null=True, help_text='First 256 chars of the response.')

    def __str__(self):
        username = self.user and getattr(self.user, self.user.USERNAME_FIELD) or None
        return f'{username} {self.ip_addr} {self.url}'
