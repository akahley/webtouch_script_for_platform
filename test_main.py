import selenium
import time
import csv
import os, sys
import argparse
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

environments = {
    'staging': 'https://site.zodiac-staging.com/?lang=en',
    'production': 'https://site.iaqualink.net/?lang=en',
    'test': 'https://site.zodiac-test.com/?lang=en',
}

owners_center_landing = {
    'https://site.zodiac-staging.com/?lang=en': 'https://site.zodiac-staging.com/index.html#/owners-center',
    'https://site.iaqualink.net/?lang=en': 'https://site.iaqualink.net/index.html#/owners-center',
    'https://site.zodiac-test.com/?lang=en': 'https://site.zodiac-test.com/index.html#/owners-center',
}

def get_file_info():
    with open(f'{__location__}\\proprietary_info\\creds.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        first = next(csv_reader)
        second = next(csv_reader)
        username = first[0]
        password = first[1]
        serial = second[0]
        envrionment = second[1]
        num_iterations = int(second[2])
    return [username, password, serial, envrionment, num_iterations]

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

print(__location__)

info = get_file_info()


class Driver:

    def __init__(self, environment) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--user-data-dir={__location__}\\chromedriver")
        service = Service(f'{__location__}\\chromedriver\\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(environment)
        
    def openOwnersCenter(self, username, password, environment):
        try:
            time.sleep(15)
            print(self.driver.window_handles)
            if(len(self.driver.window_handles)):
                self.driver.switch_to.window(self.driver.window_handles[1])
            else:
                pass
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="userID"]'))).send_keys(username)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="userPassword"]'))).send_keys(password)
            time.sleep(1)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ng-app"]/div[2]/div[2]/div[1]/form/div/div[4]/button'))).click()
            return self.verifySuccessfulSignOn()
        except:
            return self.verifySuccessfulSignOn()

    def verifySuccessfulSignOn(self):
        try:
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div[4]/div[1]/div[1]/a/span/span')))
            return True
        except TimeoutException:
            return False


    def verifyWebtouchOpen(self): 
        try:
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainMap"]/div[1]')))
            if self.driver.find_element(By.XPATH, '//*[@id="2D"]').text:
                return True
            else:
                return False
        except:
            return False
        

    def verifyPumpOn(self):
        if WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_0"]/table/tbody/tr/td[2]'))).text == 'ON':
            return True
        else:
            return False

    def verifyPumpOff(self):
        if WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_0"]/table/tbody/tr/td[2]'))).text == 'OFF':
            return True
        else:
            return False

    def verifyAuxOn(self, i):
        if WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_'+str(i)+'"]/table/tbody/tr/td[1]'))).text == 'ON':
            return True
        else:
            return False

    def verifyAuxOff(self, i):
        if WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_'+str(i)+'"]/table/tbody/tr/td[1]'))).text == 'OFF':
            return True
        else:
            return False


    def checkDeviceStatus(self, i):
        try:
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[1]/div[2]/div'))).click()
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[2]/div[2]/div[1]/div[2]/div/p[1]/span[2]')))
            deviceStatus = self.driver.find_element(By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[2]/div[2]/div[1]/div[2]/div/p[1]/span[2]').text
            print(deviceStatus)
            offline_counter = 0
            while deviceStatus == 'Offline':
                WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[1]/div[2]/div'))).click()
                time.sleep(1)
                WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[1]/div[2]/div'))).click()
                time.sleep(1)
                try:
                    device_status = self.driver.find_element(By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[2]/div[2]/div[1]/div[2]/div/p[1]/span[2]').text
                    print(device_status) #prints device status
                except:
                    print('Cannot find Status')
                    return False
            
                offline_counter+=1

                if offline_counter > 20:
                    return False
                else:
                    return True
            
        except:
            print('Could not check status')

    def openDevice(self, deviceName):
        try:
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div[4]/div[1]/div[1]/a/span/span')))
            i = 4
            while WebDriverWait(self.driver,25).until(EC.presence_of_element_located((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) + ']/div[1]/div[1]/a/span/span'))).text != deviceName:
                i += 1

            self.checkDeviceStatus(i)
            time.sleep(1)
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) + ']/div[1]/div[1]/a/span/span'))).click()
            print(self.driver.window_handles)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            return True
        except:
            return False

    def turnOnOffFilterPumpFromHome(self):
        try:
            self.verifyWebtouchOpen()
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="1_24_7"]'))).click()
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_0"]/table/tbody/tr/td[2]'))).click()
            time.sleep(1)
            
            assert self.verifyPumpOn() == True
            
            time.sleep(10)

            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_0"]/table/tbody/tr/td[2]'))).click()
            time.sleep(1)

            assert self.verifyPumpOff() == True

            return True
        except (TimeoutException, AssertionError):
            return False

    def turnOnOffAuxFromOtherDevices(self, aux_num):
        try:
            index = self.onOffDevices(aux_num)
            time.sleep(1)
            assert True == self.verifyAuxOn(index)
            time.sleep(10)
            self.onOffDevices(aux_num)
            time.sleep(1)
            assert True == self.verifyAuxOff(index)
            time.sleep(3)
            return True
        except (TimeoutException, AssertionError):
            return False

    def onOffDevices(self, device):
        try:
            time.sleep(2)
            i = 0
            while WebDriverWait(self.driver,25).until(EC.presence_of_element_located((By.XPATH, '//*[@id="10_24_'+str(i)+'"]/table/tbody/tr/td[1]'))).text != device: #find desired device
                i +=1
            WebDriverWait(self.driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_'+str(i)+'"]/table/tbody/tr/td[1]'))).click() #click desired device
            return i
        except:
            return None
        
    def switch_window_handle(self, window_num):
        self.driver.switch_to.window(self.driver.window_handles[window_num])

    def close_window(self):
        self.driver.close()




@pytest.mark.parametrize('i', range(info[4]))
def test_main(i):
    
    
    username = info[0]
    password = info[1]
    serial = info[2]
    environ = info[3]

    try:
        driver = Driver(environments[environ])
        test_passed = True

        assert test_passed == driver.openOwnersCenter(username, password, environments[environ])
        time.sleep(1)
        assert test_passed == driver.openDevice(serial)
        time.sleep(10)
        assert test_passed == driver.turnOnOffFilterPumpFromHome()
        time.sleep(3)
        assert test_passed == driver.turnOnOffAuxFromOtherDevices('Aux6')
        driver.switch_window_handle(0)
        driver.close_window()
        assert test_passed == True
    except (WebDriverException, AssertionError):
        driver.switch_window_handle(0)
        driver.close_window()

'''
if __name__ == "__main__":
    main()
'''