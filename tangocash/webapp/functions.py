from requests_html import HTMLSession
import requests
import json

from hashlib import md5

import uuid
import datetime

google_api_key = ''

def get_verification_code(username):
    # The code is the first 16 chars of the md5 hash of the username
    username_hash = md5(username.encode('utf-8'))
    return username_hash.hexdigest()[0:16]

def verfiy_localbitcoins(username, lbc_username):
    session = HTMLSession()
    # Fake user agent to reduce chance of getting seen as a bot
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0', }
    response = session.request(url=f'https://localbitcoins.com/accounts/profile/{lbc_username}/', method='GET', headers=headers)
    
    # If the profile is invalid it will redirect to home
    if response.html.next() == 'https://localbitcoins.com/':
        return False
    
    code_area = response.html.find('.overflow-catch', first=True)

    return code_area.text.find(get_verification_code(username)) != -1
    
def get_google_autocomplete_locations(location_string, session):
    session_id = _get_google_maps_platform_session_id(session)

    url = f'https://maps.googleapis.com/maps/api/place/autocomplete/json?input={location_string}&key={google_api_key}&sessiontoken={session_id}&types=(cities)'
    response = requests.get(url)

    if response.status_code == 200:
        response_body = json.loads(response.content.decode('utf-8'))
        if response_body['status'] == 'OK':            
            return response_body['predictions']

    return None

def get_google_location(place_id, session):
    session_id = _get_google_maps_platform_session_id(session)
    
    url = f'https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={google_api_key}&sessiontoken={session_id}&fields=geometry,formatted_address'
    response = requests.get(url)
    
    # A session ends after a series of autocomplete queries followed by a details request
    _clear_google_maps_platform_session_id(session)
    
    if response.status_code == 200:
        response_body = json.loads(response.content.decode('utf-8'))
        if response_body['status'] == 'OK':            
            return response_body['result']

    return None


def _get_google_maps_platform_session_id(session):
    """Get a unique session id to use to interact with the google maps platform api
    
    Takes the request.session argument from the user's request

    Automatically creates a new session id if the current session timeouts
    """
    # Try get google autocomplete session id for the user
    # If the user does not have the session id, create it and add an expiration time/start time
    # If the user does have the session id, check it hasn't expired
    
    # Before making requests, ensure the user has a google maps platform session that has not expired
    if (session.get('google_places_session_id', False)) and (datetime.datetime.now().timestamp() < session.get('google_places_expiration', datetime.datetime(1970,1,1).timestamp())):
        session_id = session['google_places_session_id']
        # print('using old gmp session')
        return session_id
    else:
        session_id = str(uuid.uuid4())
        session['google_places_session_id'] = session_id
        # Google maps platform sessions expire after a few minutes
        session['google_places_expiration'] = (datetime.datetime.now() + datetime.timedelta(seconds=120)).timestamp()
        # print('new gmp session created')
        return session_id

def _clear_google_maps_platform_session_id(session):
    """Clear the unique session id
    
    Takes the request.session argument from the user's request

    This should be done in order to close the session and ensure that new sessions use new session ids
    Otherwise, the old session might be used and result in extra charges
    """
    del session['google_places_session_id']
    del session['google_places_expiration']
    session.modified = True