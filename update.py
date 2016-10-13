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

# ================================== Files ================================== #
CURRENT_DIRECTORY = './'
UPDATED_RESOURCES = CURRENT_DIRECTORY+'updatedResources.txt'
DOWNLOADED_RESOURCES = CURRENT_DIRECTORY+'downloadedResources.txt'
CREDENTIALS = CURRENT_DIRECTORY+'credentials.config'

# ================================== Sites ================================== #

TODAY_SITE = 'http://www.zimuzu.tv/today'
SIGNIN_SITE = "http://www.zimuzu.tv/user/sign"
LOGIN_SITE = "http://www.zimuzu.tv/user/login/ajaxLogin"

# =============================== Preferences =============================== #

ACCOUNT_NAME_LINE = 3
PASSWORD_LINE = 6
PREFERRED_MOVIE_CATEGORIES_LINE = 9
PREFERRED_MOVIE_RESOLUTIONS_LINE = 12
PREFERRED_SHOW_CATEGORIES_LINE = 15
PREFERRED_SHOW_RESOLUTIONS_LINE = 18
PREFERRED_SOURCE_TYPE_LINE = 21

HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}

# ================================== Date =================================== #

TODAY = str(datetime.date.today()).split('-')[2]

# ================================== Codes ================================== #


# ================================ Stage 00 ================================= #

# Read credentials
def collect_infos():
	global USER_INFO
	global PREFERRED_MOVIE_CATEGORIES
	global PREFERRED_MOVIE_RESOLUTIONS
	global PREFERRED_SHOW_CATEGORIES
	global PREFERRED_SHOW_RESOLUTIONS
	global PREFERRED_SOURCE_TYPE

	credential_file = open(CREDENTIALS, 'r', encoding="utf-8")
	credentials = credential_file.readlines()
	credential_file.close()

	ACCOUNT_NAME = collect_pref(ACCOUNT_NAME_LINE, credentials)[0]
	PASSWORD = collect_pref(PASSWORD_LINE, credentials)[0]
	
	PREFERRED_MOVIE_CATEGORIES = collect_pref( \
		PREFERRED_MOVIE_CATEGORIES_LINE, credentials)

	PREFERRED_MOVIE_RESOLUTIONS = collect_pref( \
		PREFERRED_MOVIE_RESOLUTIONS_LINE, credentials)

	PREFERRED_SHOW_CATEGORIES = collect_pref( \
		PREFERRED_SHOW_CATEGORIES_LINE, credentials)
	
	PREFERRED_SHOW_RESOLUTIONS = collect_pref( \
		PREFERRED_SHOW_RESOLUTIONS_LINE, credentials)
	
	PREFERRED_SOURCE_TYPE = collect_pref( \
		PREFERRED_SOURCE_TYPE_LINE, credentials)

	USER_INFO = dict(account=ACCOUNT_NAME, password=PASSWORD, \
		url_back='http://www.zimuzu.tv/user/user')


# Collect each preference from the CREDENTIALS
def collect_pref(pref, lines):
	return lines[pref][:-1].split("\t\t")


# ================================ Stage 01 ================================= #

# Log into zimuzu.tv
def login():
	user = requests.Session()
	login_page = user.post(LOGIN_SITE, data=USER_INFO, headers=HEADER)
	loginInfo = json.loads(login_page.text)
	report(loginInfo)
	return user

# Report whether the login process is successful
def report(loginInfo):
	if loginInfo['status'] == 1:
		print("Login successfully: " + USER_INFO['account'])
		return
	print("Login failed: " + str(loginInfo['info']))

# ================================ Stage 02 ================================ #

# Collect the dramas that have been updated in UPDATED_RESOURCES but did not downloaded
def read_from_updated_file():
	read_updated_file = open(UPDATED_RESOURCES, 'r', encoding="utf-8")
	raw_updated_lines = read_updated_file.readlines()
	read_updated_file.close()
	return raw_updated_lines


# ================================ Stage 03 ================================= #

