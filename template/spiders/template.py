import re
import csv
import scrapy
import datetime
import codecs

class BoostSpider(scrapy.Spider):
	name                   = 'boost'
	allowed_domains        = ['ssp.isboost.co.jp']
	handle_httpstatus_list = [303, 302, 301, 200]
	custom_settings        = {
		'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
	}
	cookie_var             = {}

	def start_requests(self):
		url                = 'https://ssp.isboost.co.jp/app/login'

		yield scrapy.Request(url=url, callback=self.parse_boost)

	def parse_boost(self, response):
		self.get_cookies(response.headers.getlist('Set-Cookie'))
		url                = 'https://ssp.isboost.co.jp/heimdallr/login'
		formdata           = {
			'domain': 'ssp.isboost.co.jp',
			'client_id': 'aladdin',
			'redirect_uri': 'https://ssp.isboost.co.jp/app/login/check-custom',
			'response_type': 'code',
			'service': 'aladdin',
			'username': '***',
			'password': '****',
			'_submit': 'Log in',
		}

		yield scrapy.FormRequest(url=url, formdata=formdata, method='POST', cookies=self.cookie_var, callback=self.parse_login)

	def parse_login(self, response):
		url                = response.headers['Location'].decode('utf-8')
		self.get_cookies(response.headers.getlist('Set-Cookie'))
		meta               = {
			'dont_redirect': True,
		}

		yield scrapy.Request(url=url, cookies=self.cookie_var, meta=meta, dont_filter=True, callback=self.parse_check)
		
	def parse_check(self, response):
		self.get_cookies(response.headers.getlist('Set-Cookie'))
		url                = 'https://ssp.isboost.co.jp/app/'
		meta               = {
			'dont_redirect': True,
		}

		yield scrapy.Request(url=url, cookies=self.cookie_var, meta=meta, dont_filter=True, callback=self.parse_app)

	def parse_app(self, response):
		url                = 'https://ssp.isboost.co.jp/app/download'
		today              = datetime.datetime.today()
		yesterday          = today + datetime.timedelta(days=-1)
		if today.hour      > 0:
			csv_date       = str(today.year) + "/" + str(today.month) + "/" + str(today.day)
		else:
			csv_date       = str(yesterday.year) + "/" + str(yesterday.month) + "/" + str(yesterday.day)
		formdata           = {
			'domain': 'ssp.isboost.co.jp',
			'client_id': 'aladdin',
			'redirect_uri': 'https://ssp.isboost.co.jp/app/login/check-custom',
			'response_type': 'code',
			'service': 'aladdin',
			'username': 'boost-****',
			'password': '****',
			'_submit': 'Log in',
			'search_report[startDate]': csv_date, 
			'search_report[endDate]': csv_date,
			'search_report[publisherRadio]': '0',
			'search_report[mediaRadio]': '0',
			'search_report[zoneRadio]': '0',
			'search_report[adsourceRadio]': '0',
			'search_report[masterAdnetworkRadio]': '0',
			'search_report[mediaTypeRadio]': '0',
			'search_report[zoneTypeRadio]': '0',
			'search_report[ownedLampRadio]': '0',
			'search_report[groupByDate]': '1',
			'search_report[groupByZone]': '1',
			'search_report[groupByAdSource]': '1',
			'fileType': 'csv',
			'search_report[vendorId]': '81',
			'search_report[publisherId]': '',
			'search_report[lampVendorId]': '139',
		}
		yield scrapy.FormRequest(url=url, formdata=formdata, cookies=self.cookie_var, callback=self.parse_download)

	def parse_download(self, response):
		csv                = open('./test.csv', 'w')
		csv.write(response.body.decode('cp932'))
		csv.close()
		print('done!')

	def get_cookies(self, t_cookie):
		if len(t_cookie) > 0:
			cookie_list = []
			for val in t_cookie:
				value      = val.decode('utf-8')
				cookie_list.extend(list(i for i in value.split(';')))
			for var in cookie_list:
				if 'genieeadserver' in var:
					self.cookie_var['genieeadserver'] = var.split('genieeadserver=')[1]
				elif 'authenticator' in var:
					self.cookie_var['authenticator'] = var.split('authenticator=')[1]