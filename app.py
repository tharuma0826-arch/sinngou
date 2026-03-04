import streamlit as st
import folium as folium
from streamlit_folium import st_folium
import math
import time
from streamlit_js_eval import get_geolocation
st.set_page_config(page_title="信号予測アプリ", layout="centered")
st.title("信号予測アプリ")
st.caption("現在地と信号の位置から、信号の状態を予測します。")
st.divider()

#固定値
cycle = 120 #周期
redtime = 60  #赤信号の時間

#地図の中心座標
center_lat = 35.2214855
center_lon = 136.8851517

#信号データ(座標)
signals = {
    "赤代町交差点（縦）": (35.2215809, 136.8863208,0),
    "赤代町交差点(横)": (35.2216515, 136.88616,10),
    "ツルハドラッグ交差点(縦）": (35.2211560, 136.8829332,20),
    "ツルハドラッグ交差点（横）": (35.221212, 136.8827847,30),
    "山田中学校前": (35.2232048, 136.87887238,40),
    "名古屋第二環状自動車道": (35.2234179, 136.8789380,50),
}

#距離計算関数
def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # 地球の半径（メートル）
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

#現在地入力
st.subheader("📍現在地")
if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lon = None

if st.button("現在地を取得"):
    location = get_geolocation()
    if location:
        user_lat = location["coords"]["latitude"]
        user_lon = location["coords"]["longitude"]
        st.success("現在地を取得しました。")
    else:
        st.error("現在地の取得に失敗しました。")
if st.session_state.user_lat is not None:
    user_lat = st.session_state.user_lat
    user_lon = st.session_state.user_lon

else:
    user_lat = center_lat
    user_lon = center_lon


#地図表示
m = folium.Map([center_lat, center_lon], zoom_start=16)

for name, (lat, lon,offset) in signals.items():
    folium.Marker([lat, lon], popup=name, icon=folium.Icon(color="blue")).add_to(m)

folium.Marker([user_lat, user_lon], popup="現在地", icon=folium.Icon(color="red")).add_to(m)
st.subheader("🗺 地図")
st_folium(m, width=700, height=500)


#信号マーカー
for name, (lat, lon,offset) in signals.items():
    folium.Marker([lat, lon], popup=name, icon=folium.Icon(color="blue")).add_to(m)

#自分の位置
folium.Marker(location=[user_lat, user_lon], popup="現在地", icon=folium.Icon(color="red")).add_to(m)


#信号判定
st.subheader("信号の予測")

speed = st.number_input("移動速度 (m/s)", value=1.2)

if st.button("予測開始"):
    current_time = time.time()
    for name, (lat, lon, offset) in signals.items():
        distance = calc_distance(user_lat, user_lon, lat, lon)
        arrival_time = distance / speed
        #ずらし
        signal_time = (current_time + arrival_time + offset) % cycle
        if signal_time < redtime:
            st.error(f"{name}は赤信号です。(距離{round(distance, 1)}m)")
        else:           
            st.success(f"{name} は青信号です。(距離{round(distance, 1)}m)")
     