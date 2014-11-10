#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
from timeit import Timer
import time,datetime
#,timelimit
import TimeDeal as TD
import pandas as pd
import csv
import profile
import os

def fuzzy_matching(word,key):
	'''对字符进行模糊匹配，返回结果类型为“_sre.SRE_MATCH”或“NoneType”。（可以用if进行判断）
	'''
	import re
	Is_match = re.search(key,word)
	return Is_match

def create_channel2iddict(channel2iddata_path):
	'''读取频道名称对应频道id的文件并生成频道名称到频道id的字典
	'''
	channel2iddict = {}
	with open(channel2iddata_path,'rb') as channel2iddata:
		reader = csv.reader(channel2iddata)
		i = 0
		for row in reader:
			i +=1
			if i<2:
				continue
			channel2iddict[row[1].decode('gbk')] = row[2]
	return channel2iddict

def read_channeldatas(channeldata_path,branddata_path,channel2iddata_path):
	'''读取频道文件的数据并对数据做筛选和修改，返回以频道id为索引的字典
	'''
	channeldata_dict = {}
	temp_dict = {}
	channel2iddict = create_channel2iddict(channel2iddata_path)
	with open(channeldata_path,'rb') as TVdata:
		reader = csv.reader(TVdata)
		i = 0
		channelid = ""
		line_num = 0
		for row in reader:
			i = i+1
			if i<4:
				continue
			erow = []
			add_this_row = False
			ad_classify1 = row[7].decode('gbk')
			if temp_dict.has_key(ad_classify1) and temp_dict[ad_classify1]!=None:
				add_this_row = True
			else:
				with open(branddata_path,'rb') as branddata:
					brdata = csv.reader(branddata)
					for brrow in brdata:
						if fuzzy_matching(row[7],brrow[1]):
							add_this_row = True
							temp_dict[ad_classify1] = row[0]
							break
						else:
							if not temp_dict.has_key(ad_classify1):
								temp_dict[ad_classify1] = None
			if row[0]!="":
				line_num = 0
				channelid = int(channel2iddict[row[0].decode('gbk')])
				channeldata_dict[channelid] = pd.DataFrame(index = range(0,1),columns = ["adstarttime","adendtime","addelta","classify"])
				if add_this_row:
					erow.append(row[2])
					erow.append(row[3])
					erow.append(row[4])
					erow.append(row[7].decode('gbk'))
					channeldata_dict[channelid].ix[line_num] = erow
			else:
				if add_this_row:
					erow.append(row[2])
					erow.append(row[3])
					erow.append(row[4])
					erow.append(row[7].decode('gbk'))
					channeldata_dict[channelid].ix[line_num] = erow
					line_num+=1
	return channeldata_dict


def find_value_userdatas(value_userdata_path):
	'''读取需要分析的用户文件并输出userids
	'''
	value_userdatas = set()
	with open(value_userdata_path,"rb") as value_userdata:
		reader = csv.reader(value_userdata)
		for value in reader:
			value_userdatas.add(int(value[1]))
	return value_userdatas

def read_userdatas(userdata_path):
	'''读取用户观看电视记录并做筛选、排序，输出用户观看记录数据
	'''
	temp_L = []
	initial_userdata = pd.DataFrame(columns = ["userid","channelid","datetime"])
	full_userdata = pd.read_csv(userdata_path,header=-1,names=range(1,7))
	initial_userdata["userid"] = full_userdata[1]
	initial_userdata["channelid"] = full_userdata[2]
	initial_userdata["datetime"] = pd.to_datetime(full_userdata[3]+" "+full_userdata[4])
	userdata = initial_userdata.sort_index(by=["userid","datetime"],ascending=[1, 0])
	return userdata

def cut(stime,etime):
	'''按照间隔时间限制对时间进行分割操作（需要用到timelimit.py文件）
	'''
	stime_delta = []
	limit = TD.timelimit 	#首先将输入时间的日期与时间分开，并得到开始时间是星期几
	s_time = TD.get_time(stime)
	weekday = TD.get_weekday(stime) 	#trunctime为timelimit.py中函数，得到开始时间属于一天中的哪个时间段
	week_id,s_time,delta = TD.trunctime(s_time,TD.str2seconds(etime)-TD.str2seconds(stime))
	w_limit = limit[week_id]['weekendlimit']		#初始化w_limit为周末
	#如果不是周末（星期六或星期日），limit取worklimit
	if weekday!="0" and weekday!="6":
		w_limit = limit[week_id]['worklimit']
	#开始分析每个时间段，并对不同时间段做不同处理
	stime_delta.append(TD.str2seconds(stime))
	stime_delta.append(delta)
	return stime_delta



