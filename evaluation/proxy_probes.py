"""Scenarios I1, I3 and I4: requests the custodian's proxy must refuse.

Run inside the coordinator's executor container, which reaches the enclave over vsock and the proxy
through the platform's tunnel relay:

    docker exec -i -e PROBE_JOB_ID=<job id> -e PROBE_WORKSPACE_ID=<workspace id> \
        -e PROBE_DATASET_ID=<project id> -e PROBE_ARCHETYPE_ID=<archetype id> \
        coordinator-executor-worker-1 python - < proxy_probes.py

The job and workspace identify an existing job of the approved researcher; the platform uses them to
return the tunnel port, the request-signing token and the query, exactly as it does for a job.

Each case sends one request to the proxy and prints the HTTP status and the proxy's error code. No
request in this script can obtain data: every request that carries an acceptable attestation document
also carries a query the proxy's validator blocks. The signing token and the attestation documents are
never printed. Set PROBE_SKIP_STALE=1 to leave out the case that waits five and a half minutes.

Expected:
  SIG  wrong request signature                         401 SIGNATURE_INVALID
  I1   no attestation document                         403 ATTESTATION_REQUIRED
  I3   genuine document, another session's public key  403 PCR_MISMATCH
  I4a  genuine document, used a second time            403 ATTESTATION_REPLAYED
  I4b  genuine document, older than five minutes       403 ATTESTATION_STALE
"""
import hashlib
import hmac
import json
import logging
import os
import time

import requests

from workers.executor.constants import EnclaveOperations
from workers.executor.factories import EnclaveClientFactory, MiddlewareClientFactory
from workers.executor.interfaces import MiddlewareRequest
from workers.executor.settings import get_settings

logging.disable(logging.CRITICAL)

JOB_ID = os.environ["PROBE_JOB_ID"]
WORKSPACE_ID = os.environ["PROBE_WORKSPACE_ID"]
DATASET_ID = os.environ["PROBE_DATASET_ID"]
ARCHETYPE_ID = os.environ["PROBE_ARCHETYPE_ID"]
BLOCKED_QUERY = "DELETE FROM patients"
STALE_WAIT_SECONDS = 330


def field(info, name):
    return info.get(name) if isinstance(info, dict) else getattr(info, name, None)


def new_session(enclave, label):
    public_key, session_id = enclave.get_public_key(label)
    response = enclave._send_to_enclave({"operation": EnclaveOperations.GET_ATTESTATION, "session_id": session_id})
    document = (response.get("attestation") or {}).get("attestation_document", "")
    if not document:
        raise SystemExit(f"The enclave issued no attestation document for {label}")
    return public_key, document


def send(url, token, case, sql_query, public_key, document, wrong_signature=False):
    timestamp = str(int(time.time()))
    request_id = f"probe-{case}-{timestamp}"
    signed = hmac.new(token.encode(), (request_id + timestamp).encode(), hashlib.sha256).hexdigest()
    if wrong_signature:
        signed = "0" * len(signed)
    payload = {
        "request_id": request_id,
        "session_id": "",
        "sql_query": sql_query,
        "enclave_public_key": public_key,
        "attestation_document": document,
        "timestamp": int(timestamp),
    }
    response = requests.post(url, json=payload, headers={"X-Signature": signed, "X-Request-ID": request_id}, timeout=120)
    try:
        body = response.json()
    except ValueError:
        body = {}
    return {
        "case": case,
        "request_id": request_id,
        "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "http_status": response.status_code,
        "success": body.get("success"),
        "error": body.get("error"),
        "message": body.get("message"),
        "data_returned": bool(body.get("encrypted_csv")),
    }


def report(result, expected_status, expected_error):
    result["expected"] = f"{expected_status} {expected_error}"
    result["as_expected"] = result["http_status"] == expected_status and result["error"] == expected_error
    print(json.dumps(result))


def main():
    settings = get_settings()
    enclave = EnclaveClientFactory.create_client(settings)
    middleware = MiddlewareClientFactory.create_client(settings)

    key_a, document_a = new_session(enclave, "PROBE-A")
    key_b, _ = new_session(enclave, "PROBE-B")

    response = middleware.fetch_encrypted_csv(MiddlewareRequest(
        dataset_id=DATASET_ID, archetype_id=ARCHETYPE_ID, public_key=key_a,
        job_id=JOB_ID, workspace_id=WORKSPACE_ID,
    ))
    info = response.proxy_info
    if not response.success or not info:
        raise SystemExit("The platform did not return proxy details; is the project in the Proxy configuration?")
    port = field(info, "assigned_port") or field(info, "assignedPort")
    token = field(info, "proxy_token") or field(info, "proxyToken")
    real_query = field(info, "sql_query") or field(info, "sqlQuery")
    url = f"http://{settings.proxy.rathole_host}:{port}/query"
    print(json.dumps({"setup": "ok", "proxy_port": port, "query_length": len(real_query or ""),
                      "token_present": bool(token)}))

    report(send(url, token, "SIG", real_query, key_a, document_a, wrong_signature=True), 401, "SIGNATURE_INVALID")
    report(send(url, token, "I1", real_query, key_a, ""), 403, "ATTESTATION_REQUIRED")
    report(send(url, token, "I3", real_query, key_b, document_a), 403, "PCR_MISMATCH")

    first_use = send(url, token, "I4a-first-use", BLOCKED_QUERY, key_a, document_a)
    report(first_use, 400, "QUERY_BLOCKED")
    report(send(url, token, "I4a-replay", real_query, key_a, document_a), 403, "ATTESTATION_REPLAYED")

    if os.environ.get("PROBE_SKIP_STALE") == "1":
        print(json.dumps({"case": "I4b-stale", "skipped": True}))
        return
    key_c, document_c = new_session(enclave, "PROBE-C")
    print(json.dumps({"case": "I4b-stale", "waiting_seconds": STALE_WAIT_SECONDS}), flush=True)
    time.sleep(STALE_WAIT_SECONDS)
    report(send(url, token, "I4b-stale", real_query, key_c, document_c), 403, "ATTESTATION_STALE")


if __name__ == "__main__":
    main()
