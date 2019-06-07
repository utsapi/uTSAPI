'''unofficial API client for the tagesschau.de show archive (based on HTML requests)
Provided without any warranty
Might break any time without a fix'''

from datetime import datetime
import bs4
import requests
import re

BASE = 'https://www.tagesschau.de'
PROTOCOL_DOWNLOAD = 'https:'

class TagesschauArchiveAPI(object):
	def get_earliest_available_date(self):
		return '2007-04-01'
		
	def get_info_from_date(self, date, shownames = ['tagesschau','tagesthemen']):
		'''Returns a dict with name of the show (and time if show is "tagesschau") and the direct url to the show
		Format of date is a string of the international format: YEAR-MONTH-DAY (e.g. 2019-05-06)'''
		
		result = {}
		dt = datetime.strptime(date,'%Y-%m-%d')
		#~ print(dt)
		#~ exit()
		r = requests.get(f'https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-{dt.year}{dt.month:02}{dt.day:02}.html')
		if 'Für diesen Tag liegen keine Archiveinträge vor.'  in r.text:
			return result
		soup = bs4.BeautifulSoup(r.text, 'html.parser')
		h4s = soup.find_all('h4',  {'class':['headline']})
		dz_ps = soup.find_all('p',  {'class':['dachzeile']})
		#~ tt_ps = soup.find_all('p',  {'class':['teasertext','']})
		times = []
		for p in dz_ps:
			text = p.text
			x = re.search(r'20\d\d (\d\d:\d\d Uhr)', text)
			times.append(x.group(1))
		#~ for p in tt_ps:
			#~ print(p)
		for idx,h4 in enumerate(h4s):
			if h4.a.text.strip() in shownames:
				url = BASE + h4.a.get('href')
				result[f'{h4.a.text.strip()} {times[idx]}'] = url
			else:
				print(f'Skipping {h4.a.text.strip()!r}...')
		return result
		
	def get_links_from_show_url(self, url, show, funnythings_on = False):
		funnythings = []
		print(f'Requesting {show}...')
		r = requests.get(url)
		soup = bs4.BeautifulSoup(r.text, 'html.parser')
		tt_ps = soup.find_all('p',  {'class':['teasertext']})
		themen = None
		hinweis = None
		for tt_p in tt_ps:
			if tt_p.text.startswith('Hinweis'):
				hinweis = tt_p.text.replace('Hinweis: ','')
			elif tt_p.text.startswith('Themen der Sendung'):
				themen = tt_p.text.replace('Themen der Sendung: ','')
		div = soup.find('div',  {'class':['controls']})
		ps = div.previous_sibling.previous_sibling
		result = []
		if ps:
			if 'Download' in ps.text:
				links = div.find_all('div',  {'class':['button']})
				for link in links:
					a = link.a
					#~ q = a.text.strip().replace(' (h264)','')
					#~ print(q)
					
					#~ if 'HD' in a.text:
					href = a.get('href')
					if href != '':
						DLL = PROTOCOL_DOWNLOAD + href
						result.append(DLL)
					else:
						funnythings.append(f'Check {url} for ')
		else:
			check = f'Check {url!r} for some potential fun/funny thing!'
			print(check)
			funnythings.append(check)
		if funnythings_on:
			return result, themen, hinweis, funnythings
		else:
			return result, themen, hinweis, None