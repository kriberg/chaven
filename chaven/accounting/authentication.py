from rest_framework_jwt.settings import api_settings
from .models import Capsuler, AccessClaim
from chaven.xmlapi import get_api
import logging


log = logging.getLogger('chaven')


class UnauthorizedAccess(BaseException):
    '''
    Exception raised when an eve sso user is not allowed to log in.
    '''
    pass


def jwt_response_payload_handler(token, user=None, request=None):
    if user is not None:
        sec = user.get_security_object()
    else:
        sec = {}
    return {
        'token': token,
        'sec': sec
    }


def authorize_sso_character(charinfo, token=None):
    '''
    Runs the authentication and authorization chain with the SSO character info

    :param charinfo:
    :return:
    '''
    name = charinfo.get('CharacterName')
    character_id = charinfo.get('CharacterID')
    owner_hash = charinfo.get('CharacterOwnerHash')

    if not all((name, character_id, owner_hash)):
        raise UnauthorizedAccess('Could not verify character with info "{}"' \
                                 .format(charinfo))

    # Try to find an account first, if not create
    try:
        capsuler = Capsuler.objects.get(username=name)
    except Capsuler.DoesNotExist:
        capsuler = Capsuler(username=name,
                            owner_hash=owner_hash)

    # When we have the account, chech tke owner hash
    if capsuler.owner_hash != owner_hash:
        log.warning('Character "{}" changed owner hash!'.format(
            name
        ))
        # We delete the capsuler first, so we are sure it delete
        # all connected data. Then we re-create.
        capsuler.delete()
        capsuler = Capsuler(username=name,
                            owner_hash=owner_hash)


    public_info = get_public_character_info(character_id)
    log.debug('CharacterAffiliation {}'.format(public_info))

    claims = check_access_eligibility(public_info, capsuler, token)

    if not claims.count() > 0:
        raise UnauthorizedAccess('Capsuler is not eligible to log in')

    capsuler.save()

    capsuler.claims.set(claims)

    return get_jwt_token(capsuler)


def get_jwt_token(capsuler):
    '''
    Creates security object and generates the JWT token.
    :param capsuler:
    :return:
    '''
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(capsuler)
    token = jwt_encode_handler(payload)

    return token


def get_public_character_info(characterID):
    '''
    Retrieves the public character information from CharacterAffiliation
    endpoint in the xmlapi.

    :param characterID:
    :return:
    '''
    api = get_api()
    resp = api.eve.CharacterAffiliation(ids=characterID)

    if len(resp.characters) != 1:
        log.error('CharacterID {} returned multiple entries from xmlapi'.format(characterID))
        raise UnauthorizedAccess('EVE xmlapi error')

    return resp.characters[0]


def check_access_eligibility(public_info, capsuler, token=None):
    '''
    Finds, if any, valid access claims for the authenticated capsuler.

    :param public_info:
    :param capsuler:
    :param token:
    :return:
    '''
    if token is not None:
        return AccessClaim.objects.check_access_token(token)

    return AccessClaim.objects.check_access(public_info)
