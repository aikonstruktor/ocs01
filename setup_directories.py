import subprocess

def setup_directories():
    print("Setting up installation directories...")
    subprocess.run(["sudo", "mkdir", "-p", "/opt/ocs"], check=True)

