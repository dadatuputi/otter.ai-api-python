import requests
import base64

API_BASE_URL = 'https://otter.ai/forward/api/v1'
CSRF_COOKIE_NAME = 'csrftoken'

class OtterSession:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()

    def is_logged_in(self):
        return 'sessionid' in self.session.cookies.keys()

    def login(self):
        _r_csrf = self.session.get(API_BASE_URL + '/login_csrf')
        assert CSRF_COOKIE_NAME in _r_csrf.cookies.keys()
        _csrf_token = _r_csrf.cookies[CSRF_COOKIE_NAME]

        _login_b64 = base64.b64encode('{}:{}'.format(self.email, self.password).encode('utf-8')).decode()
        self.session.headers.update({'authorization': 'Basic {}'.format(_login_b64)})
        self.session.headers.update({'x-csrftoken': _csrf_token})

        _r_login = self.session.get(API_BASE_URL + '/login', params={'username': self.email})
        if _r_login.status_code is not 200:
            raise NotLoggedInError()

        # Get user data
        self.user = _r_login.json()['user']

        return _r_login

    def get_speeches(self):
        if not self.is_logged_in():
            self.login()

        _r_speeches = self.session.get(API_BASE_URL + '/speeches', params={'userid': self.user['id']})
        return _r_speeches.json()['speeches']
        
    def get_speech(self, speech_id):
        if not self.is_logged_in():
            self.login()

        _r_speech = self.session.get(API_BASE_URL + '/speech', params={'speech_id': speech_id, 'userid': self.user['id']})
        return _r_speech.json()['speech']

    def search_speech(self, query):
        if not self.is_logged_in():
            self.login()

        _r_query = self.session.get(API_BASE_URL + '/speech_search', params={'query': query, 'userid': self.user['id']})
        return _r_query.json()['hits']

class NotLoggedInError(Exception):
    """Base class for exceptions in this module."""
    pass
