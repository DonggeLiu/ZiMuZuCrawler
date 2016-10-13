#coding=GBK

import sys
import os
import time
import copy


CURRENT_DIRECTORY = './'
UPDATED_RESOURCES = CURRENT_DIRECTORY+'updatedResources.txt'
DOWNLOADED_RESOURCES = CURRENT_DIRECTORY+'downloadedResources.txt'
XUNLEI_DIR = '/Applications/Thunder.app'


# ================================================ Stage 01 ================================================ #

def collect_drama_dict():

	raw_updated_dramas = collect_dramas(UPDATED_RESOURCES)
	raw_downloaded_dramas = collect_dramas(DOWNLOADED_RESOURCES)

	raw_drama_dict = dict(updated = raw_updated_dramas, downloaded = raw_downloaded_dramas)
	return raw_drama_dict


def collect_dramas(resource):

	file_reader = open(resource, 'r', encoding="utf-8")
	raw_dramas = file_reader.readlines()
	file_reader.close()

	return raw_dramas


# ================================================ Stage 02 ================================================ #

def parse_drama_dict(raw_drama_dict):

	updated_dramas = parse_dramas(raw_drama_dict['updated'])
	downloaded_dramas = parse_dramas(raw_drama_dict['downloaded'])

	drama_dict = dict(updated = updated_dramas, downloaded = downloaded_dramas)
	return drama_dict

def parse_dramas(raw_dramas):
	
	dramas = []
	for raw_drama in raw_dramas:
		dramas.append(raw_drama.split('\t\t'))

	return dramas




# ================================================ Stage 03 ================================================ #

def download_all(drama_dict):

	tmp_updated_drama = copy.copy(drama_dict['updated'])
	tmp_downloaded_drama = copy.copy(drama_dict['downloaded'])
	
	#for drama in tmp_updated_drama:
	#	if len(drama) == 1: continue
	#	print(drama[0] + ' ' + drama[1] + ' ' + drama[2] + drama[3] + '\n')

	for updated_drama in tmp_updated_drama:
		# skip the first line (date line takes only one cell)
		if len(updated_drama) == 1: continue

		# check if the drama updated is newer
		is_new = True
		for downloaded_drama in tmp_downloaded_drama:
			if in_same_series(updated_drama, downloaded_drama):
				if not newer(updated_drama, downloaded_drama):
					is_new = False
					# drama_dict['downloaded'].append(updated_drama)
		if is_new:
			download_drama(updated_drama)
			drama_dict['downloaded'].append(updated_drama)
			drama_dict['updated'].remove(updated_drama)

	return drama_dict


def in_same_series(drama_1, drama_2):
	return (drama_1[0] == drama_2[0]) or (drama_1[1] == drama_2[1])

def newer(drama_1, drama_2):

	if drama_1[2] > drama_2[2]:
		return True
	if drama_1[3] > drama_2[3]:
		return True
	return False


def download_drama(drama):
	print(drama[0] + ' ' + drama[1] + ' ' + drama[2] + drama[3])
	os.system('open ' + XUNLEI_DIR + ' "' + drama[4] + '"')
	time.sleep(5)




# ================================================ Stage 04 ================================================ #

def renovate_drama_dict(new_drama_dict):
	new_drama_dict['updated'] = renovate_updated_drama(new_drama_dict['updated'])
	new_drama_dict['downloaded'] = renovate_downloaded_drama(new_drama_dict['downloaded'])

	return new_drama_dict


def renovate_updated_drama(dramas):
	return dramas

def renovate_downloaded_drama(dramas):

	for drama_1 in dramas:
		if not drama_1: continue
		for drama_2 in dramas:
			if not drama_2: continue
			if in_same_series(drama_1, drama_2) and newer(drama_1, drama_2):
				dramas.remove(drama_2)

	for drama_1 in reversed(dramas):
		if not drama_1: continue
		for drama_2 in reversed(dramas):
			if not drama_2: continue
			if in_same_series(drama_1, drama_2) and newer(drama_1, drama_2):
				dramas.remove(drama_2)
	return dramas




# ================================================ Stage 05 ================================================ #

def write_drama_dict(dramas):
	write_dramas(dramas['updated'], UPDATED_RESOURCES)
	write_dramas(dramas['downloaded'], DOWNLOADED_RESOURCES)


def write_dramas(dramas, resource):
	# print(dramas)
	file_writer = open(resource, 'w', encoding="utf-8")
	if resource == UPDATED_RESOURCES:
		file_writer.writelines(format_updated_drama(dramas))
	if resource == DOWNLOADED_RESOURCES:
		file_writer.writelines(output_downloaded_drama(dramas))

	file_writer.close()

def output_updated_drama(dramas):
	output = []
	for drama in dramas:
		output.append(drama[0])

	return output


def format_updated_drama(drama):
	return drama[0]


def output_downloaded_drama(dramas):
	output = []
	for drama in dramas:
		output.append(format_downloaded_drama(drama))
	return output

def format_downloaded_drama(drama):
	if len(drama) == 1:
		return ''
	return drama[0] + '\t\t' + drama[1] + '\t\t' + drama[2] + '\t\t' + drama[3] + '\t\t' + '\n'



# ================================================ Main ================================================ #

if __name__ == '__main__':
	
	# Stage 01
	raw_drama_dict = collect_drama_dict()

	# Stage 02
	drama_dict = parse_drama_dict(raw_drama_dict)

	# Stage 03
	new_drama_dict = download_all(drama_dict)

	# Stage 04
	new_drama_dict = renovate_drama_dict(new_drama_dict)

	# Stage 05
	write_drama_dict(new_drama_dict)

	# End Stage
	print("Downloaded Successfully")




















