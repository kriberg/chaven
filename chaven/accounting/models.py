from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
import pytz


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

    def get_security_object(self):
        return {}


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


class AccessClaimManager(models.Manager):
    def check_access(self, public_info):
        '''
        Finds any valid claim matching a character's public info from the
        xmlapi

        :param public_info: xmlapi info from CharacterAffiliation
        :return: all valid claims
        '''
        return self.filter(valid_until__gt=timezone.now()).filter(
            (
                Q(entity_type=AccessClaim.CHARACTER) &
                Q(entityID=getattr(public_info, 'characterID')) &
                Q(name=getattr(public_info, 'characterName'))
            ) |
            (
                Q(entity_type=AccessClaim.CORPORATION) &
                Q(entityID=getattr(public_info, 'corporationID')) &
                Q(name=getattr(public_info, 'corporationName'))
            ) |
            (
                Q(entity_type=AccessClaim.ALLIANCE) &
                Q(entityID=getattr(public_info, 'allianceID')) &
                Q(name=getattr(public_info, 'allianceName'))
            ) |
            (
                Q(entity_type=AccessClaim.FACTION) &
                Q(entityID=getattr(public_info, 'factionID')) &
                Q(name=getattr(public_info, 'factionName'))
            )
        )
    def check_access_token(self, token):
        '''
        Find any access claim from a one-time token

        :param token: access token
        :return: all valid claims
        '''

        return self.filter(valid_until__gt=timezone.now(),
                           entity_type=AccessClaim.TOKEN,
                           name=token)


class AccessClaim(models.Model):
    CHARACTER = 0
    CORPORATION = 1
    ALLIANCE = 2
    FACTION = 3
    TOKEN = 4

    VERY_LONG_TIME = timezone.datetime(2099, 12, 31, tzinfo=pytz.UTC)

    ENTITY_TYPE = (
        (CHARACTER, 'Character'),
        (CORPORATION, 'Corporation'),
        (ALLIANCE, 'Alliance'),
        (FACTION, 'Faction'),
        (TOKEN, 'Token'),
    )

    entity_type = models.SmallIntegerField(choices=ENTITY_TYPE)
    name = models.CharField(max_length=255)
    entityID = models.BigIntegerField(null=True)
    valid_until = models.DateTimeField(default=VERY_LONG_TIME)

    objects = AccessClaimManager()
