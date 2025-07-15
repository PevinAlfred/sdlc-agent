# This script simulates a system status check
# It randomly returns "OK" or "FAIL" to mimic a monitoring system.
import random

def check_system_status() -> str:
    return random.choice(["OK", "FAIL"])

if __name__ == "__main__":
    print(check_system_status())
