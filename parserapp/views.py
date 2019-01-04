from django.shortcuts import render, HttpResponse

from .sqlparsers import extract_columns, extract_tables
from .models import DdmSlTable
from re import search, sub
from django.db import DatabaseError
import sqlparse

ptrn = r'[.]'



def replace_to_original(sql, tPtrn, rPtrn):	

	if search(tPtrn, sql):
		split_tPtrn=tPtrn.split('.')
		tPtrn=split_tPtrn[0]+'[.]'+split_tPtrn[1]
		# print(tPtrn,'----',rPtrn)

		s= sub(tPtrn, rPtrn, sql)
		# print(s)
		return s


def get_original_table_name(sl_id, m_table_name):
	try:
		original_table=DdmSlTable.objects.filter(mapped_table_name=m_table_name, sl=sl_id).values('original_table_name').get()
		return original_table['original_table_name']

	except DdmSlTable.DoesNotExist: 
		return m_table_name
	except :
		return m_table_name

	# return m_table_name


def get_original_col_name(sl,tName, col_name):
	try:
		column_data=DdmSlTable.objects.filter(mapped_table_name=tName, sl=sl).values('original_column_name','mapped_column_name').get()
		mapped_columns=column_data['mapped_column_name']
		col_index=mapped_columns.index(col_name)
		original_columns=column_data['original_column_name']
		ori_column_name=original_columns[col_index]

		return ori_column_name
	
	except DdmSlTable.DoesNotExist as e:
		# print('Boss---',str(e))
		return col_name


def check_schema_name(sl, tablename):

	if search(ptrn, tablename):
		stName=tablename.split('.')
		sName=stName[0]
		tName=stName[1]

		otName=get_original_table_name(sl, tName)
		rPtrn = sName+'.'+otName

		return rPtrn

	else:

		otName=get_original_table_name(sl, tablename)
		# rPtrn = sName+'.'+otName

		return otName


	

def check_col_prefix(sql, sl, columns_list, tablename, table_alias=None):

	for c in columns_list:

		col_name_split=c.split()

		if len(col_name_split)==1:
			if search(ptrn, c):
				alias_col_name = c.split('.')
				alias_name=alias_col_name[0]
				col_name=alias_col_name[1]

				if table_alias != None and alias_name == table_alias:
					# print('alias-->', alias_name)

					if search(ptrn, tablename):
						tName=tablename.split('.')[1]
						ori_col_name=get_original_col_name(sl, tName, col_name)
						col_ptrn = alias_name+'.'+ori_col_name

						# print(c,'-->Column patern-->',col_ptrn)

						sql1=replace_to_original(sql, c, col_ptrn)
						if sql1:
							sql=sql1
			# else:

			# 	col_name=c

			# 	if table_alias != None and alias_name == table_alias:
			# 		# print('alias-->', alias_name)

			# 		if search(ptrn, tablename):
			# 			tName=tablename.split('.')[1]
			# 			ori_col_name=get_original_col_name(sl, tName, col_name)
			# 			col_ptrn = alias_name+'.'+ori_col_name

			# 			# print(c,'-->Column patern-->',col_ptrn)

			# 			sql1=replace_to_original(sql, c, col_ptrn)
			# 			if sql1:
			# 				sql=sql1



		# elif len(col_name_split)==2:
		else:
			cName=col_name_split[0]
			caName = col_name_split[1]


			if search(ptrn, cName):
				alias_col_name = cName.split('.')
				alias_name=alias_col_name[0]
				col_name=alias_col_name[1]

				if table_alias != None and alias_name == table_alias:
					# print('alias-->', alias_name)

					if search(ptrn, tablename):
						tName=tablename.split('.')[1]
						ori_col_name=get_original_col_name(sl, tName, col_name)
						col_ptrn = alias_name+'.'+ori_col_name

						# print(c,'-->Column patern-->',col_ptrn)

						sql1=replace_to_original(sql, cName, col_ptrn)
						if sql1:
							sql=sql1


		# elif table_alias == None and not search(ptrn, c):

		# 		# if search(ptrn, tablename):
		# 		# tName=tablename.split('.')[1]

		# 	print('theBoss--1--',c)
		# 	if search(ptrn, tablename):
		# 		tName=tablename.split('.')[1]
		# 		ori_col_name=get_original_col_name(sl, tName, c)
		# 		print('boss--2--',ori_col_name)
		# 			# col_ptrn = alias_name+'.'+ori_col_name

		# 		sql1=replace_to_original(sql, c, ori_col_name)
		# 		if sql1:
		# 			sql=sql1 



	return sql

def convert_queries(sql, sl):


	tables_list=extract_tables(sql)
	columns_list=extract_columns(sql)

	print(tables_list)
	print(columns_list)


	for t in tables_list:

		table_name_split = t.split()
		# print('xxxx   ',table_name_split)

		if len(table_name_split)==3: #SCHEMA.TABLE AS TAB
			tablename= table_name_split[0]
			table_alias=table_name_split[2]

			rPtrn=check_schema_name(sl,tablename)			 
			sql1=replace_to_original(sql, tablename, rPtrn)
			if sql1:
				sql=sql1

			sql=check_col_prefix(sql, sl,columns_list, tablename, table_alias)

			# print(sql)

						

		elif len(table_name_split)==2:
			tablename= table_name_split[0]
			table_alias=table_name_split[1]

			rPtrn=check_schema_name(sl,tablename)
			sql1=replace_to_original(sql, tablename, rPtrn)

			if sql1:
				sql=sql1

			sql=check_col_prefix(sql, sl, columns_list, tablename, table_alias)
			# print('The Boss')
			# print(sql)

		else:
			tablename= table_name_split[0]

			rPtrn=check_schema_name(sl,tablename)
			sql1=replace_to_original(sql, tablename, rPtrn)

			if sql1:
				sql=sql1

			sql=check_col_prefix(sql, sl, columns_list, tablename)
			# print('The Boss')
			# print(sql)


	# template = str(tables_list) +'	--->	'+str(columns_list) 

	return sql


def apicall(request):

	sql1='''
	select cust.id ,cust.name ,cust.address ,cust.phone , acc.ACC_CATEGORIES 
	from schema.customer as cust, schema.account as acc where upper(acc.id) in 
	(select c.name from schema.customer c where upper(c.name)='ram')
	'''.upper()

	sql="""

	select rowcount, m.id
	from (select cust.id id
	from schema.customer as cust) as M
	""".upper()

	sl='1'
	temp = sqlparse.format(convert_queries(sql,sl),reindent=True)
	print(temp)

	return HttpResponse(temp)