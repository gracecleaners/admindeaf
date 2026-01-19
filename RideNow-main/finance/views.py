import json

from django.conf import settings
from django.utils import timezone
from django.core import serializers
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponse, HttpRequest, JsonResponse, HttpResponseBadRequest

# from google_currency import convert 
# from currency_converter import CurrencyConverter
# from forex_python.converter import CurrencyRates

from core.models import SystemUtility
from .forms import DepositForm, TipForm
from accounts.models import User, User
from core.tasks import  send_sms_alert_task
from core.utils import info_message, create_action, send_email_alert, send_sms_alert
from .models import Payments, UserWallet, Ledger


def convertCurrency(amount, from_currency, to_currency):
	import urllib.parse
	import requests
	from jsonpath_ng import jsonpath, parse
	
	# setting the base URL value
	baseUrl = "https://v6.exchangerate-api.com/v6/0f215802f0c83392e64ee40d/pair/"
	# ask user to enter currency values
	from_value = from_currency
	to_value = to_currency
	# combine base URL with final URL including both currencies
	result = from_value+"/"+to_value
	final_url = baseUrl+result
	# send API call and retrieve JSON data
	json_data = requests.get(final_url).json()
	# set up jsonpath expression to select conversion rate
	jsonpath_expr = parse('$.conversion_rate')
	# use jsonpath expression to extract conversion rate
	result = jsonpath_expr.find(json_data)[0].value
	print("Conversion rate from "+from_value+" to "+to_value+" = ", result)
	converter = float(result*amount)
	return round(converter, 2)

	# ############ Using google_currency ###########
	# converter = convert(from_currency, to_currency, amount)
	# print(converter)
	# converted_amount = int(converter[2])
	# return round(converted_amount, 2)
	

def initiate_payment(request):
	if request.method == "POST":
		try:
			# Parse JSON body if the request contains JSON
			data = json.loads(request.body.decode('utf-8'))
			amount = data.get("amount")
			phone = data.get("phone")

			# Validate input
			if not amount or not phone:
				return JsonResponse({
					"error": "Both 'amount' and 'phone' are required."
				}, status=400)

			# Save payment in the database
			payment = Payments.objects.create(
				phone=phone,
				amount=amount,
				note="Payment from Shukrani Foods",
				initiated_by=request.user,
			)

			# Return success response
			return JsonResponse({
				"payment_id": payment.id,
				"message": "Payment initiated successfully."
			})

		except Exception as e:
			print("Error in Initiate Payment: ", e)
			# Handle unexpected server errors
			return JsonResponse({
				"error": "An error occurred while initiating the payment.",
				"details": str(e)
			}, status=500)

	# Handle non-POST requests
	return JsonResponse({
		"error": "Invalid request method. Only POST is allowed."
	}, status=405)

def get_payment_update(request, id=id):
	is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
	if is_ajax:
		if request.method == 'GET':
			payment = Payments.objects.get(id=id)
			status = payment.is_complete

			is_complete =  status
			declined = payment.declined
			id = payment.id
			dataSet = {'id':id, 'status':status, 'paymentDeclined':declined}
			return JsonResponse({'context': dataSet})
		return JsonResponse({'status': 'Invalid request'}, status=400)
	else:
		return HttpResponseBadRequest('Invalid request')
	


def send_subscription_email(email, plan_name, end_date):
    subject = 'Subscription Confirmation'
    message = f'Thank you for subscribing to {plan_name}! Your subscription is active until {end_date}.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


@login_required
def user_wallet(request, id, username):
	try:
		user = User.objects.get(id=id)
		profile = User.objects.get(user=user, username=username)
		try:
			wallet = UserWallet.objects.get(owner=profile)
		except UserWallet.DoesNotExist:
			messages.warning(request, '<h5>Sorry, could not find wallet! Activate your wallet by depositing some funds</h5>')
			return redirect('wallet_deposit', profile.pk)
		return render(request, 'finance/user_wallet.html', {'user':user, 'profile':profile, 'wallet':wallet})
	except User.DoesNotExist or UserWallet.DoesNotExist:
		messages.error(request, 'Could not obtain user and profile. You are not authorized!')
		return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))