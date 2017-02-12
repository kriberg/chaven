from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField


class Capsuler(AbstractUser):
    settings = JSONField(blank=True, default={})
    owner_hash = models.CharField(max_length=255, null=True)
    claims = models.ManyToManyField('AccessClaim')

    def __unicode__(self):
        return self.username

    def get_active_keys(self):
        return APIKey.objects.filter(owner=self.pk, expired=False)

    def is_owner(self, obj):
        if type(obj.owner) is Capsuler:
            return obj.owner == self
        else:
            return obj.owner.owner == self


class APIKey(models.Model):
    KEY_TYPES = (
        ('Account', 'Account'),
        ('Character', 'Character'),
        ('Corporation', 'Corporation')
    )

    name = models.CharField(max_length=100)
    keyID = models.CharField(max_length=20)
    vCode = models.CharField(max_length=128)
    accessMask = models.IntegerField(null=True, editable=False)
    type = models.CharField(max_length=11, choices=KEY_TYPES, editable=False, null=True)
    expired = models.BooleanField(default=False, editable=False)
    expires = models.DateTimeField(editable=False, null=True)
    brokeness = models.IntegerField(default=0)
    characterID = models.BigIntegerField(null=True, blank=True)
    corporationID = models.BigIntegerField(null=True, blank=True)
    characterIDs = JSONField(null=True, default=[])

    owner = models.ForeignKey(Capsuler)

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.keyID)


class AccessClaim(models.Model):
    ENTITY_TYPE = (
        (0, 'Character'),
        (1, 'Corporation'),
        (2, 'Alliance')
    )

    entity_type = models.SmallIntegerField(choices=ENTITY_TYPE)
    name = models.CharField(max_length=255)
    entityID = models.BigIntegerField(null=True)

