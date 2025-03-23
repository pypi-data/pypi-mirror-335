# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-02-26 11:46
# @Author : 毛鹏
import os
import platform

import sys

system = platform.system().lower()
if system == "windows":
    runtime_path = os.path.join(os.path.dirname(__file__), "pyarmor_runtime_windows")
elif system == "linux":
    runtime_path = os.path.join(os.path.dirname(__file__), "pyarmor_runtime_linux")
elif system == "Darwin":  # macOS
    runtime_path = os.path.join(os.path.dirname(__file__), "pyarmor_runtime_linux")
else:
    raise RuntimeError(f"Unsupported platform: {system}")

if runtime_path not in sys.path:
    sys.path.append(runtime_path)

runtime_sub_path = os.path.join(runtime_path, "pyarmor_runtime_000000")
if runtime_sub_path not in sys.path:
    sys.path.append(runtime_sub_path)

try:
    import pyarmor_runtime_000000
except ImportError as e:
    raise RuntimeError(f"Failed to load PyArmor runtime for {system}: {e}")

try:
    from mango import Mango
except ImportError as e:
    raise RuntimeError(f"Failed to import obfuscated module: {e}")
