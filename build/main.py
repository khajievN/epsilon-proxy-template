"""Scenario E4, part 1: a job that tries to leave a process and files behind for the next job.

Submitted as build/main.py. It starts a detached process that sleeps for an hour and writes marker files in the
shared temporary folders, then ends normally. Run e4_look_main.py as the next job to see what remained.
"""
import os
import subprocess
import tempfile
import time

MARKER = "epsilon_e4_marker"

sleeper = subprocess.Popen(
    ["python3", "-c", "import time; time.sleep(3600)  # " + MARKER],
    start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
print(f"uid={os.getuid()} started detached sleeper pid={sleeper.pid} session={os.getsid(sleeper.pid)}")

for folder in (tempfile.gettempdir(), "/var/tmp", "/dev/shm"):
    path = os.path.join(folder, f"{MARKER}_{int(time.time())}.txt")
    try:
        with open(path, "w") as handle:
            handle.write("left by the E4 job\n")
        print(f"wrote {path}")
    except OSError as error:
        print(f"could not write in {folder}: {error.strerror}")

print(f"sleeper still running at exit: {sleeper.poll() is None}")
