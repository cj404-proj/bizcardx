# Libraries
import re
import easyocr
import pymysql
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import streamlit as st

# Create an object for the reader
reader = easyocr.Reader(lang_list=['en'])

# Functions
## Function to split the image
def split_image(image):
    width,height = image.size
    half_width = (width-100)//2
    img1 = image.crop((0,0,half_width,height))
    img2 = image.crop((half_width,0,width,height))
    return np.array(img1), np.array(img2)

## Function to extract data from image
def extract_text_from_image(image):
    return reader.readtext(image,detail=0)

## Function to get person's details from extracted text
def get_person_details(results):
    mobile_number_pattern = r'\+*\d+-\d+-\d+'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    data = {}
    for index, value in enumerate(results):
        if index == 0:
            data['name'] = value
        elif index == 1:
            data['designation'] = value
        elif re.match(mobile_number_pattern,value) is not None:
            data['mobile'] = value
        elif re.match(email_pattern,value) is not None:
            data['email'] = value
        elif value.lower().startswith('www') and len(value)>3:
            data['url'] = value.lower()
        elif value.lower() == 'www':
            data['url'] = (results[index] + "." + results[index+1]).lower()
        
        if re.findall('^[0-9].+, [a-zA-Z]+',value):
            data["area"] = value.split(',')[0]
        elif re.findall('[0-9] [a-zA-Z]+',value):
            data["area"] = value
        
        # To get CITY NAME
        match1 = re.findall('.+St , ([a-zA-Z]+).+', value)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', value)
        match3 = re.findall('^[E].*',value)
        if match1:
            data["city"] = match1[0]
        elif match2:
            data["city"] = match2[0]
        elif match3:
            data["city"] = match3[0]
        
        # To get STATE
        state_match1 = re.findall('[a-zA-Z]{9} +[0-9]',value)
        state_match2 = re.findall('[a-zA-Z]{9};',value)
        if state_match1:
            data["state"] = value[:9]
            # data["state"] = state_match1
        elif state_match2:
            data["state"] = value[-10:-1]
            # data["state"] = state_match2

        # To get PINCODE        
        if len(value)>=6 and value.isdigit():
            data["pin_code"] = value
        elif re.findall('[a-zA-Z]{9} +[0-9]',value):
            data["pin_code"] = value[10:]

    return data

## Function to get company name
def get_company_name(results):
    if len(results) > 1:
        return results[0] + " " + results[1]
    return results[0]

## Function to combine person's details and company name
def process(image):
    image = Image.open(image)
    img1, img2 = split_image(image)
    img1_data, img2_data = map(extract_text_from_image,[img1,img2])
    if len(img1_data) <= 2:
        data = get_person_details(img2_data)
        data['company'] = get_company_name(img1_data)
    else:
        data = get_person_details(img1_data)
        data['company'] = get_company_name(img2_data)
    return data

# Function to connect to SQL
def connect_to_sql():
    conn = pymysql.connect(host='localhost',user='root',password='root',db='guvi_projects_prac')
    cursor = conn.cursor()
    return conn, cursor
# Function to store data in SQL
def store_in_sql(data):
    conn, cursor = connect_to_sql()
    sql = "INSERT INTO biz VALUES (%s,%s,%s,%s,%s,%s)"
    # vals = (
    #     data['name'],
    #     data['designation'],
    #     data['mobile'],
    #     data['email'],
    #     data['url'],
    #     data['company']
    # )
    vals = (
        data[0],data[1],data[2],data[3],data[4],data[5],

    )
    cursor.execute(sql,vals)
    conn.commit()
    conn.close()

# Function to fetch data from SQL
def fetch_data_from_sql():
    conn, cursor = connect_to_sql()
    sql = "SELECT * FROM biz;"
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

# Function to delete data from SQL
def delete_data_from_sql(name):
    conn, cursor = connect_to_sql()
    sql = "DELETE FROM biz WHERE name = %s"
    vals = name
    cursor.execute(sql,vals)
    conn.commit()
    conn.close()

# FUnction to get the names from SQL
def fetch_names_from_sql():
    conn, cursor = connect_to_sql()
    sql = "SELECT name FROM biz;"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    return cursor.fetchall()

# Function to convert image to binary
def img_to_binary(image):
    img = Image.open(image)
    binary_img = BytesIO()
    img.save(binary_img,format="JPEG")
    binary_img = binary_img.getvalue()
    return binary_img