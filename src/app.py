import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    if os.path.exists('session.json'):
        with open('session.json', 'r') as f:
            session_data = json.load(f)
            st.session_state.authenticated = session_data.get('authenticated', False)

def save_session():
    session_data = {
        'authenticated': st.session_state.authenticated
    }
    with open('session.json', 'w') as f:
        json.dump(session_data, f)

# Data file paths
BOOKINGS_FILE = os.path.join('data', 'bookings.csv')
PARTICIPANTS_FILE = os.path.join('data', 'participants.csv')
USERS_FILE = os.path.join('data', 'users.csv')

# Initialize CSV files if they don't exist
def init_csv_files():
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if not os.path.exists(BOOKINGS_FILE):
        pd.DataFrame(columns=[
            'id', 'facility', 'court_number', 'start_time', 
            'end_time', 'latest_file'
        ]).to_csv(BOOKINGS_FILE, index=False)
    
    if not os.path.exists(PARTICIPANTS_FILE):
        pd.DataFrame(columns=[
            'booking_id', 'name', 'contact'
        ]).to_csv(PARTICIPANTS_FILE, index=False)

def load_data():
    bookings = pd.read_csv(BOOKINGS_FILE)
    participants = pd.read_csv(PARTICIPANTS_FILE)
    return bookings, participants

def main():

    css = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        .element-container:has(button.stDeployButton) {display:none;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    st.title("勝中テニス会コート予約状況")
    
    init_csv_files()
    
    # ログインフォーム
    if not st.session_state.authenticated:
        with st.form("login_form"):
            username = st.text_input("ユーザー名")
            password = st.text_input("パスワード", type="password")
            if st.form_submit_button("ログイン"):
                if (username == st.secrets["credentials"]["username"] and 
                    password == st.secrets["credentials"]["password"]):
                    st.session_state.authenticated = True
                else:
                    st.error("ユーザー名またはパスワードが違います")
                save_session()
                st.rerun()
    
    else:
        if st.button("ログアウト"):
            st.session_state.authenticated = False
            save_session()
            st.rerun()
        # メインアプリケーション
        tab1, tab2 = st.tabs(["予約一覧", "新規登録"])
        
        with tab1:
            display_bookings()
            
        with tab2:
            create_booking()

def delete_booking(booking_id):
    bookings = pd.read_csv(BOOKINGS_FILE)
    participants = pd.read_csv(PARTICIPANTS_FILE)
    
    # Delete booking
    bookings = bookings[bookings['id'] != booking_id]
    bookings.to_csv(BOOKINGS_FILE, index=False)
    
    # Delete associated participants
    participants = participants[participants['booking_id'] != booking_id]
    participants.to_csv(PARTICIPANTS_FILE, index=False)
    
    st.success("予約を削除しました")
    st.rerun()

def add_participant(booking_id, name):
    participants = pd.read_csv(PARTICIPANTS_FILE)
    new_participant = pd.DataFrame([{
        'booking_id': booking_id,
        'name': name,
        'contact': ''  # Empty string for contact
    }])
    participants = pd.concat([participants, new_participant], ignore_index=True)
    participants.to_csv(PARTICIPANTS_FILE, index=False)
    st.success("参加者を追加しました")
    st.rerun()

def delete_participant(booking_id, participant_name):
    participants = pd.read_csv(PARTICIPANTS_FILE)
    participants = participants[~((participants['booking_id'] == booking_id) & 
                                (participants['name'] == participant_name))]
    participants.to_csv(PARTICIPANTS_FILE, index=False)
    st.success("参加者を削除しました")
    st.rerun()

def display_bookings():
    bookings, participants = load_data()
    if not bookings.empty:
        for _, booking in bookings.iterrows():
            # 日時をフォーマット
            start_datetime = datetime.strptime(booking['start_time'], '%Y-%m-%d %H:%M')
            formatted_date = start_datetime.strftime('%Y年%m月%d日 %H:%M')
            
            # タイトルを大きく表示（日時を含める）
            title = f"### {booking['facility']} - コート{booking['court_number']} ({formatted_date})"
            with st.expander(title):
                st.write(f"**予約日時:** {booking['start_time']} 〜 {booking['end_time']}")
                
                # 参加者一覧
                booking_participants = participants[participants['booking_id'] == booking['id']]
                if not booking_participants.empty:
                    st.write("**参加者リスト:**")
                    for _, participant in booking_participants.iterrows():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"- {participant['name']}")
                        with col2:
                            if st.button("削除", key=f"delete_participant_{booking['id']}_{participant['name']}"):
                                delete_participant(booking['id'], participant['name'])
                
                # 参加者追加フォーム
                with st.form(key=f"add_participant_{booking['id']}"):
                    name = st.text_input("名前", key=f"name_{booking['id']}")
                    if st.form_submit_button("参加者を追加"):
                        add_participant(booking['id'], name)
                
                # 予約削除ボタン
                if st.button("予約を削除", key=f"delete_booking_{booking['id']}"):
                    delete_booking(booking['id'])

def create_booking():
    with st.form("booking_form"):
        facility = st.text_input("施設名")
        court_number = st.number_input("コート番号", min_value=1)
        
        # 日付と時間を別々に入力
        start_date = st.date_input("予約日")
        start_time = st.time_input("開始時間")
        end_time = st.time_input("終了時間")
        
        if st.form_submit_button("登録する"):
            bookings = pd.read_csv(BOOKINGS_FILE)
            new_id = len(bookings) + 1
            
            # 日付と時間を組み合わせてdatetimeオブジェクトを作成
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(start_date, end_time)
            
            new_booking = pd.DataFrame([{
                'id': new_id,
                'facility': facility,
                'court_number': court_number,
                'start_time': start_datetime.strftime('%Y-%m-%d %H:%M'),
                'end_time': end_datetime.strftime('%Y-%m-%d %H:%M'),
                'latest_file': ''
            }])
            bookings = pd.concat([bookings, new_booking], ignore_index=True)
            bookings.to_csv(BOOKINGS_FILE, index=False)
            st.success("予約が完了しました！")
            st.rerun()

if __name__ == "__main__":
    main()