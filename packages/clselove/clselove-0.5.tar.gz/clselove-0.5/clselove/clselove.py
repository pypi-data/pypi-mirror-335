from uiautomator import Device
import subprocess
import pycountry, phonenumbers
from phonenumbers import geocoder

#twine upload dist/*
#__init__.py
#rm -rf dist build *.egg-info
#python3 setup.py sdist bdist_wheel
def auto(pan,d):
    kind, name = pan.split("@")[0], pan.split("#")[0].split("@")[-1]
    name_se = pan.split("#")[-1] if "#" in pan else None
    def b():
        clickable_elements = d(clickable=True)
        clickable_elements[int(name)].click()
    action_map = {
        "cl_te": lambda: d(text=name).click(),"cl_cl": lambda: d(className=name).click(),"cl_id": lambda: d(resourceId=name).click(),"cl_de": lambda: d(description=name).click(),
        "cl_tee": lambda: d(text=name),"cl_cll": lambda: d(className=name),"cl_idd": lambda: d(resourceId=name),"cl_dee": lambda: d(description=name),
        "se_te": lambda: d(text=name).set_text(name_se) if name_se else None,"se_cl": lambda: d(className=name).set_text(name_se) if name_se else None,"se_id": lambda: d(resourceId=name).set_text(name_se) if name_se else None,"se_de": lambda: d(description=name).set_text(name_se) if name_se else None,
        "cr_te": lambda: d(text=name).clear_text(),"cr_cl": lambda: d(className=name).clear_text(),"cr_id": lambda: d(resourceId=name).clear_text(),"cr_de": lambda: d(description=name).clear_text(),
        "sc_te": lambda: any(d(scrollable=True).scroll.forward() for _ in range(20)) if not d(text=name).exists else d(text=name).click(),"sc_cl": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(className=name).exists else d(className=name).click(),"sc_id": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(resourceId=name).exists else d(resourceId=name).click(),"sc_de": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(description=name).exists else d(description=name).click(),
        "en": lambda: d.press('enter'),"ba": lambda: d.press.back(),"ti": lambda: time.sleep(int(name)),
        "cr": lambda: subprocess.run(f"adb -s {ip_address} shell pm clear {name}", shell=True, capture_output=True, text=True),
        "op": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n {name}", shell=True, capture_output=True, text=True),
        "st": lambda: subprocess.run(f"adb -s {ip_address} shell am force-stop {name}", shell=True, capture_output=True, text=True),
        "sw": lambda: subprocess.run(f"adb -s {ip_address} shell input swipe {name}",shell=True, capture_output=True, text=True),
       "not": lambda: subprocess.run(f"adb -s {ip_address} shell cmd statusbar expand-notifications", shell=True, capture_output=True, text=True),
       "col": lambda:subprocess.run(f"adb -s {ip_address} shell cmd statusbar collapse", shell=True, capture_output=True, text=True),
       "bo": lambda: b(),
            }
    action_map.get(kind, lambda: None)()

def get_phone(name):
    global phone
    global country_code
    global stop_phone
    global fn
    global co
    stop_phone = False
    response_get = requests.get(f'{name}.json')

    user_data = response_get.json()

    if user_data is None:

        print('no phone',name)
        stop_phone = True
    else:

        first_key = random.choice(list(user_data.keys()))

        phone= user_data[first_key].strip()
        requests.delete(f'{name}/{phone}.json')
        parsed_number = phonenumbers.parse(f'+{phone}')
        country = pycountry.countries.get(alpha_2=phonenumbers.region_code_for_country_code(parsed_number.country_code))
        country_code, fn, co = parsed_number.country_code, country.name[0], country.name.split(",")[0] if country else (None, None)
        print(phone)

