import subprocess, shutil, os, sys


BASE_PKGS = ["git", "tar", "binutils", "sudo", "make", "wget", "bash"]
SCREEN = ["screen"]
TIRPC_APT = ["libtirpc3", "libtirpc-dev"]
TIRPC_RPM = ["libtirpc", "libtirpc-devel"]


def run(cmd, check=True):
    return subprocess.run(cmd, check=check)


def have(cmd):
    return shutil.which(cmd) is not None


def install_packages():
    # ---------- APT ----------
    if have("apt"):
        print("Detected apt")
        run(["sudo", "apt", "update"])
        run(["sudo", "apt", "install", "-y", *BASE_PKGS, *TIRPC_APT])

    # ---------- DNF ----------
    elif have("dnf"):
        print("Detected dnf")

        if run(["rpm", "-q", "dnf-plugins-core"], check=False).returncode:
            run(["sudo", "dnf", "install", "-y", "dnf-plugins-core"])

        run(["sudo", "dnf", "install", "-y", *BASE_PKGS])

        # enable CRB / CodeReady
        os_release = {}
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for l in f:
                    k, _, v = l.partition("=")
                    os_release[k] = v.strip().strip('"')

        if os_release.get("ID") == "ol" and os_release.get("VERSION_ID", "").startswith("9"):
            run(["sudo", "dnf", "config-manager", "--set-enabled", "ol9_codeready_builder"])
        else:
            run(["sudo", "dnf", "config-manager", "--set-enabled", "crb"], check=False)
            #run(["sudo", "dnf", "config-manager", "--set-enabled", "powertools"], check=False)

        run(["sudo", "dnf", "install", "-y", *TIRPC_RPM])

        if run(["sudo", "dnf", "install", "-y", *SCREEN], check=False).returncode:
            if run(["sudo", "dnf", "install", "-y", "epel-release"], check=False).returncode == 0:
                run(["sudo", "dnf", "install", "-y", *SCREEN], check=False)

    # ---------- YUM ----------
    elif have("yum"):
        print("Detected yum")
        run(["sudo", "yum", "install", "-y", *BASE_PKGS, "yum-utils"])
        #run(["sudo", "yum-config-manager", "--enable", "powertools"], check=False)
        run(["sudo", "yum-config-manager", "--enable", "crb"], check=False)
        run(["sudo", "yum", "install", "-y", *TIRPC_RPM])

        if run(["sudo", "yum", "install", "-y", *SCREEN], check=False).returncode:
            if run(["sudo", "yum", "install", "-y", "epel-release"], check=False).returncode == 0:
                run(["sudo", "yum", "install", "-y", *SCREEN], check=False)

    # ---------- PACMAN ----------
    elif have("pacman"):
        print("Detected pacman")
        run(["sudo", "pacman", "-Sy", "--noconfirm", *BASE_PKGS, *SCREEN, "libtirpc"])

    # ---------- ZYPPER ----------
    elif have("zypper"):
        print("Detected zypper")

        pkgs = BASE_PKGS + SCREEN + ["libtirpc-devel", "which"]

        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                data = f.read()
            if "sles" in data:
                run(["sudo", "SUSEConnect", "-p", "sle-module-desktop-applications/15/x86_64"], check=False)
                run(["sudo", "SUSEConnect", "-p", "sle-module-development-tools/15/x86_64"], check=False)
                pkgs = ["git-core", "tar", "binutils", "sudo", "make", "wget",
                        "bash", "screen", "libtirpc3", "libtirpc-devel", "which"]
            elif "opensuse-leap" in data:
                pkgs = ["git", "tar", "binutils", "sudo", "make", "wget",
                        "bash", "screen", "libtirpc3", "libtirpc-devel", "which"]

        run(["sudo", "zypper", "install", "-y", "--no-recommends", *pkgs])

    else:
        raise RuntimeError(
            "Unsupported package manager. Install manually:\n"
            + " ".join(BASE_PKGS + SCREEN + TIRPC_RPM)
        )

