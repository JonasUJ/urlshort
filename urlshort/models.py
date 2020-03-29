from django.db import models
from django.contrib.auth.hashers import check_password, make_password


class SafeState(models.IntegerChoices):
    NO = 0
    YES = 1
    UNKNOWN = 2


class ShortUrlKey(models.Model):
    keyhash = models.CharField(max_length=100)

    def matches(self, key):
        return check_password(key, self.keyhash)

    def set_key(self, key):
        self.keyhash = make_password(key)
        self.save()


class ShortUrlActive(models.Model):
    is_active = models.BooleanField(default=True)
    reason = models.CharField(max_length=256, default='')
    deactivated_since = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{type(self).__name__}(is_active={self.is_active}, reason={self.reason})'


class ShortUrl(models.Model):
    link = models.URLField()
    name = models.CharField(max_length=48, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    uses = models.IntegerField(default=0)
    is_safe = models.IntegerField(
        choices=SafeState.choices, default=SafeState.UNKNOWN)
    urlkey = models.ForeignKey(
        ShortUrlKey, on_delete=models.CASCADE, blank=True, null=True)
    active = models.ForeignKey(ShortUrlActive, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return self.link

    def __str__(self):
        return self.name
