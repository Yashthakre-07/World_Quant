import sys
try:
    import ace_lib
    print(f"ace_lib path: {ace_lib.__file__}")
except Exception as e:
    print(f"Failed to import ace_lib: {e}")

try:
    import helpful_functions
    print(f"helpful_functions path: {helpful_functions.__file__}")
except Exception as e:
    print(f"Failed to import helpful_functions: {e}")

print("Python sys.path:")
for p in sys.path:
    print(p)
