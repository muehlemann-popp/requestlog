from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.db import models

class RequestLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    ip_addr = models.GenericIPAddressField()
    url = models.TextField()
    session_key = models.CharField(max_length=40, null=True)
    method = models.CharField(max_length=16)
    headers = JSONField(null=True)
    query = JSONField(null=True)
    body = models.BinaryField(null=True)
    cookies = JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField(null=True)
    response_snippet = models.CharField(max_length=256, null=True, help_text='First 256 chars of the response.')

    def __unicode__(self):
        username = self.user and self.user.username or None
        return u'%s %s %s' % (username, self.ip_addr, self.url)
