"""Scenario E4: submitted code tries to use the enclave's signing interface (/dev/nsm).

Submitted as build/main.py. Expected: the script runs as an unprivileged user, cannot open /dev/nsm or start the
NSM library, and the job's signed record holds only what the runner built.
"""
import ctypes
import os
import stat

print(f"uid={os.getuid()} gid={os.getgid()}")

try:
    st = os.stat("/dev/nsm")
    print(f"/dev/nsm mode={stat.filemode(st.st_mode)} owner={st.st_uid}:{st.st_gid}")
except OSError as e:
    print(f"stat /dev/nsm failed: {e}")

try:
    fd = os.open("/dev/nsm", os.O_RDWR)
    print("open /dev/nsm: OPENED")
    os.close(fd)
except OSError as e:
    print(f"open /dev/nsm: denied ({e.strerror})")

try:
    lib = ctypes.CDLL("/usr/lib64/libnsm.so")
    print(f"nsm_lib_init: returned {lib.nsm_lib_init()} (negative = no device handle)")
except OSError as e:
    print(f"load libnsm: failed ({e})")
