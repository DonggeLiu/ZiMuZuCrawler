#coding=GBK

import sys
import re
import requests
import time
import datetime
import json
from bs4 import BeautifulSoup
import os
import io
import codecs
import copy

DIRECTORY = '/Users/donggeliu/kit/ZiMuZu/'
UPDATED_RESOURCES = DIRECTORY+'updatedResources.txt'
DOWNLOADED_RESOURCES = DIRECTORY+'downloadedResources.txt'

TODAY_SITE = 'http://www.zimuzu.tv/today'
SIGNIN_SITE = "http://www.zimuzu.tv/user/sign"
LOGIN_SITE = "http://www.zimuzu.tv/user/login/ajaxLogin"

PREFERRED_MOIVE_CATEGORIES = ['电影']
PREFERRED_MOIVE_RESOLUTIONS = ["720P"]

PREFERRED_SHOW_CATEGORIES = ['美剧', '日剧', 'mini剧', '电视剧']
PREFERRED_SHOW_RESOLUTIONS = ['HR-HDTV']
PREFERRED_SOURCE_TYPE = ['驴', '迅雷']


USER_INFO = dict(account='your_account', password='your_password', url_back='http://www.zimuzu.tv/user/user')
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

TODAY = str(datetime.date.today()).split('-')[2]


def login():
	user = requests.Session()
	login_page = user.post(LOGIN_SITE, data=USER_INFO, headers=HEADERS)
	loginInfo = json.loads(login_page.text)
	report(loginInfo)
	return user

	

def report(loginInfo):
	if loginInfo['status'] == 1:
		print("Login successfully: " + USER_INFO['account'])
		return
	print("Login failed: " + loginInfo['status'])



def read_from_updated_file():
	read_updated_file = open(UPDATED_RESOURCES, 'r', encoding="utf-8")
	raw_updated_lines = read_updated_file.readlines()
	read_updated_file.close()
	return raw_updated_lines


def signin(user, raw_updated_lines):

	if not is_today(raw_updated_lines):
		sign_in_page = user.get(SIGNIN_SITE)
		sign_in_page = user.get(SIGNIN_SITE)
		# updated_lines[0] = today + '\n'
	return raw_updated_lines

def is_today(raw_updated_lines):

	return (raw_updated_lines[0][:-1] == TODAY)


def prepare_new_shows(user):
	show_items = fetch_new_shows(user)
	show_items = fix_formart(show_items)
	return show_items

def fetch_new_shows(user):
	show_items = []

	released_today = user.get(TODAY_SITE)
	released_today_page = released_today.text
	released_todaySoup = BeautifulSoup(released_today_page, "html.parser")

	released_today_shows = released_todaySoup.find_all('div')[19].find_all('tr')

	
	for show in released_today_shows:
		if(not show.find_all("td")): continue
		category = show.find_all("td")[0].string
		resolution = show.find_all("td")[1].string

		if is_preferred_show(category, resolution):
			show_name = show.a.string

			links = show.find_all("td")[3].find_all('a')
			source_link = ''
			for link in links:
				source_type = link.string
				if is_preferred_source_type(source_type):
					source_link = link.get('href')
					break
			if source_link:
				show_items.append([show_name, category, resolution, source_link])

	return show_items

def is_preferred_show(category, resolution):

	if (category in PREFERRED_SHOW_CATEGORIES):
		return (resolution in PREFERRED_SHOW_RESOLUTIONS)

	if (category in PREFERRED_MOIVE_CATEGORIES):
		return (resolution in PREFERRED_MOIVE_RESOLUTIONS)

	return False


def is_preferred_source_type(source_type):
	return (source_type in PREFERRED_SOURCE_TYPE)


def fix_formart(show_items):

	for show_item in show_items:
		if is_movie(show_item):
			show_item = fix_movie_format(show_item)
		elif is_show(show_item):
			show_item = fix_show_format(show_item)
	return show_items

