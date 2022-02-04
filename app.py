from pandas.core.tools.datetimes import to_datetime
import streamlit as st
import requests
import json
import datetime
import pandas as pd

selected = st.sidebar.selectbox(
    "Choose your page",["users","rooms","bookings","booking_delete"]
)

if selected == "users":
    st.title("ユーザー登録画面")
    with st.form("user"):
        user_name:str = st.text_input('ユーザーネーム', max_chars=20)
        data = {
            "user_name" : user_name
        }
        
        submitted = st.form_submit_button(label="登録")
        
        if submitted:
            st.write("レスポンス結果")
            url = "http://127.0.0.1:8000/users"
            res = requests.post(url,json.dumps(data))
            st.write(res.status_code)
            
            if res.status_code == 200:
                st.success("登録しました")
            st.json(res.json())

            
if selected == "rooms":
    st.title("会議室登録画面")
    with st.form("rooms"):
        room_name:str = st.text_input('ルームネーム', max_chars=20)
        capacity:int = st.number_input("キャパシティ",min_value=1,max_value=10)
        data = {
            "room_name" : room_name,
            "capacity" : capacity
        }
        
        submitted = st.form_submit_button(label="登録")
        
        if submitted:
            st.write("送信データ")
            st.json(data)
            st.write("レスポンス結果")
            url = "http://127.0.0.1:8000/rooms"
            res = requests.post(url,json.dumps(data))
            st.write("status code",res.status_code)
            if res.status_code == 200:
                st.success("登録しました")
            st.json(res.json())
            
if selected == "bookings":
    st.title("予約画面")
    
    #ユーザー一覧取得
    url_users = "http://127.0.0.1:8000/users"
    res = requests.get(url_users)
    users = res.json()
    
    #キーにユーザーネーム，値にユーザーID
    user_dict:dict = {}
    for user in users:
        user_dict[user['user_name']] = user['user_id']
        
    #キーにユーザーID，値にユーザーネーム
    user_dict_reverse:dict = {value:key for key,value in user_dict.items()}
    
    #会議室一覧取得
    url_rooms = "http://127.0.0.1:8000/rooms"
    res = requests.get(url_rooms)
    rooms = res.json()

    #キーに会議室名，値に辞書(キー：ID,キャパシティ)
    room_dict:dict = {}
    for room in rooms:
        room_dict[room['room_name']] = {
            "room_id" : room['room_id'],
            "room_capacity" : room['capacity']
        }
    
    #キーにroom_id，値にdict{room_name,room_capacity}
    room_id_to_name: dict = {}
    for room in rooms:
        room_id_to_name[room["room_id"]] = {
            "room_name" : room["room_name"],
            "room_capacity" : room["capacity"]
        }
    
    to_user_name = lambda x:user_dict_reverse[x]
    to_room_name = lambda x:room_id_to_name[x]["room_name"]
    to_datetime = lambda x:datetime.datetime.fromisoformat(x).strftime("%Y/%m/%d %H:%M")
    
    
    #予約一覧取得
    st.write("### 予約一覧")
    url_bookings = "http://127.0.0.1:8000/bookings"
    res = requests.get(url_bookings)
    bookings = res.json()
    df_bookings =  pd.DataFrame(bookings)
    df_bookings["user_id"] = df_bookings["user_id"].map(to_user_name)
    df_bookings["room_id"] = df_bookings["room_id"].map(to_room_name)
    df_bookings["start_datetime"] = df_bookings["start_datetime"].map(to_datetime)
    df_bookings["end_datetime"] = df_bookings["end_datetime"].map(to_datetime)
    df_bookings = df_bookings.rename(columns={
        "user_id":"予約者名",
        "room_id": "会議室名",
        "booking_num": "人数",
        "start_datetime": "開始時間",
        "end_datetime": "終了時間",
        "booking_id" : "予約番号"
    })
    hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    st.table(df_bookings)
    
    #会議室一覧
    st.write("### 会議室一覧")
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ["会議室名","キャパシティ","会議室ID"]
    st.table(df_rooms)
    
    with st.form("bookings"):
        user_name:str = st.selectbox("ユーザーネーム",user_dict.keys())
        room_name:str = st.selectbox("会議室名",room_dict.keys())
        booking_num: int = st.number_input("人数",min_value=1,max_value=10)
        date = st.date_input("日付を入力", min_value=datetime.date.today())
        start_time = st.time_input("開始時刻",value=datetime.time(hour=9,minute=0))
        end_time = st.time_input("終了時刻",value=datetime.time(hour=10,minute=0))
        submitted = st.form_submit_button("送信")
        
        if submitted:
            user_id:int = user_dict[user_name]
            room_id:int = room_dict[room_name]["room_id"]
            room_capacity:int = room_dict[room_name]["room_capacity"]
            data = {
                "user_id" : user_id,
                "room_id" : room_id,
                "booking_num" : booking_num,
                "start_datetime": datetime.datetime(
                    year = date.year,
                    month = date.month,
                    day = date.day,
                    hour = start_time.hour,
                    minute = start_time.minute
                    ).isoformat(),
                "end_datetime" : datetime.datetime(
                    year = date.year,
                    month = date.month,
                    day = date.day,
                    hour = end_time.hour,
                    minute = end_time.minute
                    ).isoformat()
            }
            #定員Overの場合
            if room_capacity < booking_num: 
                st.error(f'{room_name}の定員は{room_capacity}です')
            elif start_time > end_time:
                st.error("終了時間より早くは始められません")
            elif start_time < datetime.time(hour=9,minute=0,second=0) or end_time > datetime.time(hour=20,minute=0,second=0):
                st.error("利用時間は9:00~20:00です")
            else:
                url = "http://127.0.0.1:8000/bookings"
                res = requests.post(url,json.dumps(data))
                st.write(res.status_code)
                if res.status_code == 200:
                    st.success("予約しました")
                elif res.status_code == 404 and res.json()["detail"] == "Already booked":
                    st.error("すでに他の予約があります")
                    
if selected == "booking_delete":
    st.title("予約削除画面")
    with st.form("booking_delete"):
        booking_id: int = st.number_input("削除する予約番号を入力してください", step=1)
        submitted = st.form_submit_button(label="削除")
        
        if submitted:
            url = "http://127.0.0.1:8000/bookings/{0}".format(booking_id)
            st.write(url)
            st.write(booking_id)
            res = requests.delete(url)
            st.write("status code",res.status_code)
            if res.status_code == 200:
                st.success("削除しました")
            st.json(res.json())