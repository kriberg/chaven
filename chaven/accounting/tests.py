from django.test import TestCase
from .authentication import authorize_sso_character, UnauthorizedAccess
from chaven.xmlapi import DjangoCache
from .models import AccessClaim, Capsuler


class AuthorizeSSOViewTest(TestCase):
    class APITimer(object):
        cachedUntil = 360
        currentTime = 0

    def setUp(self):
        cache = DjangoCache()
        cache.store(
            'api.eveonline.com',
            '/eve/CharacterAffiliation.xml.aspx',
            {'ids': 941287462},
            '''<?xml version='1.0' encoding='UTF-8'?>
<eveapi version="2">
  <currentTime>2017-02-15 20:19:41</currentTime>
  <result>
    <rowset name="characters" key="characterID" columns="characterID,characterName,corporationID,corporationName,allianceID,allianceName,factionID,factionName">
      <row characterID="941287462" characterName="Vittoros" corporationID="144749962" corporationName="Evolution" allianceID="1727758877" allianceName="Northern Coalition." factionID="0" factionName="" />
    </rowset>
  </result>
  <cachedUntil>2017-02-15 20:30:12</cachedUntil>
</eveapi>''',
            self.APITimer()
        )
        self.charinfo = {
            u'Scopes': u'',
            u'ExpiresOn': u'2017-02-15T20:29:13',
            u'TokenType': u'Character',
            u'CharacterName': u'Vittoros',
            u'IntellectualProperty': u'EVE',
            u'CharacterOwnerHash': u'hunter2=',
            u'CharacterID': 941287462
        }

    def test_authorization_step(self):
        self.assertRaises(UnauthorizedAccess,
                          lambda: authorize_sso_character(self.charinfo))

        self.assertRaises(Capsuler.DoesNotExist,
                          lambda: Capsuler.objects.get(username=u'Vittoros'))

        for entity_type, name, entity_id, msg in (
                (AccessClaim.CHARACTER, u'Vittoros', 941287462, 'Character Access Claim'),
                (AccessClaim.CORPORATION, u'Evolution', 144749962, 'Corporation Access Claim'),
                (AccessClaim.ALLIANCE, u'Northern Coalition.', 1727758877, 'Alliance Access Claim'),
                (AccessClaim.FACTION, u'', 0, 'Faction Access Claim'),
        ):
            claim = AccessClaim(entity_type=entity_type,
                                     name=name,
                                     entityID=entity_id)
            claim.save()
            token = authorize_sso_character(self.charinfo)
            self.assertIsNotNone(token, msg=msg)
            capsuler = Capsuler.objects.get(username=u'Vittoros')
            self.assertEquals(capsuler.claims.all().count(), 1)
            claim.delete()
            self.assertEquals(capsuler.claims.all().count(), 0)

        claim = AccessClaim(entity_type=AccessClaim.TOKEN,
                            name='cheesecake')
        claim.save()
        token = authorize_sso_character(self.charinfo, token='cheesecake')
        self.assertIsNotNone(token, msg='Token Access Claim')
        capsuler = Capsuler.objects.get(username=u'Vittoros')
        self.assertEquals(capsuler.claims.all().count(), 1)
        claim.delete()
        self.assertEquals(capsuler.claims.all().count(), 0)
        capsuler.delete()

        for entity_type, name, entity_id in (
                (AccessClaim.CHARACTER, u'Vittoros', 941287462),
                (AccessClaim.CORPORATION, u'Evolution', 144749962),
                (AccessClaim.ALLIANCE, u'Northern Coalition.', 1727758877),
        ):
            claim = AccessClaim(entity_type=entity_type,
                                     name=name,
                                     entityID=entity_id)
            claim.save()

        token = authorize_sso_character(self.charinfo)
        self.assertIsNotNone(token, 'Multiple Access Claims')
        capsuler = Capsuler.objects.get(username=u'Vittoros')
        self.assertEquals(capsuler.claims.all().count(), 3)
        AccessClaim.objects.get(entity_type=AccessClaim.CHARACTER,
                                entityID=941287462,
                                name=u'Vittoros').delete()
        self.assertEquals(capsuler.claims.all().count(), 2)

        AccessClaim.objects.all().delete()
        self.assertRaises(UnauthorizedAccess,
                          lambda: authorize_sso_character(self.charinfo))