def valueable_ad(user_ad,duration,temp_channel,channeldata_dict):
	'''根据广告时间和用户收视情况统计用户观看广告情况
	'''
	channel_full_id = duration[1]
	try:
		channel_id = int(channel_full_id)%1000	#channelid取channelfullid的最后三位
	except:
		channel_id = channel_full_id
	Is_channel = False
	if temp_channel.has_key(channel_full_id) and temp_channel[channel_full_id]:
		Is_channel = True
	else:
		if channeldata_dict.has_key(channel_id):
			temp_channel[channel_full_id] = True
			Is_channel = True
		if not temp_channel.has_key(channel_full_id):
			temp_channel[channel_full_id] = False
	if Is_channel:
		s_datetime = duration[2]
		s_date = TD.get_date(str(s_datetime))
		e_datetime = s_datetime+duration[3]
		e_date = TD.get_date(str(e_datetime))
		this_channeldata = channeldata_dict[channel_id] 	#类型为DataFrame
		for index,adstarttime in this_channeldata["adstarttime"].iteritems():
			ad_deltatime = TD.str2timedelta(str(this_channeldata["addelta"][index]))
			ads_datetime = datetime.datetime.combine(s_date,TD.str2time(str(adstarttime)))
			ade_datetime = ads_datetime+ad_deltatime
			#判断是否符合条件
			add_this_ad = False
			if s_datetime<=ads_datetime:
				if e_datetime>=ads_datetime:
					add_this_ad = True
			if add_this_ad:
				if duration[0] in user_ad.keys():
					if this_channeldata["classify"][index] in user_ad[duration[0]].keys():
						user_ad[duration[0]][this_channeldata["classify"][index]]+=1
					else:
						user_ad[duration[0]][this_channeldata["classify"][index]]=1
				else:
					user_ad[duration[0]]={this_channeldata["classify"][index]:1}

def record_number_of_ads(user_ad,userdatas,channeldata_dict,value_userdatas):
	'''将用户观看频道时间与频道广告时间做比较，将符合标准的广告记录入user_ad字典中
	'''
	temp_channel = {}
	different_usernum=0
	userad_call=0
	temp_userid = None
	end_time = "2200-01-01 00:00:00"
	temp_endtime = "2200-01-01 00:00:00"
	for index,userid in userdatas["userid"].iteritems():
		if userid in value_userdatas:
			userad_call+=1
			channelid = userdatas["channelid"][index]
			time_here = str(userdatas["datetime"][index])
			if temp_userid!=userid:
				different_usernum+=1
				temp_userid = userid
				temp_duration = cut(time_here,end_time)
				duration = [userid,channelid]+temp_duration
				valueable_ad(user_ad,duration,temp_channel,channeldata_dict)
			else:
				temp_duration = cut(time_here,temp_endtime)
				duration = [userid,channelid]+temp_duration
				valueable_ad(user_ad,duration,temp_channel,channeldata_dict)
			temp_endtime = time_here

	print "debug: different_usernum=", different_usernum
	print "debug: userad_call=", userad_call
	return user_ad


def create_userad_table(user_ad,channeldata_dict):
	'''生成userad_table.csv文件
	'''
	classify = []
	if user_ad=={}:
		print "Someting Wrong!!!"
	ad_classify = set()
	for channel in channeldata_dict:
		ad_classify.update(set(channeldata_dict[channel]["classify"]))
	for i in ad_classify:
		classify.append(i.encode("gbk"))
	with open("userad_table.csv","wb") as finaldatas:
		spamwriter = csv.writer(finaldatas)
		row_1 = list(classify)
		row_1.insert(0,"user_id")
		spamwriter.writerow(row_1)
		user_id = user_ad.keys()
		for j in user_id:
			row = []
			row.append(j)
			for cl in classify:
				if cl.decode("gbk") in user_ad[j].keys():
					row.append(user_ad[j][cl.decode("gbk")])
				else:
					row.append(None)
			spamwriter.writerow(row)


def deal_file(channeldata_path,userdata_path,branddata_path,channel2iddata_path,value_userdata_path):
	'''处理单个userdata文件
	'''
	user_ad = {}
	print "Read_channeldatas started at time:",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	channeldata_dict = read_channeldatas(channeldata_path,branddata_path,channel2iddata_path)
	print "Find_value_userdatas started at time:",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	value_userdatas = find_value_userdatas(value_userdata_path)
	print "Read_userdatas started at time:",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	userdatas = read_userdatas(userdata_path)
	print "Record_number_of_ads started at time:",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	user_ad = record_number_of_ads(user_ad,userdatas,channeldata_dict,value_userdatas)
	print "create_userad_table started at time:",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	create_userad_table(user_ad,channeldata_dict)

if __name__=='__main__':
	import sys
	#add filename argv support
	if len(sys.argv) < 2:
		sys.exit('Usage: python %s <tvdatafile-name.csv>' % sys.argv[0])
	if not os.path.exists(sys.argv[1]):
		sys.exit('ERROR: Tvdatafile %s was not found!' % sys.argv[1])

	stime = datetime.datetime.now()
	print "Code started at time:",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	datapath = os.path.join(os.getcwd(),'tvdatas')
	channeldata_path = os.path.join(datapath,'TVdata.csv')
	channel2iddata_path = os.path.join(datapath,'channelids.csv')
	
	#add filename argv support
	userdata_path = sys.argv[1]

	branddata_path = os.path.join(datapath,'brand.csv')
	value_userdata_path = os.path.join(datapath,'ca2stb.csv')
	#开始分析文件
	deal_file(channeldata_path,userdata_path,branddata_path,channel2iddata_path,value_userdata_path)

	print "Code ended at time:",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	etime = datetime.datetime.now()
	print "Code dealing time is:",(etime-stime).seconds,"s"