# TODO: Check-in functions to be implemented in the future
def checkIn(user, raw_updated_lines):

	if not is_today(raw_updated_lines):
		sign_in_page = user.get(SIGNIN_SITE)
		sign_in_page = user.get(SIGNIN_SITE)
		# updated_lines[0] = today + '\n'
	return raw_updated_lines

# checks if this is the first update of today
def is_today(raw_updated_lines):

	return (raw_updated_lines[0][:-1] == TODAY)


# ================================ Stage 04 ================================= #

# fetch newly updated dramas and put them into required format
def prepare_new_dramas(user):
	drama_items = fetch_new_dramas(user)
	drama_items = fix_formart(drama_items)
	return drama_items


# Fetch newly updated dramas from TODAY_SITE
def fetch_new_dramas(user):
	drama_items = []

	released_today = user.get(TODAY_SITE)
	released_today_page = released_today.text
	released_todaySoup = BeautifulSoup(released_today_page, "html.parser")
	released_today_dramas = released_todaySoup.find_all('div')[19].find_all('tr')

	for drama in released_today_dramas:
		if(not drama.find_all("td")): continue
		category = drama.find_all("td")[0].string
		resolution = drama.find_all("td")[1].string

		if is_preferred_drama(category, resolution):
			drama_name = drama.a.string

			links = drama.find_all("td")[3].find_all('a')
			source_link = ''
			for link in links:
				source_type = link.string
				if is_preferred_source_type(source_type):
					source_link = link.get('href')
					break
			if source_link:
				drama_items.append([drama_name, category, resolution, source_link])

	return drama_items


# Check if the category and resolution of a given drama is preferred
def is_preferred_drama(category, resolution):

	if (category in PREFERRED_SHOW_CATEGORIES):
		return (resolution in PREFERRED_SHOW_RESOLUTIONS)

	if (category in PREFERRED_MOVIE_CATEGORIES):
		return (resolution in PREFERRED_MOVIE_RESOLUTIONS)

	return False


# Check if the source type of the given drama is preferred
def is_preferred_source_type(source_type):
	return (source_type in PREFERRED_SOURCE_TYPE)


# Fix the format of given drama
def fix_formart(drama_items):

	for drama_item in drama_items:
		if is_movie(drama_item):
			drama_item = fix_movie_format(drama_item)
		elif is_TV(drama_item):
			drama_item = fix_TV_format(drama_item)
		# TODO: add more filters
		# elif is_other_category(drama_item):
		# 	drama_item = fix_other_category_format(drama_item)
	return drama_items


# Check if given drama is a movie
def is_movie(drama_item):
	return drama_item[1] in PREFERRED_MOVIE_CATEGORIES


# Fix the format of movie info
def fix_movie_format(drama_item):
	drama_item.insert(1, ['',''])
	drama_item.insert(1, '')
	return drama_item


# Check if given drama is a TV series
def is_TV(drama_item):
	return drama_item[1] in PREFERRED_SHOW_CATEGORIES


# Fix the format of TV series info
def fix_TV_format(drama_item):

	drama_item = fix_drama_episode(drama_item)
	drama_item = fix_drama_name(drama_item)

	return drama_item


# Fix the episode info of TV series to be identified
def fix_drama_episode(drama_item):

	episode = identify_drama_episode(drama_item)

	drama_item[0] = re.sub(episode[0], "", drama_item[0], flags=re.IGNORECASE)
	drama_item[0] = re.sub(episode[1], "NAME_SEPERATOR", drama_item[0], flags=re.IGNORECASE)

	episode[1] = episode[1].replace('EP', 'E')

	drama_item.insert(1, episode)
	return drama_item



# Identify the episode of given drama
def identify_drama_episode(drama_item):

	episode = re.findall(r'(S*[0-9]*)?(Ep?[0-9]+)', drama_item[0], flags=re.IGNORECASE)
	episode = [list(x) for x in episode]
	if len(episode) > 0:
		episode = episode[0]
		episode = [episode[0].upper(), episode[1].upper()]
	else:
		episode = ['S00', 'E00']

	return episode


