#!/usr/bin/env python
import subprocess
import sys

# Run backend checks
print("=" * 60)
print("TASK 3: BACKEND VALIDATION")
print("=" * 60)

print("\n1. Django System Check:")
print("-" * 40)
result = subprocess.run([
    sys.executable, "manage.py", "check"
], cwd=r"e:\vidyavana-website\vidyavana-backend", capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)

print("\n2. Chatbot Tests:")
print("-" * 40)
result = subprocess.run([
    sys.executable, "manage.py", "test", "apps.chatbot", "--verbosity=2"
], cwd=r"e:\vidyavana-website\vidyavana-backend", capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
if result.returncode == 0:
    print("✅ ALL TESTS PASSED")
else:
    print("❌ TESTS FAILED")