def is_movie(show_item):
	return show_item[1] in PREFERRED_MOIVE_CATEGORIES

def fix_movie_format(show_item):
	show_item.insert(1, ['',''])
	show_item.insert(1, '')
	return show_item


def is_show(show_item):
	return show_item[1] in PREFERRED_SHOW_CATEGORIES



def fix_show_format(show_item):

	show_item = fix_show_episode(show_item)
	show_item = fix_show_name(show_item)

	return show_item

def fix_show_episode(show_item):

	episode = recognise_show_episode(show_item)

	show_item[0] = re.sub(episode[0], "", show_item[0], flags=re.IGNORECASE)
	show_item[0] = re.sub(episode[1], "NAME_SEPERATOR", show_item[0], flags=re.IGNORECASE)

	episode[1] = episode[1].replace('EP', 'E')

	show_item.insert(1, episode)
	return show_item

def recognise_show_episode(show_item):

	episode = re.findall(r'(S*[0-9]*)?(Ep?[0-9]+)', show_item[0], flags=re.IGNORECASE)
	episode = [list(x) for x in episode]
	if len(episode) > 0:
		episode = episode[0]
		episode = [episode[0].upper(), episode[1].upper()]
	else:
		episode = ['S00', 'E00']

	return episode


def fix_show_name(show_item):
	names = recognise_show_name(show_item)

	chinese_name = fix_chinese_name(names['chinese'])
	english_name = fix_english_name(names['english'])

	show_item.insert(0, english_name)
	show_item[1] = chinese_name

	return show_item


def recognise_show_name(show_item):

	full_name = re.findall(r'(.*).NAME_SEPERATOR.', show_item[0])
	if len(full_name) > 0:
		chinese_name = re.findall(r'(.*?)\.[A-Za-z0-9\-]*', full_name[0], flags=re.IGNORECASE)
		english_name = re.findall(r'\.([A-Za-z0-9\-].*)', full_name[0], flags=re.IGNORECASE)
	else:
		chinese_name = ['未知']
		english_name = ['Undetermined']
	names = dict(english=english_name, chinese=chinese_name)

	return names

def fix_chinese_name(chinese_name):
	chinese_name = [x for x in chinese_name if x]

	if len(chinese_name) == 0 or (len(chinese_name) == 1 and chinese_name[0] == '中英'):
		chinese_name = ''
	elif (len(chinese_name) == 1 and chinese_name[0] != '中英'):
		chinese_name = chinese_name[0]
	elif (len(chinese_name) == 2):
		chinese_name = chinese_name[1]

	return chinese_name

def fix_english_name(english_name):

	english_name = [x for x in english_name if x]
	if english_name:
		english_name = english_name[0].split('.')
	english_name = " ".join(english_name).lower()
	
	return english_name


def check_new(show_items):
	updated_show_items = recognise_updated_show_items()
	downloaded_show_items = recognise_downloaded_show_items()
	new_show_items = filter_shows(show_items, updated_show_items, downloaded_show_items)
	return new_show_items


def recognise_updated_show_items():
	updated_show_items = []
	for line in raw_updated_lines:
		if (raw_updated_lines.index(line) == 0) or not line: continue
		updated_show_items.append(line.split('\t\t'))
	return updated_show_items


def recognise_downloaded_show_items():
	downloaded_file = open(DOWNLOADED_RESOURCES, 'r', encoding="utf-8")
	downloaded_lines = downloaded_file.readlines()
	downloaded_show_items = []
	for line in downloaded_lines:
		if not line: continue
		downloaded_show_items.append(line.split('\t\t'))
	return downloaded_show_items


def filter_shows(show_items, updated_show_items, downloaded_show_items):
	new_show_items = filter_from_updated(show_items, updated_show_items)
	final_show_items = filter_from_downloaded(new_show_items, downloaded_show_items)
	return final_show_items

