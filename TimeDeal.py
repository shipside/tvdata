#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time,datetime

def channeldata_timestr2int(datestr,timestr):
	'''将时间字符串转换成int类型整数（提高时间比较的运行效率）
	'''
	one_day = 86400 	#一天的秒数
	form = "%d/%m/%Y %H:%M:%S" 	#channel日期数据格式
	s=timestr.split(':')
	if int(s[0])>=24: 	#时间大于24则是第二天的凌晨了
		s[0] = str(int(s[0])-24)
		new_timestr = ':'.join(s)
		datetimestr = datestr+" "+new_timestr
		timeArray = time.strptime(datetimestr,form)
		timeStamp = int(time.mktime(timeArray))+one_day
	else:
		datetimestr = datestr+" "+timestr
		timeArray = time.strptime(datetimestr,form)
		timeStamp = int(time.mktime(timeArray))
	return timeStamp

def userdata_timestr2int(datetimestr):
	'''将时间字符串转换成int类型整数（提高时间比较的运行效率）
	'''
	form = "%Y-%m-%d %H:%M:%S" 	#用户数据中的日期数据格式
	timeArray = time.strptime(datetimestr,form)
	timeStamp = int(time.mktime(timeArray))
	return timeStamp

def get_weekday(timeStamp):
	'''根据时间戳得到当时是星期几，返回int类型
	'''
	timeArray = datetime.datetime.utcfromtimestamp(timeStamp)
	week = int(timeArray.strftime("%w"))
	return week

def str2timedelta(str):
	'''将时间字符串转换为datetime.timedelta类型（两个datetime.datetime相减得到的类型，可加减）
	'''
	s=str.split(':')
	if int(s[0])>24:
		s[0] = int(s[0])-24
	if len(s)==2:
		return datetime.timedelta(minutes=int(s[0]),seconds=int(s[1]))
	elif len(s)==3:
		return datetime.timedelta(hours=int(s[0]), minutes=int(s[1]),seconds=int(s[2]))
	else:
		return None