import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from QueenNoxi.modules.disable import DisableAbleCommandHandler

print(f"DisableAbleCommandHandler: {DisableAbleCommandHandler}")

def test_func(client, message):
    pass

try:
    decorator = DisableAbleCommandHandler(["notes", "saved"])
    print(f"Decorator created: {decorator}")
    wrapped = decorator(test_func)
    print(f"Wrapped function: {wrapped}")
except Exception as e:
    print(f"Error: {e}")
