import os
import shutil
import subprocess
import urllib.request
import glob

OCS_VERSION = "9.0.10"  # example
OCS_PACKAGE_DIR = os.environ.get("OCS_PACKAGE_DIR")
DOWNLOAD_DIR = "./ocs_downloads"
INSTALL_DIR = "/opt/ocs"

# Mapping of version/arch to URLs
OCS_URLS = {
    "9.0.10": {
        "lx-amd64": "https://hpc-gridware.com/download/11543/?tmstv=1765743707",
        "lx-arm64": "https://hpc-gridware.com/download/11546/?tmstv=1765743707",
        "ulx-amd64": "https://hpc-gridware.com/download/11550/?tmstv=1765743707",
        "doc": "https://hpc-gridware.com/download/11558/?tmstv=1765743707",
        "common": "https://hpc-gridware.com/download/11556/?tmstv=1765743707",
    },
    # add other versions similarly...
}

def detect_architecture():
    arch = os.uname().machine
    if arch == "x86_64":
        return "lx-amd64"
    elif arch in ("aarch64", "arm64"):
        return "lx-arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {arch}")

def download_file(url, dest):
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, dest)

def download_files():
    arch = detect_architecture()
    print(f"Detected architecture: {arch}")
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    if OCS_PACKAGE_DIR:
        print(f"Using pre-downloaded packages from {OCS_PACKAGE_DIR}")
        for pkg in ["bin", "common", "doc"]:
            for prefix in ["ocs", "gcs"]:
                fname = f"{prefix}-{OCS_VERSION}-{pkg if pkg=='bin' else pkg}-{arch if pkg=='bin' else ''}.tar.gz".replace("--", "-")
                src = os.path.join(OCS_PACKAGE_DIR, fname)
                if os.path.isfile(src):
                    shutil.copy(src, DOWNLOAD_DIR)
                    break
            else:
                raise FileNotFoundError(f"Missing package: {pkg}")
    else:
        for key, url in OCS_URLS[OCS_VERSION].items():
            print(f"Downloading OCS {OCS_VERSION} {key} packages...")
            fname = os.path.join(DOWNLOAD_DIR, f"{key}.tar.gz")
            download_file(url, fname)

    print(f"Extracting files to {INSTALL_DIR}...")
    for tar_file in glob.glob(os.path.join(DOWNLOAD_DIR, "*.tar.gz")):
        print(f"  Extracting {tar_file}...")
        subprocess.run(["sudo", "tar", "xpf", tar_file, "-C", INSTALL_DIR], check=True)

