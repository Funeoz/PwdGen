import json
import os
import sys
from time import sleep
import getpass
import hashlib
import secrets
import string
import requests
from rich.table import Table
from rich.console import Console
from rich.progress import track

banner = """[red]
    ____                  __   ______              
   / __ \ _      __  ____/ /  / ____/ ___    ____ 
  / /_/ /| | /| / / / __  /  / / __  / _ \  / __ \\
 / ____/ | |/ |/ / / /_/ /  / /_/ / /  __/ / / / /
/_/      |__/|__/  \__,_/   \____/  \___/ /_/ /_/ 

        Author: Funeoz
        Github: https://github.com/Funeoz/PwdGen
        License: GPLv3[/red]
"""

symbols_list = ["!", "@", "#", "$", "%", "^", "&", "*"]
lower_letters = string.ascii_lowercase
upper_letters = string.ascii_lowercase
api_url = "https://api.pwnedpasswords.com/range/"

console = Console()
secretsGen = secrets.SystemRandom()


def back_to_menu():
    input("Press enter to continue...")
    return menu()


def generate_password(length=16):
    """Generate the password based on configuration paramaters"""
    chars_type = [key for key, value in config["include"].items() if value is True]
    final_pwd = ""
    for _ in track(range(length), description="[red]Generating password..."):
        current_char = secretsGen.choice(chars_type)
        if current_char == "symbols":
            final_pwd += secretsGen.choice(symbols_list)
        elif current_char == "lowercase":
            final_pwd += secretsGen.choice(lower_letters)
        elif current_char == "uppercase":
            final_pwd += secretsGen.choice(upper_letters)
        elif current_char == "numbers":
            final_pwd += str(secretsGen.randint(0, 9))
        sleep(0.01)
    if config["send_to_HIBP"] is False:
        console.print(f"Generated password : [bold]{final_pwd}[/bold]")
        return back_to_menu()
    return check_pwned_password(final_pwd, regenerate=True)


def check_pwned_password(password, regenerate=False):
    """Check if the password has already been pwned""""
    # calculate the hash
    password_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    # Call Have I Been Pwned API
    request = requests.get(api_url + password_hash[:5])
    # Check if password hash is in Have I Been Pwned DB
    is_cracked = password_hash[5:] in [
        x.split(":")[0] for x in request.text.split("\n")
    ]
    if is_cracked:
        console.print("⛔ Pwned password !", style="bold red blink")
        if regenerate is True:
            time.sleep(1)
            return generate_password(length=config["length"])
    else:
        console.print(
            f"✅ Your password has not been pwned and is safe to use: [bold]{password}[/bold]"
        )
    return back_to_menu()


def config_table():
    """Print the configuration table"""
    with open("config.json", "r") as file:
        config = json.loads(file.read())
    table = Table(title="Current configuration")
    table.add_column("Option", style="bold green")
    table.add_column("Value", style="red")
    table.add_row("Password length", str(config["length"]))
    table.add_row(
        "Include lowercase letters",
        "✅" if config["include"]["lowercase"] is True else "❌",
    )
    table.add_row(
        "Include uppercase letters",
        "✅" if config["include"]["uppercase"] is True else "❌",
    )
    table.add_row(
        "Include numbers", "✅" if config["include"]["numbers"] is True else "❌"
    )
    table.add_row(
        "Include symbols", "✅" if config["include"]["symbols"] is True else "❌"
    )
    table.add_row(
        "Check if the generated password has been pwned",
        "✅" if config["send_to_HIBP"] is True else "❌",
    )
    console.print(table)


def modify_include_chars(char_type):
    """Modify the configuration file"""
    option = ""
    while option != "yes" or option != "no":
        option = input("Enter [yes] or [no] to include lowercase letters : ")
        if option in ["yes", "no"]:
            break
    if option == "yes":
        config["include"][char_type] = True
    elif option == "no":
        config["include"][char_type] = False
    with open("config.json", "w") as file:
        json.dump(config, file)
    modify_config_file()


def config_menu():
    """Display the configuration menu"""
    entry = input(
        """
[0] Modify password length
[1] Include lowercase letters
[2] Include uppercase letters
[3] Include numbers
[4] Include symbols
[5] Check if the generated password has been pwned
[back] Go back to the main menu

Enter the option's number to modify : """
    ).strip()

    if entry == "0":
        try:
            pwd_length = int(
                input("Enter the number of characters for the password : ").strip()
            )
            config["length"] = pwd_length
            with open("config.json", "w") as file:
                json.dump(config, file)
            modify_config_file()
        except ValueError:
            os.system(clean_command)
            submenu()
    elif entry == "1":
        modify_include_chars(char_type="lowercase")
    elif entry == "2":
        modify_include_chars(char_type="uppercase")
    elif entry == "3":
        modify_include_chars(char_type="numbers")
    elif entry == "4":
        modify_include_chars(char_type="symbols")
    elif entry == "5":
        option = ""
        while option != "yes" or option != "no":
            option = input("Enter [yes] or [no] to check for password leak : ")
            if option in ["yes", "no"]:
                break
        if option == "yes":
            config["send_to_HIBP"] = True
        elif option == "no":
            config["send_to_HIBP"] = False
        with open("config.json", "w") as file:
            json.dump(config, file)
        modify_config_file()
    elif entry == "back":
        return menu()
    else:
        return modify_config_file()


def modify_config_file():
    os.system(clean_command)
    console.print(banner)
    config_table()
    config_menu()


def menu():
    with open("config.json", "r") as file:
        config = json.load(file)
    os.system(clean_command)
    console.print(banner)
    print(
        """
[0] Generate a password
[1] Check if a password has been pwned
[2] Modify configuration
[exit] Exit the program\n"""
    )
    choice = input("Enter your choice : ").strip()
    if choice == "0":
        generate_password(length=config["length"])
    elif choice == "1":
        pwned_password = getpass.getpass(prompt="Enter the password (hidden input) : ")
        check_pwned_password(pwned_password, regenerate=False)
    elif choice == "2":
        modify_config_file()
    elif choice == "exit":
        sys.exit()
    else:
        menu()


if __name__ == "__main__":
    with open("config.json", "r") as file:
        config = json.load(file)
    if os.name == "nt":
        clean_command = "cls"
    elif os.name == "posix":
        clean_command = "clear"
    menu()
