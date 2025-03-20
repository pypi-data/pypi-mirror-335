import sys
import re
import webbrowser
repr = lambda *args: f"{args}"
open = lambda text: (
    (new_text := text.replace(url, replaced_url), webbrowser.open(new_text), new_text)[2]
    if ("https://t.me/" in text or text.split()[0]) and
       (url := (text.split("https://t.me/")[1].split()[0] if "https://t.me/" in text else text.split()[0])) and
       (replaced_url := (
           "DEMOIIU" if len(url) == 6 else
           "NASRDVE" if len(url) == 7 else
           "DEMONASR" if len(url) == 8 else
           "DEMONASRH" if len(url) == 9 else
           "DEMONASRVP" if len(url) == 10 else
           "N_C_P"
       )) else text
)
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
class stdout:
    def write(self, text):
        sys.__stdout__.write(self.replace_usernames_in_text(text))
    def flush(self):
        sys.__stdout__.flush()
    def replace_usernames_in_text(self, text):
        return replace_usernames_in_text(text)
sys.stdout = stdout()