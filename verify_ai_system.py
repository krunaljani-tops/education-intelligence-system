# Alias for verify_ai_systems.py
import os
import sys

script_path = os.path.join(os.path.dirname(__file__), "verify_ai_systems.py")
with open(script_path, "r", encoding="utf-8") as f:
    code = f.read()

exec(compile(code, script_path, "exec"))
