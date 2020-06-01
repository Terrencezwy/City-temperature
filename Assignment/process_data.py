import csv
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def listdir(path, list_name):
	for file in os.listdir(path):
		file_path = os.path.join(path, file)
		if(os.path.splitext(file_path)[1] == '.csv'):
			list_name.append(file_path)

# test part for listdir:


# filePath = './dataset/'
# list_name=[]
# listdir(filePath,list_name)
# print(list_name)


def getData(file, cityName, city_data):
	csvFile = open(file, "r")
	reader = csv.reader(csvFile)
	result = {}
	for item in reader:
		if reader.line_num == 1:
			city = item[1]
			cityName.append(item[1])
			result[item[0]] = item[1]
		else:
			result[item[0]] = item[1]

	city_data[city] = result
	csvFile.close()

#  test part for getData:

# cityName = []
# city_data = {}
# # getData(list_name[0])
# for file in list_name:
# 	getData(file)
# print(cityName)

# print("city_data: ------------")
# print(city_data)

def getCityName(filePath):
	list_name=[]
	listdir(filePath,list_name)
	cityName = []
	city_data = {}
	for file in list_name:
		getData(file, cityName, city_data)

	return cityName, city_data

# filePath = './dataset/'
# cityName = getCityName(filePath)
# print(city_alpha)


