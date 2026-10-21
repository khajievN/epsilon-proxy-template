"""Scenario E3: ask the enclave to sign a record without a run.

Run inside the coordinator's executor container, which reaches the enclave over vsock:
    docker exec -i coordinator-executor-worker-1 python - < e3_probe.py

Each case sends one request and prints the enclave's answer. Expected: the enclave refuses to sign any content
the caller supplies; the only document it issues on request binds a key it generated itself.
"""
import base64
import json
import socket
import struct

from epsilon_verifier.verifier import _parse_and_validate_attestation

ENCLAVE_CID = 18
ENCLAVE_PORT = 5005

FORGED_RECORD = json.dumps({
    "job_id": "JOB-FORGED",
    "script_hash": "00" * 32,
    "dataset_hash": "00" * 32,
    "output_hash": "11" * 32,
    "files_manifest_sha256": "22" * 32,
})


def call(request):
    sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((ENCLAVE_CID, ENCLAVE_PORT))
    body = json.dumps(request).encode()
    sock.sendall(struct.pack("!I", len(body)) + body)
    length = struct.unpack("!I", recv_exact(sock, 4))[0]
    response = json.loads(recv_exact(sock, length))
    sock.close()
    return response


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("enclave closed the connection")
        buf += chunk
    return buf


def attested_user_data(response):
    doc = (response.get("attestation") or {}).get("attestation_document")
    if not doc:
        return None
    user_data = _parse_and_validate_attestation(doc).user_data
    try:
        return json.loads(user_data)
    except (ValueError, TypeError):
        return {"raw_bytes": len(user_data or b""), "base64": base64.b64encode(user_data or b"").decode()}


def report(case, request, response):
    shown = {k: v for k, v in request.items() if k != "user_data"}
    if "user_data" in request:
        shown["user_data"] = "<forged execution record>"
    print(f"--- {case}")
    print(f"request:  {json.dumps(shown)}")
    print(f"success:  {response.get('success')}")
    print(f"error:    {response.get('error') or response.get('message')}")
    user_data = attested_user_data(response)
    if user_data is not None:
        keys = sorted(user_data) if isinstance(user_data, dict) else user_data
        print(f"signed document issued; user_data keys: {keys}")
    else:
        print("signed document issued: no")


def main():
    report("1 forged record as user_data", {"operation": "get_attestation", "session_id": "x", "user_data": FORGED_RECORD},
           call({"operation": "get_attestation", "session_id": "x", "user_data": FORGED_RECORD}))
    report("2 no session", {"operation": "get_attestation"}, call({"operation": "get_attestation"}))
    report("3 unknown session", {"operation": "get_attestation", "session_id": "rsa-session-forged"},
           call({"operation": "get_attestation", "session_id": "rsa-session-forged"}))

    keypair = call({"operation": "generate_rsa_keypair", "job_id": "E3-PROBE"})
    session_id = keypair.get("session_id")
    report("4 own session (control)", {"operation": "get_attestation", "session_id": session_id},
           call({"operation": "get_attestation", "session_id": session_id}))


if __name__ == "__main__":
    main()
