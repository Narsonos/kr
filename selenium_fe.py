from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import xlsxwriter

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
driver.maximize_window()

def test_login():
	driver.get('http://192.168.88.248:5000/login')
	#! Use Navigation Timing  API to calculate the timings that matter the most
	navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
	responseStart = driver.execute_script("return window.performance.timing.responseStart")
	domComplete = driver.execute_script("return window.performance.timing.domComplete")
	
	#! Calculate the performance
	backendPerformance_calc = responseStart - navigationStart
	frontendPerformance_calc = domComplete - responseStart
	
	print("Back End: %s" % backendPerformance_calc)
	print("Front End: %s" % frontendPerformance_calc)
	return frontendPerformance_calc

def test_full_login_time():
	driver.get('http://192.168.88.248:5000/login')

	login_field = driver.find_element(By.ID,"vlogin")
	login_field.send_keys("user1")

	password_field = driver.find_element(By.ID,"vpassword")
	password_field.send_keys("password1")

	login_button = driver.find_element(By.ID,"vbtn")
	login_button.click()

	start_time = time.time()
	try:
		WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, 'myChart')))
		end_time = time.time()
		load_time = end_time-start_time
		print(f'Front-end load time: {load_time}')
		return load_time
	except TimeoutException:
		print('Chart did not appear within 10 seconds!')
		return "10+ seconds"

workbook = xlsxwriter.Workbook('100-50.xlsx')
worksheet = workbook.add_worksheet()
worksheet.set_column('A:A', 5)
bold = workbook.add_format({'bold': True})
worksheet.write('A1','Experiment #', bold)
worksheet.write('B1','/login front-end load', bold)
worksheet.write('C1','auth timing', bold)


for i in range(1,102):
	worksheet.write(i,0,i)
	worksheet.write(i,1,test_login())
	worksheet.write(i,2,test_full_login_time())

workbook.close()