#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time,datetime

timelimit = []

#将时间字符串转换成能够进行运算的时间（类型为datetime.datetime）
def str2seconds(str):
	form1 = "%Y/%m/%d %H:%M:%S"
	form2 = "%Y-%m-%d %H:%M:%S"
	try:
		seconds_str = datetime.datetime.strptime(str,form1)
	except:
		seconds_str = datetime.datetime.strptime(str,form2)
	return seconds_str

#根据时间字符串得到当时是星期几（类型为int）
def get_weekday(str):
	form1 = "%Y/%m/%d %H:%M:%S"
	form2 = "%Y-%m-%d %H:%M:%S"
	try:
		t = time.strptime(str,form1)
	except:
		t = time.strptime(str,form2)
	week = datetime.datetime(t[0],t[1],t[2]).strftime("%w")
	return week

#根据日期时间字符串得到时间（类型为datetime.time）
def get_time(str):
	form1 = "%Y/%m/%d %H:%M:%S"
	form2 = "%Y-%m-%d %H:%M:%S"
	try:
		t = time.strptime(str,form1)
	except:
		t = time.strptime(str,form2)
	str_time = datetime.time(t[3],t[4],t[5])
	return str_time

#根据日期时间字符串得到日期（类型为datetime.date）
def get_date(str):
	form1 = "%Y/%m/%d %H:%M:%S"
	form2 = "%Y-%m-%d %H:%M:%S"
	try:
		t = time.strptime(str,form1)
	except:
		t = time.strptime(str,form2)
	str_date = datetime.date(t[0],t[1],t[2])
	return str_date

#将时间字符串转换为datetime.time类型（此类型不可加减，只能进行大小比较）
def str2time(str):
	s=str.split(':')
	if int(s[0])>=24:
		s[0] = int(s[0])-24
	if len(s)==2:
		return datetime.time(int(s[0]),int(s[1]))
	elif len(s)==3:
		return datetime.time(int(s[0]),int(s[1]),int(s[2]))
	else:
		return None

#将时间字符串转换为datetime.timedelta类型（两个datetime.datetime相减得到的类型，可加减）
def str2timedelta(str):
	s=str.split(':')
	if int(s[0])>24:
		s[0] = int(s[0])-24
	if len(s)==2:
		return datetime.timedelta(minutes=int(s[0]),seconds=int(s[1]))
	elif len(s)==3:
		return datetime.timedelta(hours=int(s[0]), minutes=int(s[1]),seconds=int(s[2]))
	else:
		return None

def trunctime(t1, delta):
	if len(timelimit)==0: init_timelimit()
	t1id=len(timelimit)-1
	for slot in timelimit:
		if t1 >= slot['start'] and t1 < slot['end']: t1id=slot['id']
	if delta > timelimit[t1id]['weekendlimit']:
		delta=timelimit[t1id]['weekendlimit']
	return t1id, t1, delta

def init_timelimit():
	import csv
	with open('timelimit.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		id=0
		for row in reader:
			slot={}
			slot['id']=id
			slot['start']=str2time(row[1])
			slot['end']=str2time(row[2])
			slot['worklimit']=str2timedelta(row[3])
			slot['weekendlimit']=str2timedelta(row[4])
			timelimit.append(slot)
			id+=1
	return True

def __main__():
	init_timelimit()
	print timelimit