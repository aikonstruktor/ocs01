from check_hostname_resolution import check_hostname_resolution
from install_packages import  install_packages
from setup_directories import  setup_directories
from download_files import  download_files
from create_autoinstall_template import  create_autoinstall_template
from install_ocs import  install_ocs

def main():
    check_hostname_resolution()
    install_packages()
    setup_directories()
    download_files()
    create_autoinstall_template()
    install_ocs()

if __name__ == "__main__":
    main()
