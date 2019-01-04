import itertools
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
from sqlparse.keywords import KEYWORDS
from sqlparse import tokens as T
from re import search

# Function for sub query
def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value == 'SELECT':
            return True
    return False

# Remove functins and subquery from list
def remove_unwanted_field(columns_list):

    columns=[]

    ptrn1 = r"[\(|\']"

    for col in columns_list:
	    if not search(ptrn1, col):
		    columns.append(col)

    return columns

# Break all identifiers for column
def check_token_item(item):
    if item.value not in ['DECODE','SIGN','NVL'] and item.value not in KEYWORDS:
        
        return True
    
    return False

#Breck all the parts for column
def extract_all_part(parsed):
    
    extracted_tokens =[]    
    for item in parsed.tokens:
       
        if item.is_group:            
            for x in extract_all_part(item):                
                if check_token_item(x):                
                    extracted_tokens.append(x)
        if is_subselect(item):
            for x in extract_all_part(item):
                if check_token_item(item) :
                    extracted_tokens.append(x)
        else:
            if check_token_item(item) :     
                extracted_tokens.append(item)       

    return extracted_tokens

# Break all Attribute for table
def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        
        if item.is_group:
            for x in extract_from_part(item):
                yield x
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif item.ttype is Keyword and item.value in ['ORDER', 'GROUP', 'BY', 'HAVING', 'UNION', 'ALL', 'UNION ALL', 'INTERSECT', 'MINUS']:
                from_seen = False
                StopIteration
            else:
                yield item
        if item.ttype is Keyword and item.value == 'FROM':
            from_seen = True

# Extract the column and table token
def extract_column_identifiers(token_stream):
    extracted_identifiers = []
    alias_list=[]
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():                
                value = identifier.value.replace('"', '')
                extracted_identifiers.append(value)
        elif isinstance(item, Identifier):
            alias_list.append(item.get_alias())
            value = item.value.replace('"', '')
            extracted_identifiers.append(value)

    extracted_identifier =[ v for v in extracted_identifiers if v not in set(alias_list) ]
    return extracted_identifier


# Extract the table token
def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                value = identifier.value.replace('"', '')
                yield value
        elif isinstance(item, Identifier):
            value = item.value.replace('"', '')
            yield value

# Extract the columns
def extract_columns(sql):
    sql=sql.upper()
    
    statements = list(sqlparse.parse(sql))
    for statement in statements:

        if statement.get_type() != 'UNKNOWN':
            stream = extract_all_part(statement)                    
            extracted_column = list(set(extract_column_identifiers(stream)))
    
    removed_tables = [ v for v in extracted_column if v not in extract_tables(sql) ]
    columns= remove_unwanted_field(removed_tables)

    return columns

#Extract the Tables
def extract_tables(sql):
    sql=sql.upper()
    
    extracted_tables = []
    statements = list(sqlparse.parse(sql))
    for statement in statements:

        if statement.get_type() != 'UNKNOWN':
            stream = extract_from_part(statement)
            extracted_tables.append(set(list(extract_table_identifiers(stream))))
    
    sub_table_list= list(itertools.chain(*extracted_tables))
    tables_list = remove_unwanted_field(sub_table_list) 

    return tables_list