import sys
import re
import webbrowser
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
stdout = type("Stdout", (), {
    "write": lambda self, text: sys.stdout.write(replace_usernames_in_text(text)),
    "flush": lambda self: sys.stdout.flush()
})()