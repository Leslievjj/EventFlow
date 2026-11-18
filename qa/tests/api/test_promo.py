import time

import pytest
import requests

URL = "http://localhost:8000"


def get_token():
    r = requests.post(
        URL + "/api/auth/token",
        data={
            "username": "admin@eventflow.test",
            "password": "admin1234",
        },
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_1():
    token = get_token()
    h = {"Authorization": "Bearer " + token}

    r = requests.post(
        URL + "/api/admin/promo",
        headers=h,
        json={
            "code": "TEST" + str(int(time.time())),
            "percent_off": 20,
            "max_uses": 5,
        },
    )

    assert r.status_code == 201


def test_promo2():
    token = get_token()
    h = {"Authorization": "Bearer " + token}

    r = requests.get(URL + "/api/admin/promo", headers=h)
    assert r.status_code == 200

    promos = r.json()
    for p in promos:
        if p["code"] == "WELCOME10":
            assert p["percent_off"] == 10
            return

    pytest.fail("La promoción WELCOME10 no existe")


def test_disable_promo():
    token = get_token()
    h = {"Authorization": "Bearer " + token}

    r = requests.post(
        URL + "/api/admin/promo",
        headers=h,
        json={
            "code": "DIS" + str(int(time.time())),
            "percent_off": 5,
            "max_uses": 1,
        },
    )

    assert r.status_code == 201

    promo_id = r.json()["id"]

    r2 = requests.post(
        URL + "/api/admin/promo/" + str(promo_id) + "/disable",
        headers=h,
    )

    assert r2.json()["expires_at"] is not None


def test_client_cant_see_promos():
    r = requests.post(
        URL + "/api/auth/token",
        data={
            "username": "client@eventflow.test",
            "password": "client1234",
        },
    )

    assert r.status_code == 200

    token = r.json()["access_token"]

    r = requests.get(
        URL + "/api/admin/promo",
        headers={"Authorization": "Bearer " + token},
    )

    assert r.status_code == 403
