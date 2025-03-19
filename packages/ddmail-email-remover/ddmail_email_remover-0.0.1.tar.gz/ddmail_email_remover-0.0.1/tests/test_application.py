from flask import current_app
import pytest
import os


def test_main_wrong_password(client, app):
    response_main_post = client.post("/", data={"password":"wrongpassword", "domain":"test.se", "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: wrong password" in response_main_post.data


def test_main_illigal_char_email(client, app, password):
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@test..se"})
    assert response_main_post.status_code == 200
    assert b"error: email validation failed" in response_main_post.data


def test_main_illigal_char_password(client, app):
    response_main_post = client.post("/", data={"password":"..password", "domain":"test.se", "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: password validation failed" in response_main_post.data


def test_main_illigal_char_domain(client, app, password):
    response_main_post = client.post("/", data={"password":password, "domain":"..test.se", "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: domain validation failed" in response_main_post.data


def test_main_not_matching_domain(client, app, password):
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@testtest.se"})
    assert response_main_post.status_code == 200
    assert b"error: email adress domain do not match domain" in response_main_post.data
