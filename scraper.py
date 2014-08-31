from bs4 import BeautifulSoup
import requests
import collections
import json
import random
import time
import sys
import scraperwiki
import os

class CalendarScraper:

	def __init__(self, debug=True):
	        self.cookies = {}
	        self.debug = debug

	def cal_url(self,r_id,s_date,e_date,key_id):
	        return ('https://www.airbnb.com/api/v1/listings/%s/calendar?start_date=%s&end_date=%s&key=%s&locale=en'
	                % (r_id,s_date,e_date,key_id))

	def get(self,url, referer='', min_sleep=30, max_add=120, xhr=False):
	        if self.debug:
	            print url

	        time.sleep(random.randint(0, max_add) + min_sleep)

	        headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Version/7.0.5 Safari/537.77.4',
	                   'referer': referer}
	        if xhr:
	            headers['x-requested-with'] = 'XMLHttpRequest'

	        r = requests.get(url, headers=headers, cookies=self.cookies)
	        self.cookies = r.cookies

	        return r

	def cal_status(self,r_id):
		try:
			url = "https://www.airbnb.com/rooms/" + str(r_id)
			r  = self.get(url, referer='https://www.airbnb.com/s/Bali--Indonesia')
			data = r.text
			soup = BeautifulSoup(data)
			d = soup.find("meta", {"id":"_bootstrap-layout-init"})['content']
			json_data = json.loads(d)
			key_id = json_data['api_config']['key']
			date_now = time.strftime('%Y-%m-%d')
			r_cal = requests.get(self.cal_url(r_id,date_now,date_now,key_id))
			js = json.loads(r_cal.content)
			return str(js['calendar']['dates'][0]['available'])
		except:
			return "Error"

	def crawl(self):
		if 'MORPH_SEAGULL' in os.environ:
			api_key = os.environ['MORPH_SEAGULL']
		r = requests.get("https://api.morph.io/sicvermilion/airbnb_scraper_1/data.json?key="+ api_key +"&query=select%20*%20from%20'data'%20limit%203", verify=False)
		js = json.loads(r.content)
		for listing in js:
			scraperwiki.sqlite.execute("INSERT OR IGNORE INTO swdata VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",\
				[listing['id'], listing['user_id'], listing['name'], listing['address'], listing['lat'], listing['lng'],listing['price_native'], listing['property_type'], listing['user_name'], listing['room_type_category'], listing['url'], listing['picture_url'],0,0,datetime.utcnow(),1])
			scraperwiki.sqlite.commit()
			qwerty = self.cal_status(listing['id'])
			if qwerty == 'True':
				scraperwiki.sqlite.execute("UPDATE swdata SET tracking_count=tracking_count+1, last_tracking=? WHERE id=?", [datetime.utcnow,listing['id']])
			elif qwerty == 'False':
				scraperwiki.sqlite.execute("UPDATE swdata SET tracking_count=tracking_count+1, last_tracking=?, income=income+? WHERE id=?", [datetime.utcnow, listing['price'], listing['id']])
			elif qwerty == 'Error':
				scraperwiki.sqlite.execute("UPDATE swdata SET status=0 WHERE id=?", [listing['id']])
			scraperwiki.sqlite.commit()

if __name__ == "__main__":
	scraperwiki.sqlite.execute('CREATE TABLE IF NOT EXISTS swdata (id INT PRIMARY KEY, user_id INT, name TEXT, address TEXT, lat REAL, lng REAL,price_native INT, property_type TEXT, user_name TEXT, room_type_category TEXT, url TEXT,picture_url TEXT, income INT, tracking_count INT, last_tracking DATE, status INT)')
	scraperwiki.sqlite.commit()
	d = CalendarScraper()
	d.crawl()
	
