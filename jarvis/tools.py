import subprocess

def open_calculator():
    subprocess.Popen("calc.exe")
    return "Открываю калькулятор"

def open_browser():
    subprocess.Popen("start https://google.com", shell=True)
    return "Открываю браузер"