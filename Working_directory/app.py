import pymysql
import streamlit as st

from tools import get_mysql, park_desc_query, segments_desc

st.title("National Parks Database Explorer Dashboard")
st.set_page_config(page_title="National Parks Database Explorer", layout="wide")


st.sidebar.title("Query Options")
st.sidebar.subheader("Select a Query")
st.sidebar.menu_button("Query Options", options=["Parks Table", "Segment Shares Table", "Spending Profiles Table", 
                                                 "Trip Characteristics Table", "Visitor Use Stat Table", ""]
                        , key="query_option")

st.sidebar.subheader("Filter Options")
if 'ParkNames' not in st.session_state:
    parks = park_desc_query()
    parknames = []
    for park in parks:
        parknames.append(f"{park['park_code']}:{park['park_name']}")
    st.session_state.ParkNames = parknames
st.sidebar.multiselect("Select Park(s)", options=st.session_state.ParkNames, key="park_code_filter")

#List of queries that can be filtered by month
month_filer_queries = []

#List of queries that can be filtered by segment
segment_filter_queries = []

if st.session_state.query_option in month_filer_queries:
    st.sidebar.selectbox("Select Month", options=[1,2,3,4,5,6,7,8,9,10,11,12], key="month_filter")

if st.session_state.query_option in segment_filter_queries:
    st.sidebar.segmented_control("Select Segment(s)", options= list(segments_desc().keys()), key="segment_filter")

#with st.sidebar:
#    querybutton_clicked = st.button("Run Selected Query", key = "querybutton")
#    if querybutton_clicked: