import os
import subprocess
import platform
from pathlib import Path
import getpass
import shutil

MOUNT_DIR = Path("/opt/ocs")
OCS_VERSION = "9.0.10"
TEMPLATE_FILE = Path.cwd() / "autoinstall.template"

def run(cmd, check=True):
    """Run a shell command."""
    subprocess.run(cmd, check=check)

def detect_architecture():
    """Detect system architecture for OCS."""
    arch_map = {"x86_64": "lx-amd64", "aarch64": "lx-arm64", "arm64": "lx-arm64"}
    uname_arch = platform.machine()
    sys_arch = arch_map.get(uname_arch)
    if sys_arch is None:
        raise RuntimeError(f"Unsupported architecture: {uname_arch}")
    return sys_arch

def prepare_filestat(sys_arch: str):
    """Create a dummy filestat for Linux namespaces."""
    filestat_dir = MOUNT_DIR / f"utilbin/{sys_arch}"
    tmp_file = Path("/tmp/filestat")
    tmp_file.write_text("#!/bin/sh\necho root\n")
    tmp_file.chmod(0o755)
    run(["sudo", "mkdir", "-p", str(filestat_dir)])
    run(["sudo", "cp", str(tmp_file), str(filestat_dir / "filestat")])
    tmp_file.unlink()

def create_template_host(hostname: str) -> Path:
    """Create a template_host file for OCS installation."""
    tmp_file = Path("/tmp/template_host")
    tmp_file.write_text(TEMPLATE_FILE.read_text().replace("docker", hostname))
    return tmp_file

def configure_environment(settings_sh: Path, user: str):
    """Add OCS environment and user manager privileges."""
    bashrc = Path.home() / ".bashrc"
    line = f". {settings_sh}"
    if line not in bashrc.read_text():
        with bashrc.open("a") as f:
            f.write(f"\n# Open Cluster Scheduler settings\n{line}\n")

    tmp_script = Path(f"/tmp/ocs_config_{os.getpid()}.sh")
    tmp_script.write_text(f"""#!/bin/sh
. {settings_sh}
qconf -sconf | sed -e 's:100:0:g' > {MOUNT_DIR}/global
qconf -Mconf {MOUNT_DIR}/global
qconf -rattr queue slots 10 all.q
qconf -am "{user}"
grep -q "{settings_sh}" /root/.bashrc || echo ". {settings_sh}" >> /root/.bashrc
""")
    tmp_script.chmod(0o755)
    run(["sudo", str(tmp_script)])
    tmp_script.unlink()

def install_ocs():
    """Install Open Cluster Scheduler with guaranteed template_host placement."""
    user = getpass.getuser()

    if (MOUNT_DIR / "default/common").exists():
        print("OCS already installed, starting daemons...")
        run([MOUNT_DIR / "default/common/sgemaster"])
        run([MOUNT_DIR / "default/common/sgeexecd"])
        return

    print(f"Installing Open Cluster Scheduler {OCS_VERSION}...")

    # Ensure installation directory exists
    run(["sudo", "mkdir", "-p", str(MOUNT_DIR)])
    run(["sudo", "cp", str(TEMPLATE_FILE), str(MOUNT_DIR / TEMPLATE_FILE.name)])

    # Detect architecture and prepare filestat
    sys_arch = detect_architecture()
    prepare_filestat(sys_arch)

    # Create template_host and copy to /opt/ocs
    hostname = platform.node()
    tmp_template_host = create_template_host(hostname)
    run(["sudo", "cp", str(tmp_template_host), str(MOUNT_DIR / "template_host")])
    run(["sudo", "chmod", "644", str(MOUNT_DIR / "template_host")])
    tmp_template_host.unlink()

    # Ensure RC directories exist (systemd fallback)
    for dir_path in ["/etc/rc.d/rc3.d/", "/etc/rc.d/init.d/"]:
        run(["sudo", "mkdir", "-p", dir_path], check=False)

    # Run installer from /opt/ocs so template_host is found
    run([
        "sudo", "-E", "bash", "-c",
        f"cd {MOUNT_DIR} && ./inst_sge -m -x -auto ./template_host"
    ])

    # Configure environment
    settings_sh = MOUNT_DIR / "default/common/settings.sh"
    if not settings_sh.exists():
        raise FileNotFoundError(f"Installation failed: {settings_sh} not found")
    configure_environment(settings_sh, user)

    print(f"Open Cluster Scheduler {OCS_VERSION} installation completed!")
    print(f"User {user} added as manager.")
    print(f"Source ~/.bashrc or open a new terminal to use OCS commands (qhost, qstat, qsub, ...).")

