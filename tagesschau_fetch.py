import requests
import bs4
import time
import json
from datetime import datetime

from tagesschauAPI import TagesschauArchiveAPI

tsAPI = TagesschauArchiveAPI()

DLL_object = {}
funnythings = []

for year in range(2007,2020):
	DLL_object[year] = {}
	for month in range(1,13):
		if year == 2007:
			if month != 4:
				continue
		DLL_object[year][month] = {}
		for day in range(1,32):
			try:
				dt = datetime.strptime(f'{year}{month:02}{day:02}','%Y%m%d')
			except ValueError:
				#~ Invalid date 
				print(f'Skipping invalid date {year}-{month:02}-{day:02}...')
				continue
			if dt.timestamp() > time.time():
				continue
			print(f'Requesting {year}-{month:02}-{day:02}')
			DLL_object[year][month][day] =  {}
			DLL_object[year][month][day]['date_formatted'] = f'{year}-{month:02}-{day:02}'
			links = tsAPI.get_info_from_date(f'{year}-{month:02}-{day:02}')
			#~ exit()
			for show, link in links.items():
				DLL_links, themen, hinweis, funnnythings_temp = tsAPI.get_links_from_show_url(link, show, funnythings_on = True)
				funnythings.extend(funnnythings_temp)
				DLL_object[year][month][day][show] =  {'url': link}
				if hinweis:
					DLL_object[year][month][day][show]['info'] = hinweis
				if themen:
					DLL_object[year][month][day][show]['topics'] = themen
				if DLL_links != []:
					DLL_object[year][month][day][show]['mp4_urls'] = DLL_links
				else:
					if not 'links' in DLL_object[year][month][day][show]:
						DLL_object[year][month][day][show]['mp4_urls'] = DLL_links
			#~ print(json.dumps(DLL_object, indent = 4))
			#~ exit()
									
with open('sendungsarchiv-tagesschau.json', 'w') as f:
	f.write(json.dumps(DLL_object, indent = 4))
	
with open('sendungsarchiv-fehler.json', 'w') as f:
	f.write(json.dumps(funnythings, indent = 4))
	