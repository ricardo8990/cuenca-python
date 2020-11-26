import datetime as dt

import pytest
from freezegun import freeze_time

from cuenca.exc import CuencaResponseException
from cuenca.http.client import Session


@pytest.mark.vcr
def test_invalid_auth():
    session = Session()
    session.configure(sandbox=False)
    with pytest.raises(CuencaResponseException) as e:
        session.post('/api_keys', dict())
    assert e.value.status_code == 401
    assert str(e.value)


@pytest.mark.usefixtures('cuenca_creds')
def test_basic_auth_configuration():
    session = Session()
    assert session.auth == session.basic_auth
    assert session.auth == ('api_key', 'secret')
    assert not session.jwt_token


@pytest.mark.vcr
@pytest.mark.usefixtures('cuenca_creds')
def test_configures_jwt():
    session = Session()
    session.configure(use_jwt=True)
    assert not session.auth
    assert session.jwt_token


@pytest.mark.vcr
@pytest.mark.usefixtures('cuenca_creds')
def test_request_valid_token():
    session = Session()
    # Set date when the cassette was created otherwise will retrieve
    # an expired token
    with freeze_time(dt.date(2020, 10, 22)):
        session.configure(use_jwt=True)
        response = session.get('/api_keys')
    assert response['items']


@pytest.mark.vcr
@pytest.mark.usefixtures('cuenca_creds')
def test_request_expired_token():
    session = Session()
    session.configure(use_jwt=True)
    previous_jwt = session.jwt_token
    with freeze_time(dt.datetime.utcnow() + dt.timedelta(days=40)):
        response = session.get('/api_keys')
    assert response['items']
    assert session.jwt_token != previous_jwt
