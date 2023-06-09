import selenium
import time
import csv
import os, sys
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc


parser = argparse.ArgumentParser(description='Toggle pump and aux in webtouch')
parser.add_argument('-d', '--device_serial', nargs='*', help='Input the last three digits of serial number')
parser.add_argument('-e', '--environment', nargs='*', help="Input the device environment eg. test, production, staging")
# Might want to just have people sign into their account that way they wouldn't have to provision the device to the generic account

args = parser.parse_args()

environments = {
    'staging': 'https://site.zodiac-staging.com/?lang=en',
    'production': 'https://site.iaqualink.net/index.html#/owners-center',
    'test': 'https://site.zodiac-test.com/?lang=en',
}

if(args.environment == None):
    environment = environments['production']
else:
    environment = environments[args.environment[0]]

print(f'Serial Number: {args.device_serial[0]}')

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

print(__location__)

with open(f'{__location__}\\proprietary_info\\creds.csv', 'r') as f:
    csv_reader = csv.reader(f, delimiter=',')
    for line in csv_reader:
        username = line[0]
        password = line[1]

print(username)
print(password)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"--user-data-dir={__location__}\\chromedriver")
service = Service(f'{__location__}\\chromedriver\\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

def openOwnersCenter(username, password, environment):
    try:
        driver.get(environment)
        time.sleep(15)
        print(driver.window_handles)
        if(len(driver.window_handles)):
            driver.switch_to.window(driver.window_handles[1])
        else:
            pass
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="userID"]'))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="userPassword"]'))).send_keys(password)
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ng-app"]/div[2]/div[2]/div[1]/form/div/div[4]/button'))).click()
    except:
        print("Already signed in")

def checkDeviceStatus(i):
    try:
        WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[1]/div[2]/div'))).click()
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[2]/div[2]/div[1]/div[2]/div/p[1]/span[2]')))
        deviceStatus = driver.find_element(By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[2]/div[2]/div[1]/div[2]/div/p[1]/span[2]').text
        print(deviceStatus)

        while deviceStatus == 'Offline':
            WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[1]/div[2]/div'))).click()
            time.sleep(1)
            WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[1]/div[2]/div'))).click()
            time.sleep(1)
            try:
                print(driver.find_element(By.XPATH, '//*[@id="homeTab"]/div['+ str(i) +']/div[2]/div[2]/div[1]/div[2]/div/p[1]/span[2]').text) #prints device status
            except:
                print('Cannot find Status')
    except:
        print('Could not check status')

def openDevice(deviceName):
    try:
        WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div[4]/div[1]/div[1]/a/span/span')))
        i = 4
        while WebDriverWait(driver,25).until(EC.presence_of_element_located((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) + ']/div[1]/div[1]/a/span/span'))).text != deviceName:
            i += 1

        checkDeviceStatus(i)
        time.sleep(1)
        WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTab"]/div['+ str(i) + ']/div[1]/div[1]/a/span/span'))).click()
        print(driver.window_handles)
        driver.switch_to.window(driver.window_handles[-1])
    except:
        print('Could not open device')

def turnOnOffFilterPumpFromHome():
    WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="1_24_0"]'))).click()
    time.sleep(5)
    WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="1_24_0"]'))).click()

def turnOnOffAuxFromOtherDevices(aux_num):
    WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="1_24_7"]'))).click()
    time.sleep(1)
    onOffDevices(aux_num)
    time.sleep(5)
    onOffDevices(aux_num)
    time.sleep(1)

def onOffDevices(device):
    time.sleep(2)
    i = 0
    while WebDriverWait(driver,25).until(EC.presence_of_element_located((By.XPATH, '//*[@id="10_24_'+str(i)+'"]/table/tbody/tr/td[1]'))).text != device: #find desired device
        i +=1
    WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="10_24_'+str(i)+'"]/table/tbody/tr/td[1]'))).click() #click desired device



def main():

    openOwnersCenter(username, password, environment)
    time.sleep(1)
    openDevice(args.device_serial[0])
    time.sleep(5)
    turnOnOffFilterPumpFromHome()
    time.sleep(1)
    turnOnOffAuxFromOtherDevices('Aux6')
    driver.quit()


if __name__ == "__main__":
    main()
