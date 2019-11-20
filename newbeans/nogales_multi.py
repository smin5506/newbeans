from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re

from bs4 import BeautifulSoup
import pandas as pd
import time
from multiprocessing import Pool

from datetime import date, timedelta

def getData(url):
	
	options = Options()
	options.set_headless(headless=True)
	driver = webdriver.Firefox('/home/msh9584/newbeans', firefox_options=options)
	driver.implicitly_wait(1)
	driver.get(url)
	html = driver.page_source
	soup = BeautifulSoup(html, 'html.parser')
	driver.close()
	return soup

#노갈레스	
def nogales():
	url = 'https://www.cafenogales.co.kr/shop'
	beanUrl = 'https://www.cafenogales.co.kr/product/'

	#저장할 변수
	df = pd.DataFrame()
	tmp = {}

	soup = getData(url)

	beanUrlList = soup.find_all('div', class_="shopProduct productName")

	for beanCode in beanUrlList:
		code, name, processing = beanCode.text.split(' / ')
		
		beanSoup = getData(beanUrl+code.replace('-',''))
		beanRawData = beanSoup.find_all('span', class_='text')[0]
		
		for br in beanRawData.find_all("br"):
			br.replace_with("\n")
		
		beanDataList = beanRawData.text.split('\n')
		try:
			tmp['price'] = beanSoup.find_all('span', class_='productPriceSpan')[0].text
			for beanData in beanDataList:
				beanData = beanData.replace('\xa0', ' ')
				try:
					key, val = beanData.split(' : ')
					if key != 'Code':
						tmp[key] = val
					if key == 'Farmer':
						tmp['Farm'] = val
				except:
					pass
			df= df.append(tmp, ignore_index=True)
			tmp = {}
		except:
			pass
			
	return df
	
def get_links():
	url = 'https://www.cafenogales.co.kr/shop'
	soup = getData(url)
	beanUrlList = soup.find_all('div', class_="shopProduct productName")
	
	return beanUrlList
	
def get_content(beanCode):
	tmp = {}
	beanUrl = 'https://www.cafenogales.co.kr/product/'
	code, name, processing = beanCode.text.split(' / ')
		
	beanSoup = getData(beanUrl+code.replace('-',''))
	beanRawData = beanSoup.find_all('span', class_='text')[0]
	
	for br in beanRawData.find_all("br"):
		br.replace_with("\n")
	
	beanDataList = beanRawData.text.split('\n')
	try:
		tmp['price'] = beanSoup.find_all('span', class_='productPriceSpan')[0].text
		for beanData in beanDataList:
			beanData = beanData.replace('\xa0', ' ')
			try:
				key, val = beanData.split(' : ')
				if key != 'Code':
					tmp[key] = val
				if key == 'Farmer':
					tmp['Farm'] = val
			except:
				pass
	except:
		pass
	return tmp
	

if __name__=='__main__':

	df = pd.DataFrame()
	pool = Pool(processes=4) # 4개의 프로세스를 사용합니다.
	result = pool.map(get_content, get_links()) 
	df = df.append(result, ignore_index=True)
	now = date.today().strftime('%y%m%d')
	writer = pd.ExcelWriter('/home/msh9584/newbeans/xlsx/nogales'+now+'.xlsx', engine='xlsxwriter')
	df.to_excel(writer, sheet_name='Sheet1')
	writer.close()			

