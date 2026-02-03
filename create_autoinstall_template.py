import os
from pathlib import Path

def create_autoinstall_template():
    hostname = os.uname().nodename
    template_file = Path.cwd() / "autoinstall.template"

    # Environment overrides
    exec_hosts = os.environ.get("OCS_EXEC_HOSTS", hostname)
    admin_hosts = os.environ.get("OCS_ADMIN_HOSTS", exec_hosts)
    submit_hosts = os.environ.get("OCS_SUBMIT_HOSTS", exec_hosts)

    print("Creating installation template with:")
    print(f"  Admin hosts: {admin_hosts}")
    print(f"  Submit hosts: {submit_hosts}")
    print(f"  Execution hosts: {exec_hosts}")

    # Config dictionary (elegant & maintainable)
    config = {
        "SGE_ROOT": "/opt/ocs",
        "SGE_QMASTER_PORT": "6444",
        "SGE_EXECD_PORT": "6445",
        "SGE_ENABLE_SMF": "false",
        "SGE_CLUSTER_NAME": "p6444",
        "CELL_NAME": "default",
        "ADMIN_USER": "root",
        "QMASTER_SPOOL_DIR": "/opt/ocs/default/spool/master",
        "EXECD_SPOOL_DIR": "/opt/ocs/default/spool/execd",
        "GID_RANGE": "20000-20200",
        "SPOOLING_METHOD": "classic",
        "DB_SPOOLING_DIR": "/opt/ocs/default/spool/bdb",
        "PAR_EXECD_INST_COUNT": "20",
        "ADMIN_HOST_LIST": admin_hosts,
        "SUBMIT_HOST_LIST": submit_hosts,
        "EXEC_HOST_LIST": exec_hosts,
        "EXECD_SPOOL_DIR_LOCAL": "",
        "HOSTNAME_RESOLVING": "true",
        "SHELL_NAME": "ssh",
        "COPY_COMMAND": "scp",
        "DEFAULT_DOMAIN": "none",
        "ADMIN_MAIL": "none",
        "ADD_TO_RC": "true",
        "SET_FILE_PERMS": "true",
        "RESCHEDULE_JOBS": "wait",
        "SCHEDD_CONF": "3",
        "SHADOW_HOST": "",
        "EXEC_HOST_LIST_RM": "",
        "REMOVE_RC": "false",
        "CSP_RECREATE": "true",
        "CSP_COPY_CERTS": "false",
        "CSP_COUNTRY_CODE": "DE",
        "CSP_STATE": "Germany",
        "CSP_LOCATION": "Building",
        "CSP_ORGA": "Organisation",
        "CSP_ORGA_UNIT": "Organisation_unit",
        "CSP_MAIL_ADDRESS": "name@yourdomain.com",
    }

    # Write template elegantly
    with template_file.open("w") as f:
        for k, v in config.items():
            f.write(f'{k}="{v}"\n')

