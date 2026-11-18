import pymysql
import streamlit as st

from tools import get_mysql

st.title("National Parks Database Explorer")
st.set_page_config(page_title="National Parks Database Explorer", layout="wide")