# Fix the name info of TV series to be identified
def fix_drama_name(drama_item):
	names = identify_drama_name(drama_item)

	chinese_name = fix_chinese_name(names['chinese'])
	english_name = fix_english_name(names['english'])

	drama_item.insert(0, english_name)
	drama_item[1] = chinese_name

	return drama_item


# fix the chinese name format 
def fix_chinese_name(chinese_name):
	chinese_name = [x for x in chinese_name if x]

	if len(chinese_name) == 0 or (len(chinese_name) == 1 and chinese_name[0] == 'ÖÐÓ¢'):
		chinese_name = ''
	elif (len(chinese_name) == 1 and chinese_name[0] != 'ÖÐÓ¢'):
		chinese_name = chinese_name[0]
	elif (len(chinese_name) == 2):
		chinese_name = chinese_name[1]

	return chinese_name


# fix the english name format 
def fix_english_name(english_name):

	english_name = [x for x in english_name if x]
	if english_name:
		english_name = english_name[0].split('.')
	english_name = " ".join(english_name).lower()
	
	return english_name


# Identify the name of given drama
def identify_drama_name(drama_item):

	full_name = re.findall(r'(.*).NAME_SEPERATOR.', drama_item[0])
	if len(full_name) > 0:
		chinese_name = re.findall(r'(.*?)\.[A-Za-z0-9\-]*', full_name[0], flags=re.IGNORECASE)
		english_name = re.findall(r'\.([A-Za-z0-9\-].*)', full_name[0], flags=re.IGNORECASE)
	else:
		chinese_name = ['Î´Öª']
		english_name = ['Undetermined']
	names = dict(english=english_name, chinese=chinese_name)

	return names



# ================================ Stage 05 ================================= #

# Check if the dramas existed in UPDATED_RESOURCES or DOWNLOADED_RESOURCES
def check_new(drama_items):
	updated_drama_items = recognise_updated_drama_items()
	downloaded_drama_items = recognise_downloaded_drama_items()
	new_drama_items = filter_dramas(drama_items, updated_drama_items, downloaded_drama_items)
	return new_drama_items



def recognise_updated_drama_items():
	updated_drama_items = []
	for line in raw_updated_lines:
		if (raw_updated_lines.index(line) == 0) or not line: continue
		updated_drama_items.append(line.split('\t\t'))
	return updated_drama_items


def recognise_downloaded_drama_items():
	downloaded_file = open(DOWNLOADED_RESOURCES, 'r', encoding="utf-8")
	downloaded_lines = downloaded_file.readlines()
	downloaded_drama_items = []
	for line in downloaded_lines:
		if not line: continue
		downloaded_drama_items.append(line.split('\t\t'))
	return downloaded_drama_items


def filter_dramas(drama_items, updated_drama_items, downloaded_drama_items):
	new_drama_items = filter_from_updated(drama_items, updated_drama_items)
	final_drama_items = filter_from_downloaded(new_drama_items, downloaded_drama_items)
	return final_drama_items

def filter_from_updated(drama_items, updated_drama_items):
	new_drama_items = []
	for drama_item in drama_items:
		exists = False;
		for updated_drama_item in updated_drama_items:
			if (drama_item[0] == updated_drama_item[0]) and (drama_item[1] == updated_drama_item[1]):
				if drama_item[3] in PREFERRED_SHOW_CATEGORIES:
					if (not updated_drama_item[2] and updated_drama_item[3] == drama_item[2][1])\
					 or (updated_drama_item[2] == drama_item[2][0] and updated_drama_item[3] == drama_item[2][1]):
						exists = True
				if (drama_item[3] in PREFERRED_MOVIE_CATEGORIES):
					exists = True

		if(not exists):
			if (type(drama_item[0]) == str) and (type(drama_item[1]) == str):
				new_drama_items.append(drama_item[0] + '\t\t' + drama_item[1] + '\t\t' + drama_item[2][0] + '\t\t' + drama_item[2][1] + '\t\t' + drama_item[5] + '\t\t' +'\n')
	return new_drama_items


