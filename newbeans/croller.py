#html 파싱 라이브러리
from bs4 import BeautifulSoup
import re

#웹페이지 크롤링 라이브러리
import urllib.request
import urllib.parse

#데이터 변수 라이브러리
import pandas as pd
from datetime import date, timedelta

import telepot

#해당 주소에서 raw데이터 긁어오기 함수
def getData(url):
	with urllib.request.urlopen(url) as response:
		html = response.read()
		soup = BeautifulSoup(html, 'html.parser')
	return soup
	
	
#저장된 내용을 엑셀로 바꿔서 저장  
def saveDF(df, siteName): 
	now = date.today().strftime('%y%m%d')
	writer = pd.ExcelWriter('/home/msh9584/newbeans/xlsx/'+siteName+now+'.xlsx', engine='xlsxwriter')
	df.to_excel(writer, sheet_name='Sheet1')
	writer.close()

	
#2개의 dataframe을 key로 비교
def getNewData(df1, df2, key):
	dfnew = df2[~(df2[key].isin(df1[key]))].reset_index(drop=True)
	return dfnew

	
#텔레그램 메시지 전송
def sendTele(siteName):
	token = '751499265:AAG-dVcyUemGSUWcOkdxagFuBgfQB3PsYbw'
	botid = '1069356539'
	botid2 = '819650085'
	bot = telepot.Bot(token)
		
	today = date.today().strftime('%y%m%d')
	yesterday = (date.today()-timedelta(1)).strftime('%y%m%d')
	yesterdayData = pd.read_excel('xlsx/'+siteName+yesterday+'.xlsx')
	todayData = pd.read_excel('xlsx/'+siteName+today+'.xlsx')

	todayNewData = getNewData(yesterdayData, todayData)

	if todayNewData.empty:
		bot.sendMessage(botid, siteName+'에 새로운 원두가 없습니다.')
		bot.sendMessage(botid2, siteName+'에 새로운 원두가 없습니다.')
	else:
		bot.sendMessage(botid, siteName+'에 새로운 원두가'+ len(todayNewData)+'건 입고되었습니다.')
		bot.sendMessage(botid2, siteName+'에 새로운 원두가'+ len(todayNewData) +'건 입고되었습니다.')
		

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
	

#나무사이로
def namu():
	#나무사이로 주소
	url = 'https://www.namusairo.com/product/list.html?cate_no=24'

	#저장할 변수
	df = pd.DataFrame()
	beanListUrl = []
	beanList = []
	soup = getData(url)
	
	#마지막 페이지 확인
	lastPage = [td for td in soup.find_all('a') if td.find_all('img', {'alt': '마지막 페이지'})][0]['href']

	for x in range(1, int(lastPage[-1])+1):
		tmp = []
		pageurl = url+lastPage[:-1] + str(x)
		pageSoup = getData(pageurl)

		#원두 리스트로 가져오기
		tmp = [td for td in pageSoup.find_all('a') if td.text.startswith('상품명')]
		beanListUrl = beanListUrl + tmp
		
	for beanUrl in beanListUrl:
		detailurl = 'https://www.namusairo.com/' + beanUrl['href']
		#해당 생두정보 가져오기
		beanSoup = getData(detailurl)
		text = str(beanSoup.find_all('tbody')[0])
		beanList.append(re.sub('<.+?>', '', text, 0).strip())
	#생두 정보 파싱
	for bean in beanList:
		tmp = {}
		test = bean.split('\n\n\n')
		#수량, 배송비 삭제
		del test[-1]
		del test[-1]
		
		for x in test:
			key, val = x.split('\n')
			tmp[key] = val
		df = df.append(tmp, ignore_index=True)
		
	return df
	
		
#리브레
def libre():
	#나무사이로 주소
	url = 'http://www.coffeelibre.kr/shop/listtotal.php?ca_id=20'

	#저장할 변수
	df = pd.DataFrame()
	soup = getData(url)

	pageUrl = []
	beanList = []
	beanList1 = []
	keyList = ['워싱스테이션', '농장명', '농장주', '생산자', '지역', '재배고도', '품종', '가공방식', '입고일', '커핑노트']
	valueList = []

	#제품 url 가져오기
	a = soup.find_all('a')
	for x in a:
		if x.text == "제품 상세":
			pageUrl.append(x['href'])
	  
	for beanUrl in pageUrl:
		pageSoup = getData(beanUrl)
		
		#원두 리스트로 가져오기
		text = str(pageSoup.find_all('b'))
		beanString = re.sub('<.+?>', '', text, 0).strip()
		
		text1 = str(pageSoup.find_all('title'))
		beanString1 = re.sub('<.+?>', '', text1, 0).strip()
		beanfrontData = beanString1.split('|')[0]
		
		start = beanString.find('원')
		end = beanString.find(', * 배송 안내,')
		beanData = beanString[start+3:end]
		beanData = beanData.replace(',', '')
		
		tmp = {}
		valueList = []
		country = beanfrontData.split('&gt;')
		tmp['나라'] = country[1]
		tmp['원두명'] = beanfrontData.split('(')[0][1:]
		endpoint = country[0].split('/')[-1].find('원')
		tmp['가격'] = country[0].split('/')[-1][1:endpoint]
		
		for x in keyList:
			if beanData.find(x+' /') != -1:
				valueList.append(beanData.find(x+' /'))
		valueList.sort()
		
		for x in range(len(valueList)-1):
			bean = beanData[valueList[x]:valueList[x+1]]
			try:
				key, val = bean.split(' /')
				tmp[key] = val
			except:
				pass
		df = df.append(tmp, ignore_index=True)
		
	return df