def filter_from_updated(show_items, updated_show_items):
	new_show_items = []
	for show_item in show_items:
		exists = False;
		for updated_show_item in updated_show_items:
			if (show_item[0] == updated_show_item[0]) and (show_item[1] == updated_show_item[1]):
				if show_item[3] in PREFERRED_SHOW_CATEGORIES:
					if (not updated_show_item[2] and updated_show_item[3] == show_item[2][1])\
					 or (updated_show_item[2] == show_item[2][0] and updated_show_item[3] == show_item[2][1]):
						exists = True
				if (show_item[3] in PREFERRED_MOIVE_CATEGORIES):
					exists = True

		if(not exists):
			if (type(show_item[0]) == str) and (type(show_item[1]) == str):
				new_show_items.append(show_item[0] + '\t\t' + show_item[1] + '\t\t' + show_item[2][0] + '\t\t' + show_item[2][1] + '\t\t' + show_item[5] + '\t\t' +'\n')
	return new_show_items


def filter_from_downloaded(new_show_items, downloaded_show_items):


	new_show_list = []
	for show_item in new_show_items:
		new_show_list.append(show_item.split('\t\t'))
	tmp_new_show_list = copy.copy(new_show_list)

	for downloaded_show_item in downloaded_show_items:
		for new_show_item in tmp_new_show_list:
			if not new_show_item: continue
			if in_same_series(new_show_item, downloaded_show_item):
				if not newer(new_show_item, downloaded_show_item):
					for item in new_show_list:
						if item == new_show_item:
							new_show_list.remove(new_show_item)

	final_show_items = []
	for show_item in new_show_list:
		final_show_items.append(show_item[0] + '\t\t' + show_item[1] + '\t\t' + show_item[2] + '\t\t' + show_item[3] + '\t\t' + show_item[4] + '\t\t' +'\n')

	return final_show_items



def in_same_series(drama_1, drama_2):
	# print(drama_1[0] + ':' + drama_2[0])
	if drama_1[0] and drama_2[0] and drama_1[1] and drama_2[1]:
		return (drama_1[0] == drama_2[0]) or (drama_1[1] == drama_2[1])

	if (not drama_1[1]) or (not drama_2[1]):
		return (drama_1[0] == drama_2[0])

def newer(drama_1, drama_2):
	# print(drama_1[0] + ':' + drama_2[0])
	# print(drama_1[2] + ':' + drama_2[2])
	# print(drama_1[3] + ':' + drama_2[3])
	if drama_1[2] > drama_2[2]:
		return True
	if drama_1[3] > drama_2[3]:
		return True
	return False


def write_new_show_items(raw_updated_lines, new_show_items):

	
	write_updated_file = open(DIRECTORY+'updatedResources.txt', 'w', encoding="utf-8")

	raw_updated_lines[0] = TODAY + '\n'

	write_updated_file.writelines(raw_updated_lines)
	write_updated_file.writelines(new_show_items)
	write_updated_file.close()


def send_message(new_show_items):
	message = ''
	num = 0

	for item in new_show_items:
		num += 1
		item = item.split('\t\t')
		item_info = dict(english_name = item[0].replace(' ', '\ '), chinese_name = item[1].replace(' ', '\ '), season = item[2], episode = item[3])
		message += str(num) + '.\ ' + item_info['english_name'] + '\ ' + item_info['chinese_name'] + '\ ' + item_info['season'] + '\ ' + item_info['episode'] + 'NewLine'

	if message:
		os.system('Ruby /Users/donggeliu/kit/TelstraMessenger/send_to_me.rb' + ' ' + message)



if __name__ == '__main__':
	print(datetime.datetime.now())
	user = login()
	raw_updated_lines = read_from_updated_file()
	raw_updated_lines = signin(user, raw_updated_lines)
	show_items = prepare_new_shows(user)
	new_show_items = check_new(show_items)
	# print(new_show_items)
	write_new_show_items(raw_updated_lines, new_show_items)
	# send_message(new_show_items)
	print("Updated Successfully")
