from colorama import Fore, Style
from kyakx.core.ssh_tools import ssh_download, ssh_upload

def ssh_menu():
    print(Fore.YELLOW + "\n1. Download File from SSH")
    print(Fore.YELLOW + "2. Upload File to SSH")
    print(Fore.YELLOW + "3. Go Back\n")

    choice = input(Fore.CYAN + "Select an option: " + Style.RESET_ALL)

    if choice == "1":
        ssh_download()
    elif choice == "2":
        ssh_upload()
    elif choice == "3":
        from kyakx.core.main_menu import main_menu
        main_menu()
    else:
        print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
        ssh_menu()
