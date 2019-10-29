from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Create your views here.

def keyboard(request):
	return JsonResponse( {
		'type':'buttons',
		'buttons':['리브레', '나무사이로', 'gsc']
	} )

@csrf_exempt	
def answer(request):
	json_str = ((request.body).decode('utf-8'))
	received_json_data = json.loads(json_str)
	datacontent = received_json_data['content']
	
	if datacontent == '리브레':
		msg = '리브레에 오늘 입고된 생두는 2종입니다.'
		return JsonResponse({
			'message': {
				'text': msg
				},
		})
		
	elif datacontent == '나무사이로':
		msg = '나무사이로에 오늘 입고된 생두는 2종입니다.'
		return JsonResponse({
			'message': {
				'text': msg
				},
		})
		
	elif datacontent == 'gsc':
		msg = 'gsc에 오늘 입고된 생두는 2종입니다.'
		return JsonResponse({
			'message': {
				'text': msg
				},
		})