#gsc
def gsc():
	url = 'http://coffeegsc.co.kr/Product/OFFERINGLIST.aspx'
	beanUrl = 'http://coffeegsc.co.kr/Product/POP_OFFER.aspx?PLCODE='
	
	#저장할 변수
	df = pd.DataFrame()
	tmp = {}
	soup = getData(url)
	allBean = soup.find_all('span')[4:-1]
	price = soup.find_all('td', style='padding:10px 0 10px 0; text-align:right')[2::3]

	for i, bean in enumerate(allBean):
		tmp['name'] = bean.text
		tmp['price'] = price[i].text
		code = bean['onclick'].split("'")[1]
		
		beanRawData = getData(beanUrl + code)
		beanData = beanRawData.find_all('span')
		tmp['country'] = beanData[0].text
		
		
		beanDetail = beanRawData.find_all('td', {'style':re.compile("^font-family")})
		tmp['note'] = beanDetail[0].text.strip()
		tmp['processing'] = beanDetail[1].text.strip()
		tmp['variety'] = beanDetail[2].text.strip()
		tmp['harvest'] = beanDetail[3].text.strip()
		
		df = df.append(tmp, ignore_index=True)
		tmp = {}
		
	return df

#mi커피
def mi():
	#엠아이커피 주소
	url = 'http://micofftr3855.godomall.com/goods/green_bean_search.php'
	beanUrl = 'http://micofftr3855.godomall.com'
	pageUrl = 'http://micofftr3855.godomall.com/goods/'

	#저장할 변수
	df = pd.DataFrame()

	soup = getData(url)
	aTag = soup.find_all('a')
	pageUrlList = []
	keyList = ['Cupping Note', '가공방법', '농장/조합명', '원산지', '위치', '재배고도', '판매가', '품종', '수확시기']

	for a in aTag:
		if a.find_all('strong', class_ = 'item_name'):
			pageUrlList.append(a['href'])

	pages = soup.find_all('div', class_='pagination')[0].find_all('a')
	for page in pages:
		pageSoup = getData(pageUrl+page['href'][2:])
		aTag = pageSoup.find_all('a')
		for a in aTag:
			if a.find_all('strong', class_ = 'item_name'):
				pageUrlList.append(a['href'])
				
	for pageurl in pageUrlList:
		beanSoup = getData(beanUrl+pageurl[2:])
		dlTag = beanSoup.find_all('dl')
		tmp = {}
		for dl in dlTag:
			try:
				check = dl.find_all('dt')[0].text
				
				if check in keyList:
					key = dl.find_all('dt')[0].text
					val = dl.find_all('dd')[0].text.strip()
					tmp[key] = val
				
			except IndexError:
				pass
				
		df = df.append(tmp, ignore_index=True)
	
	return df

def meup():
	url = 'https://coffeemeup.biz/product/list.html?cate_no=50'
	#저장할 변수
	df = pd.DataFrame()

	soup = getData(url)
	li = soup.find_all('li', class_ = "Item xans-record-")
	tmp = {}
	for x in li:
		if x.find_all('img', {'alt' : '품절'}) == []:
			
			beanString = x.text
			namestart = beanString.find('상품명 : ')
			nameend = beanString.find('판매가 : ')
			priceend = beanString.find('상품 간략')
			name = beanString[namestart+6:nameend-2]
			price = beanString[nameend+6:priceend-2]
			
			tmp['상품명'] = name
			tmp['가격'] = price
			df = df.append(tmp, ignore_index=True)
	return df
	
	
def savenogales():
	df = nogales()
	saveDF(df, 'nogales')
	print('nogales')

def savenamu():
	df = namu()
	saveDF(df, 'namu')

def savegsc():
	df = gsc()
	saveDF(df, 'gsc')
	
def savelibre():
	df = libre()
	saveDF(df, 'libre')
	
def savemi():
	df = mi()
	saveDF(df, 'mi')
	
def savemeup():
	df = meup()
	saveDF(df, 'meup')
	
def check():
	print('call crontab')






