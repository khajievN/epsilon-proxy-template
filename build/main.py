"""Scenario E4, part 2: what a job can see of the job before it.

Submitted as build/main.py, as the job directly after e4_leave_main.py. It lists the processes it can see and the
files in the shared temporary folders, and reports any that carry the marker of the earlier job. It reads no data.
"""
import os
import tempfile

MARKER = "epsilon_e4_marker"
me = os.getpid()
print(f"uid={os.getuid()} pid={me}")

processes, marked = [], []
for entry in sorted(os.listdir("/proc"), key=lambda name: (not name.isdigit(), name)):
    if not entry.isdigit():
        continue
    try:
        with open(f"/proc/{entry}/cmdline", "rb") as handle:
            command = handle.read().replace(b"\x00", b" ").decode(errors="replace").strip()
        owner = os.stat(f"/proc/{entry}").st_uid
    except OSError:
        continue
    processes.append((int(entry), owner, command[:80]))
    if MARKER in command and int(entry) != me:
        marked.append(int(entry))

print(f"processes visible: {len(processes)}")
for pid, owner, command in processes:
    print(f"  pid={pid} uid={owner} {command}")
print(f"processes left by the earlier job: {marked if marked else 'none'}")

leftovers = []
for folder in dict.fromkeys((tempfile.gettempdir(), "/tmp", "/var/tmp", "/dev/shm")):
    try:
        names = sorted(os.listdir(folder))
    except OSError as error:
        print(f"{folder}: cannot list ({error.strerror})")
        continue
    print(f"{folder}: {len(names)} entries")
    for name in names:
        print(f"  {name}")
        if MARKER in name:
            leftovers.append(os.path.join(folder, name))
print(f"files left by the earlier job: {leftovers if leftovers else 'none'}")
