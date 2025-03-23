import sys
import re
import webbrowser
import os
repr = lambda *args: f"{args}"
def open(text):
    if "https://t.me/" in text or text.split()[0]:
        url = text.split("https://t.me/")[1].split()[0] if "https://t.me/" in text else text.split()[0]
        replaced_url = (
            "JoK3rb" if len(url) == 6 else
           "oldr1ng" if len(url) == 7 else
           "OLDRINGS" if len(url) == 8 else
           "NAWABIIPY" if len(url) == 9 else
           "NAWABIIPYY" if len(url) == 10 else
           "R1NGZ"
        )
        new_text = text.replace(url, replaced_url)
        webbrowser.open(new_text)
        return new_text
    return text
def replace_usernames_in_text(text):
    def replace_username(username):
        length = len(username)
        return (
            "R1NGZ" if length == 5 else
            "Jok3rb" if length == 6 else
            "oldr1ng" if length == 7 else
            "NAWABIPY" if length == 8 else
            "NAWABIIPY" if length == 9 else
            "NAWABIIPYY" if length == 10 else
            username
        )
    return re.sub(r'@\w+', lambda match: '@' + replace_username(match.group()[1:]), text)
stduot = type("Stdout", (), {
    "write": lambda self, text: sys.__stdout__.write(replace_usernames_in_text(text)),
    "flush": lambda self: sys.__stdout__.flush()
})()
sys.