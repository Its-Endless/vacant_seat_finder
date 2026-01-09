import time
import json
import gzip
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

def start_scraping(train_no, class_filter="ALL"):
    print(f"\n>>> 🚀 STARTING BOT for Train {train_no} ({class_filter})...")
    
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    full_train_data = []

    try:
        driver.get("https://www.irctc.co.in/online-charts/")
        driver.maximize_window()
        
        # --- AUTO-FILL ---
        try:
            time.sleep(2)
            # Train
            train_label = driver.find_element(By.XPATH, "//div[contains(text(), 'Train Name') or contains(text(), 'Train Number')]")
            train_input = train_label.find_element(By.XPATH, "./..//input")
            ActionChains(driver).move_to_element(train_input).click().send_keys(train_no).pause(2).send_keys(Keys.ENTER).perform()
            time.sleep(1)
            
            # Station
            station_label = driver.find_element(By.XPATH, "//div[contains(text(), 'Boarding Station')]")
            station_input = station_label.find_element(By.XPATH, "./..//input")
            ActionChains(driver).move_to_element(station_input).click().pause(1).send_keys(Keys.ENTER).perform()
            time.sleep(1)

            # Button
            get_chart_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Get Train Chart')]")
            try: get_chart_btn.click()
            except: get_chart_btn.find_element(By.XPATH, "./..").click()
            
            print(">>> ✅ Details Filled.")
        except Exception as e:
            print(f">>> ⚠️ Auto-fill failed: {e}")

        while "traincomposition" not in driver.current_url: time.sleep(1)
        time.sleep(4) 

        # --- SCANNING ---
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        coaches_to_scan = []
        
        for btn in all_buttons:
            txt = btn.text.strip()
            if 1 < len(txt) <= 3 and any(char.isdigit() for char in txt):
                should_click = False
                if class_filter == "ALL": should_click = True
                elif class_filter == "3A" and (txt.startswith('B') or txt.startswith('M')): should_click = True
                elif class_filter == "2A" and txt.startswith('A'): should_click = True
                elif class_filter == "1A" and txt.startswith('H'): should_click = True
                elif class_filter == "SL" and txt.startswith('S'): should_click = True
                if should_click: coaches_to_scan.append((txt, btn))

        print(f">>> 🔎 Found {len(coaches_to_scan)} coaches.")

        for coach_name, button in coaches_to_scan:
            print(f"--> {coach_name}:", end=" ")
            try:
                del driver.requests
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", button)
                
                try:
                    request = driver.wait_for_request('coachComposition', timeout=8)
                    if request.response:
                        body = request.response.body
                        try:
                            try: data = json.loads(body.decode('utf-8'))
                            except: data = json.loads(gzip.decompress(body).decode('utf-8'))
                            data['scraped_coach_name'] = coach_name
                            full_train_data.append(data)
                            print("✅")
                        except: print("⚠️ JSON Error")
                except TimeoutException: print("❌ Timeout")
            except: print("❌ Error")
            time.sleep(0.5)

        return full_train_data
    finally:
        driver.quit()