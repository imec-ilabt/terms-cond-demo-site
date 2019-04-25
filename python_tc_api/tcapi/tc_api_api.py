from urllib.parse import unquote

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.extensions import SubjectAlternativeName
from cryptography.x509.oid import ExtensionOID
from cryptography.x509.general_name import UniformResourceIdentifier

from datetime import datetime, timedelta, timezone
from typing import Optional, Callable

import pytz
from dateutil.tz import tz
import dateutil.parser

import tcapi

from flask import request, Response, jsonify, abort, redirect, url_for, current_app, Blueprint, g, app

import sqlite3

import tcapi.db as tc_db

tcapi_blueprint = Blueprint('tcapi', __name__)


HEADER_ESCAPED_CERT = "X-Ssl-Client-Escaped-Cert"


def _is_authenticated() -> bool:
    res = _get_authenticated_user_urn()
    if res.startswith('urn:'):
        return True
    return False


def _get_authenticated_user_urn():
    escaped_header = request.headers.get(HEADER_ESCAPED_CERT, None)
    if not escaped_header:
        return None
    raw_pem: bytes = unquote(escaped_header).encode()
    if not raw_pem:
        return None
    cert = x509.load_pem_x509_certificate(raw_pem, default_backend())
    if not cert:
        return None
    ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
    if not ext:
        return None
    san: SubjectAlternativeName = ext.value
    if not san:
        return None
    assert isinstance(san, SubjectAlternativeName)
    urns = san.get_values_for_type(UniformResourceIdentifier)
    if not urns:
        return None
    return urns[0]


@tcapi_blueprint.route('/')
def index():
    return jsonify({
        'accept': request.url+'accept',
        'version': tcapi.__version__,
        # 'debug': request.url+'debug',
    })


@tcapi_blueprint.route('/version', methods=['GET'])
def version_info():
    return jsonify({
        'version': tcapi.__version__
    })


@tcapi_blueprint.route('/accept', methods=['GET'])
def get_accept():
    user_urn = _get_authenticated_user_urn()
    if not user_urn:
        return Response(response='Not authenticated', status=401)

    res = tc_db.find_accept(user_urn)
    if res:
        if 'until' not in res or not res['until']:
            return Response(response='DB entry has no until', status=500)
        if 'user' not in res or not res['user']:
            return Response(response='DB entry has no user', status=500)
        if 'main_accept' not in res:
            return Response(response='DB entry has no main_accept', status=500)
        now = datetime.now(timezone.utc)
        until = dateutil.parser.parse(res['until'])
        if not until:
            return Response(response='Failed to parse until date "{}"'.format(res['until']), status=500)
        res['testbed_access'] = res['main_accept'] and now < until
        return jsonify(res)
    else:
        return jsonify({
            'user': user_urn,
            'main_accept': False,
            'testbed_access': False,
            'until': datetime.now(timezone.utc).isoformat(),
        })
        # Less informative alternative:
        # return Response(response='No info', status=404)


@tcapi_blueprint.route('/accept', methods=['PUT'])
def register_accept():
    req = request.get_json()
    if not req:
        return Response(response='Expected JSON accept object in request', status=400)
    if not 'main_accept' in req or not isinstance(req['main_accept'], bool):
        return Response(response='JSON accept object in request should contain bool "main_accept"', status=400)
    if 'user' in req:
        return Response(response='user is not allowed in request (it is known already)', status=400)
    if 'until' in req:
        return Response(response='until is not allowed in request (it is generated automatically)', status=400)
    if 'testbed_access' in req:
        return Response(response='testbed_access is not allowed in request (it is generated automatically)', status=400)

    user_urn = _get_authenticated_user_urn()
    if not user_urn:
        return Response(response='Not authenticated', status=401)

    if req['main_accept']:
        until = (datetime.now(timezone.utc) + timedelta(days=31*6)).isoformat()
    else:
        until = (datetime.now(timezone.utc)).isoformat()
    tc_db.register_accept(user_urn, until, req['main_accept'])

    return Response(status=204)


@tcapi_blueprint.route('/accept', methods=['DELETE'])
def register_delete():
    user_urn = _get_authenticated_user_urn()
    if not user_urn:
        return Response(response='Not authenticated', status=401)

    tc_db.delete_accept(user_urn)

    return Response(status=204)


@tcapi_blueprint.route('/debug', methods=['GET'])
def show_debug_info():
    all_headers = {}
    for key, value in request.headers:
        all_headers[str(key)] = str(value)

    return jsonify({
        'is_authenticated': _is_authenticated(),
        'authenticated_user_urn': _get_authenticated_user_urn(),
        "Raw-Headers": all_headers
    })
