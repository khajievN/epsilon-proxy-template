"""Scenario FAIL: a script that fails on purpose.

Submitted as build/main.py. Expected: the run ends with a non-zero exit code, the enclave signs a record with
outcome "failed" and a digest of the error text, and nothing of the error is shown before review.
"""
print("About to fail on purpose")
raise RuntimeError("deliberate test failure")
