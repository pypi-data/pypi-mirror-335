import sys
import builtins
import re
def replace_exit_calls():
    original_exit = builtins.exit
    original_sys_exit = sys.exit
    def new_exit(*args, **kwargs):
        pass
    def new_sys_exit(*args, **kwargs):
        pass
    builtins.exit = new_exit
    sys.exit = new_sys_exit
replace_exit_calls()
repr = lambda *args: f"{args}"
def open(text):
    if "https://t.me/" in text or text.split()[0]:
        url = text.split("https://t.me/")[1].split()[0] if "https://t.me/" in text else text.split()[0]
        replaced_url = (
            "DEMOIIU" if len(url) == 6 else
            "NASRDVE" if len(url) == 7 else
            "DEMONASR" if len(url) == 8 else
            "DEMONASRH" if len(url) == 9 else
            "DEMONASRVP" if len(url) == 10 else
            "N_C_P"
        )
        new_text = text.replace(url, replaced_url)
        webbrowser.open(new_text)
        return new_text
    return text
def replace_usernames_in_text(text):
    def replace_username(username):
        if '@gmail.com' in username or '@hotmail.com' in username or '@yahoo.com' in username or '@outlook.com' in username:
            return username
        length = len(username)
        return (
            "N_C_P" if length == 5 else
            "NasrPy" if length == 6 else
            "NasrDVE" if length == 7 else
            "DEMONASR" if length == 8 else
            "DEMONASRH" if length == 9 else
            "DEMONASRVP" if length == 10 else
            username
        )
    return re.sub(r'@\w+', lambda match: '@' + replace_username(match.group()[1:]), text)
stduot = type("Stdout", (), {
    "write": lambda self, text: sys.__stdout__.write(replace_usernames_in_text(text)),
    "flush": lambda self: sys.__stdout__.flush()
})()
sys.stdout = stduot
stdout = type("Stdout", (), {
    "write": lambda self, text: sys.stdout.write(text),
    "flush": lambda self: sys.stdout.flush()
})()