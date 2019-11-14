from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import time

import pandas as pd
from .croller import *
from datetime import date, timedelta

# Create your views here.
def keyboard(request):
	return JsonResponse( {
		'type':'buttons',
		'buttons':['리브레', '나무사이로', 'gsc']
	} )
	
def compareData(siteName, id, name, detail):
	today = date.today().strftime('%y%m%d')
	yesterday = (date.today()-timedelta(1)).strftime('%y%m%d')
	
	yesterdayData = pd.read_excel('xlsx/'+siteName+yesterday+'.xlsx')
	try:
		todayData = pd.read_excel('xlsx/'+siteName+today+'.xlsx')
		
	except FileNotFoundError:
		if siteName == 'namu':
			savenamu()
		elif siteName == 'nogales':
			savenogales()
		elif siteName == 'gsc':
			savegsc()
		elif siteName == 'libre':
			savelibre()
	
	siteKey = {'namu': '상품명', 'gsc': 'name', 'libre': '원두명', 'mi': '농장/조합명', 'nogales': 'Farm'}
	siteURL = {'namu': 'https://www.namusairo.com/product/list.html?cate_no=24', 
	'gsc': 'http://coffeegsc.co.kr/Product/OFFERINGLIST.aspx', 
	'libre': 'http://www.coffeelibre.kr/shop/listtotal.php?ca_id=20', 
	'nogales': 'https://www.cafenogales.co.kr/shop'}
	key = siteKey[siteName]
	
	todayNewData = getNewData(yesterdayData, todayData, key)
	
	if todayNewData.empty:
		msg = name+'에 새로운 원두가 없습니다.'
		
		if detail == 'site':
			msg = siteURL[siteName]
		
	else:
		if detail == True:
			msg = name+'에 새로운 원두가'+ str(len(todayNewData))+'건 입고되었습니다.\n' + str(todayNewData[key])
			
		elif detail == 'site':
			msg = siteURL[siteName]
			
			
		else:
			msg = name+'에 새로운 원두가'+ str(len(todayNewData))+'건 입고되었습니다.'
			
	return msg
	
@csrf_exempt
def answer(request):
	json_str = ((request.body).decode('utf-8'))
	received_json_data = json.loads(json_str)
	datacontent = received_json_data['userRequest']['utterance']
	data = datacontent.split()[0]
	msg = ''
	detailFlag = False
	
	if '자세히' in data:
		detailFlag = True
	
	
	if '사이트' in data:
		detailFlag = 'site'
	
	
	if '리브레' in data:
		msg = compareData('libre', id, '리브레', detailFlag)

	elif '나무사이로' in data:
		msg = compareData('namu', id, '나무사이로', detailFlag)

	elif 'gsc' in data:
		msg = compareData('gsc', id, 'GSC', detailFlag)
		
	elif '노갈레스' in data:
		msg = compareData('nogales', id, 'nogales', detailFlag)
	
	elif '새로운 원두' in data:
				msg = compareData('namu', id, '나무사이로', detailFlag)
				msg = msg + compareData('nogales', id, 'nogales', detailFlag)
				msg = msg + compareData('gsc', id, 'GSC', detailFlag)
				msg = msg + compareData('libre', id, '리브레', detailFlag)
				
	else:
		msg = data + '는 이해하지 못했습니다.'


	return JsonResponse({
		'version': "2.0",
		'template': {
			'outputs': [ {
				'simpleText': {
					'text': msg
				}
			} ]
		}
	})