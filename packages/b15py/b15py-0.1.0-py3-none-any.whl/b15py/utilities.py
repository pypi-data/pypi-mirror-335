import sys
import subprocess
import platform

OK: int = 0xFF

def info(message: str):
    print(f"[\x1b[32m\x1b[1mINFO\x1b[0m] {message}")

def error(message: str):
    print(f"[\x1b[31m\x1b[1mERROR\x1b[0m] {message}")
    sys.exit(0)

def hint_error(message: str, hint: str):
    print(f"[\x1b[31m\x1b[1mERROR\x1b[0m] {message}")
    print(f"\x1b[3mhint\x1b[0m: {hint}")
    sys.exit(0)

def reverse(val: int):
    return int("{:08b}".format(val)[::-1], 2)

def get_devices():
    serial_port = "ls /dev/ttyUSB*"
    
    if platform.architecture()[0] == "64bit" and (platform.machine().startswith("arm") or platform.machine().startswith("aarch64")):
        serial_port = "ls /dev/ttyAMA*"
    
    try:
        result = subprocess.run(serial_port, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8').split()
    except subprocess.CalledProcessError as e:
        return []


