from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import time

import pandas as pd
from croller import *
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
	
	yesterdayData = pd.read_excel(siteName+yesterday+'.xlsx')
	try:
		todayData = pd.read_excel(siteName+today+'.xlsx')
		
	except FileNotFoundError:
		savenogales()
		savenamu()
		savegsc()
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
			
			
@csrf_exempt
def answer(request):
	json_str = ((request.body).decode('utf-8'))
	received_json_data = json.loads(json_str)
	datacontent = received_json_data['userRequest']['utterance']
	data = datacontent.split()[0]
	msg = ''
	if '자세히' in msg['text']:
		detailFlag = True
	
	
	if '사이트' in msg['text']:
		detailFlag = 'site'
	
	
	if '리브레' in data:
		compareData('libre', id, '리브레', detailFlag)

	elif '나무사이로' in data:
		compareData('namu', id, '나무사이로', detailFlag)

	elif 'gsc' in data:
		compareData('gsc', id, 'GSC', detailFlag)
		
	elif '노갈레스' in data:
		compareData('nogales', id, 'nogales', detailFlag)
	
	elif '새로운 원두' in msg['text']:
				compareData('namu', id, '나무사이로', detailFlag)
				compareData('nogales', id, 'nogales', detailFlag)
				compareData('gsc', id, 'GSC', detailFlag)
				compareData('libre', id, '리브레', detailFlag)
				
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