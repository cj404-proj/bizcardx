import streamlit as st
import time
import pandas as pd
from streamlit_option_menu import option_menu

import bizfuncs

# Streamlit code

## Page setup
st.set_page_config(
    page_title="BizCardX",
    layout="wide"
)

## Functions
def processing_section(image):
    st.header("Processing")
    st.write(bizfuncs.process(image))

def storing_section(image):
    st.header("Storing")
    st.image(image,use_column_width=True)
    data = bizfuncs.process(image)
    with st.form("biz-form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(label="Name",value=data['name'])
            designation = st.text_input(label="Designation",value=data['designation'])
            mobile = st.text_input(label="Mobile",value=data['mobile'])
            email = st.text_input(label="Email",value=data['email'])
            url = st.text_input(label="URL",value=data['url'])
        with col2:
            company = st.text_input(label="Company",value=data['company'])
            area = st.text_input(label="Area",value=data['area'])
            city = st.text_input(label="City",value=data['city'])
            state = st.text_input(label="State",value=data.get("state"))
            pincode = st.text_input(label="Pin",value=data['pin_code'])
        submit = st.form_submit_button(label="Store",use_container_width=True)
        if submit:
            with st.spinner("Pushing data to the SQL."):
                time.sleep(5)
                new_data = [name,designation,mobile,email,url,company,area,city,state,pincode,bizfuncs.img_to_binary(st.session_state['image_holder'])]
                bizfuncs.store_in_sql(new_data)
            st.success("Data pushing is done successfully.")

## Main
st.title("BizCardX")

selected = option_menu("",["Introduction","Extract","Add","View","Delete"],orientation="horizontal",icons=["info","card-image","database-add","database","database-dash"],)

if selected == "Extract":
    image_holder = st.file_uploader(label="Upload the file",accept_multiple_files=False,type=['png','jpeg','jpg'])
    extract_btn = st.button(label="Extract",use_container_width=True)

    if image_holder and extract_btn:
        st.session_state['image_holder'] = image_holder
        st.image(image_holder,use_column_width=True)
        processing_section(image_holder)
    else:
        st.warning("Input the image and then click the extract button")
elif selected == "Add":
    st.header("Storing the data to the DB.")
    if 'image_holder' not in st.session_state:
        st.write("Please insert the image and process it in the `Extract` tab")
    else:
        storing_section(st.session_state['image_holder'])

elif selected == "View":
    st.header("View the data in the DB.")
    df = pd.DataFrame(bizfuncs.fetch_data_from_sql(),columns=[
        "Company","Name","Designation","Mobile","Mail","URL","Area","City","State","Pin","Image"
    ]).drop("Image",axis=1)
    st.dataframe(df,use_container_width=True)

elif selected == "Delete":
    to_be_deleted_name = st.selectbox(label="Select the name",options=[i[0] for i in bizfuncs.fetch_names_from_sql()])
    delete_btn = st.button(label="Delete",use_container_width=True)

    if delete_btn:
        with st.spinner(f"Deleting data related to {to_be_deleted_name}"):
            time.sleep(5)
            bizfuncs.delete_data_from_sql(to_be_deleted_name)
        st.success(f"Data related to {to_be_deleted_name} is deleted successfully.")
    else:
        st.warning("Please delete only when you are sure.")
