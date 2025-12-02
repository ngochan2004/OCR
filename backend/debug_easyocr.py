import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import easyocr
    print("SUCCESS: easyocr imported")
except ImportError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"EXCEPTION: {e}")

try:
    import torch
    print(f"SUCCESS: torch imported (version {torch.__version__})")
except ImportError as e:
    print(f"ERROR importing torch: {e}")