def filter_from_downloaded(new_drama_items, downloaded_drama_items):


	new_drama_list = []
	for drama_item in new_drama_items:
		new_drama_list.append(drama_item.split('\t\t'))
	tmp_new_drama_list = copy.copy(new_drama_list)

	for downloaded_drama_item in downloaded_drama_items:
		for new_drama_item in tmp_new_drama_list:
			if not new_drama_item: continue
			if in_same_series(new_drama_item, downloaded_drama_item):
				if not newer(new_drama_item, downloaded_drama_item):
					for item in new_drama_list:
						if item == new_drama_item:
							new_drama_list.remove(new_drama_item)

	final_drama_items = []
	for drama_item in new_drama_list:
		final_drama_items.append(drama_item[0] + '\t\t' + drama_item[1] + '\t\t' + drama_item[2] + '\t\t' + drama_item[3] + '\t\t' + drama_item[4] + '\t\t' +'\n')

	return final_drama_items



def in_same_series(drama_1, drama_2):
	if drama_1[0] and drama_2[0] and drama_1[1] and drama_2[1]:
		return (drama_1[0] == drama_2[0]) or (drama_1[1] == drama_2[1]) or (drama_1[0] == drama_2[1]) or (drama_1[1] == drama_2[0])

	if (not drama_1[1]) or (not drama_2[1]):
		return (drama_1[0] == drama_2[0])

	if (not drama_1[0]) or (not drama_2[0]):
		return (drama_1[1] == drama_2[1])

def newer(drama_1, drama_2):
	if drama_1[2] < drama_2[2]:
		return False
	if (drama_1[2] == drama_2[2]) and (drama_1[3] <= drama_2[3]):
		return False
	return True

# ================================ Stage 06 ================================= #

def write_new_drama_items(raw_updated_lines, new_drama_items):

	
	write_updated_file = open(UPDATED_RESOURCES, 'w', encoding="utf-8")

	raw_updated_lines[0] = TODAY + '\n'

	write_updated_file.writelines(raw_updated_lines)
	write_updated_file.writelines(new_drama_items)
	write_updated_file.close()



# ================================ Stage 07 ================================= #

def send_message(new_drama_items):
	message = ''
	notification = ''
	num = 0

	for item in new_drama_items:
		num += 1
		item = item.split('\t\t')
		item_info = dict(english_name = item[0].replace(' ', '\ '), chinese_name = item[1].replace(' ', '\ '), season = item[2], episode = item[3])
		message += str(num) + '.\ ' + item_info['english_name'] + '\ ' + item_info['chinese_name'] + '\ ' + item_info['season'] + '\ ' + item_info['episode'] + 'NewLine'
		notification += str(num) + '.\ ' + item_info['english_name'] + '\ ' + item_info['chinese_name'] + '\ ' + item_info['season'] + '\ ' + item_info['episode']
		os.system('terminal-notifier' + ' -message ' + notification + ' -title ' + "ZiMuZu")

	if message:
		os.system('Ruby ../TelstraMessenger/send_to_me.rb' + ' ' + message)
		

# ================================== Main =================================== #

if __name__ == '__main__':
	print(datetime.datetime.now())

	# Stage 00
	collect_infos()

	# Stage 01
	user = login()
	# Stage 02
	raw_updated_lines = read_from_updated_file()
	# Stage 03
	# raw_updated_lines = checkIn(user, raw_updated_lines)
	# Stage 04
	drama_items = prepare_new_dramas(user)
	# Stage 05
	new_drama_items = check_new(drama_items)
	# Stage 06
	write_new_drama_items(raw_updated_lines, new_drama_items)
	# Stage 07
	# send_message(new_drama_items)
	print("Updated Successfully")
