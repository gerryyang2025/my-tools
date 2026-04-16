#!/usr/bin/env python3

"""
Tencent Meeting API - Query meeting info by Meeting Code
Docs: https://cloud.tencent.com/document/product/1095/93432
"""

import hashlib
import hmac
import base64
import time
import random
import json
import os
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw.strip(), 10)


def _normalize_meeting_code(raw: str) -> str:
    """Accept UI format like xxx-xxx-xxx; API expects digits only."""
    return raw.replace("-", "").replace(" ", "")


# ─────────────────────────────────────────
# Config: environment variables only (never hardcode secrets)
# ─────────────────────────────────────────
SECRET_ID  = os.environ.get("TENCENT_MEETING_SECRET_ID", "").strip()
SECRET_KEY = os.environ.get("TENCENT_MEETING_SECRET_KEY", "").strip()
# Organization AppId (Tencent Meeting Open Platform → Organization Info)
APP_ID = os.environ.get("TENCENT_MEETING_APP_ID", "").strip()
# SdkId for the app (optional; may be empty)
SDK_ID = os.environ.get("TENCENT_MEETING_SDK_ID", "").strip()

# Meeting Code to query: can be `xxx-xxx-xxx` or `xxxxxxxxx` (see _normalize_meeting_code)
MEETING_CODE_RAW = os.environ.get("TENCENT_MEETING_MEETING_CODE", "").strip()
MEETING_CODE = _normalize_meeting_code(MEETING_CODE_RAW)

# Operator info (must be a valid org member for auth)
OPERATOR_ID = os.environ.get("TENCENT_MEETING_OPERATOR_ID", "").strip()
# 1=userid, 2=openid, 3=rooms_id
OPERATOR_ID_TYPE = _env_int("TENCENT_MEETING_OPERATOR_ID_TYPE", 1)
# Client type, e.g. 0=PC (see official docs)
INSTANCE_ID = _env_int("TENCENT_MEETING_INSTANCE_ID", 0)

BASE_URL = os.environ.get("TENCENT_MEETING_BASE_URL", "https://api.meeting.qq.com").rstrip("/")
HTTP_TIMEOUT = _env_int("TENCENT_MEETING_HTTP_TIMEOUT", 10)


# ─────────────────────────────────────────
# Signature helpers
# Docs: https://cloud.tencent.com/document/product/1095/42413
# StringToSign = HTTPMethod + "\n"
#              + "X-TC-Key={SecretId}&X-TC-Nonce={Nonce}&X-TC-Timestamp={Timestamp}" + "\n"
#              + URI + "\n"
#              + RequestBody
# Signature = Base64( hex(HmacSHA256(StringToSign, SecretKey)) )
# ─────────────────────────────────────────
def generate_signature(
    secret_id: str,
    secret_key: str,
    http_method: str,
    timestamp: str,
    nonce: str,
    uri: str,
    body: str = "",
) -> str:
    header_string = f"X-TC-Key={secret_id}&X-TC-Nonce={nonce}&X-TC-Timestamp={timestamp}"
    string_to_sign = f"{http_method}\n{header_string}\n{uri}\n{body}"

    mac = hmac.new(
        secret_key.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    )
    hex_digest = mac.hexdigest()
    signature  = base64.b64encode(hex_digest.encode("utf-8")).decode("utf-8")
    return signature


def build_headers(
    secret_id: str,
    secret_key: str,
    http_method: str,
    uri: str,
    body: str = "",
    app_id: str = "",
    sdk_id: str = "",
) -> dict:
    timestamp = str(int(time.time()))
    nonce     = str(random.randint(10000, 99999999))
    signature = generate_signature(
        secret_id, secret_key, http_method.upper(), timestamp, nonce, uri, body
    )

    headers = {
        "Content-Type":    "application/json",
        "X-TC-Key":        secret_id,
        "X-TC-Timestamp":  timestamp,
        "X-TC-Nonce":      nonce,
        "X-TC-Signature":  signature,
        "X-TC-Registered": "1",
    }
    if app_id:
        headers["AppId"] = app_id
    if sdk_id:
        headers["SdkId"] = sdk_id

    return headers


# ─────────────────────────────────────────
# Core query
# ─────────────────────────────────────────
def query_meeting_by_code(meeting_code: str) -> dict:
    """
    Query meeting info by meeting_code and return the full JSON response.
    API: GET /v1/meetings?meeting_code=xxx
    Note: for signature, the URI must include the full query string.
    """
    uri_path = "/v1/meetings"
    params = {
        "meeting_code":     meeting_code,
        "operator_id":      OPERATOR_ID,
        "operator_id_type": OPERATOR_ID_TYPE,
        "instanceid":       INSTANCE_ID,
    }
    # Build a query-string-included URI for signing
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    uri_for_sign = f"{uri_path}?{query_string}"

    headers = build_headers(
        secret_id=SECRET_ID,
        secret_key=SECRET_KEY,
        http_method="GET",
        uri=uri_for_sign,
        body="",          # GET has no request body
        app_id=APP_ID,
        sdk_id=SDK_ID,
    )

    url      = BASE_URL + uri_path
    full_url = f"{url}?{urlencode(params)}"
    req      = Request(full_url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            status = resp.status
            raw    = resp.read().decode("utf-8")
    except HTTPError as e:
        status = e.code
        raw    = e.read().decode("utf-8")

    print(f"[HTTP {status}] GET {full_url}")
    return json.loads(raw)


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    required = (
        ("TENCENT_MEETING_SECRET_ID", SECRET_ID),
        ("TENCENT_MEETING_SECRET_KEY", SECRET_KEY),
        ("TENCENT_MEETING_OPERATOR_ID", OPERATOR_ID),
        ("TENCENT_MEETING_MEETING_CODE", MEETING_CODE_RAW),
    )
    missing = [name for name, val in required if not val]
    if missing:
        print(
            "Error: the following environment variables are missing or empty "
            "(provide them via environment or .env; do not hardcode):\n  "
            + "\n  ".join(missing),
            file=sys.stderr,
        )
        sys.exit(1)
    if not MEETING_CODE:
        print(
            "Error: TENCENT_MEETING_MEETING_CODE has no valid digits after removing dashes/spaces.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("=" * 55)
    print(f"Meeting Code: {MEETING_CODE_RAW}  (API param: {MEETING_CODE})")
    print("=" * 55)

    result = query_meeting_by_code(MEETING_CODE)
    print("\nFull response:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Extract meeting_id
    meetings = result.get("meeting_info_list") or result.get("meeting_list") or []
    if meetings:
        for meeting in meetings:
            meeting_id = meeting.get("meeting_id", "N/A")
            subject    = meeting.get("subject",    "N/A")
            status     = meeting.get("status",     "N/A")
            print("\n─────────────────────────────────")
            print(f"  meeting_id : {meeting_id}")
            print(f"  subject    : {subject}")
            print(f"  status     : {status}")
            print("─────────────────────────────────")
    else:
        err_code = result.get("error_info", {}).get("error_code") or result.get("error_code")
        err_msg  = result.get("error_info", {}).get("message")    or result.get("message")
        print(f"\nNo meeting found. error_code: {err_code}, message: {err_msg}")


if __name__ == "__main__":
    main()