import os
import time
import subprocess
from uiautomator import Device

class UIAutomator:
    def __init__(self, ip_address="localhost:5555"):
        self.ip_address = ip_address
        os.system(f"adb connect {self.ip_address}")
        self.d = Device(self.ip_address)

    def execute(self, command):
        kind, name = command.split("@")[0], command.split("#")[0].split("@")[-1]
        name_se = command.split("#")[-1] if "#" in command else None

        def click_index():
            clickable_elements = self.d(clickable=True)
            clickable_elements[int(name)].click()

        action_map = {
            "cl_te": lambda: self.d(text=name).click(), "cl_cl": lambda: self.d(className=name).click(),
            "cl_id": lambda: self.d(resourceId=name).click(), "cl_de": lambda: self.d(description=name).click(),
            "se_te": lambda: self.d(text=name).set_text(name_se) if name_se else None,
            "sc_te": lambda: any(self.d(scrollable=True).scroll.forward() for _ in range(20)) if not self.d(text=name).exists else self.d(text=name).click(),
            "en": lambda: self.d.press('enter'), "ba": lambda: self.d.press.back(), "ti": lambda: time.sleep(int(name)),
            "cr": lambda: subprocess.run(f"adb -s {self.ip_address} shell pm clear {name}", shell=True),
            "op": lambda: subprocess.run(f"adb -s {self.ip_address} shell am start -n {name}", shell=True),
            "st": lambda: subprocess.run(f"adb -s {self.ip_address} shell am force-stop {name}", shell=True),
            "not": lambda: subprocess.run(f"adb -s {self.ip_address} shell cmd statusbar expand-notifications", shell=True),
            "col": lambda: subprocess.run(f"adb -s {self.ip_address} shell cmd statusbar collapse", shell=True),
            "bo": lambda: click_index(),
        }

        return action_map.get(kind, lambda: None)()


