import streamlit as st
import requests
import pandas as pd

# 1. 設定網頁標題與說明
st.title("🚲 台北市 YouBike 2.0 即時動態儀表板")
st.write("這是一個結合政府開放資料與即時更新機制的資料管線展示專案。")

# 2. 定義抓取與清洗資料的函數 (Data Pipeline / ETL)
# 💡 這裡加上了 st.cache_data(ttl=300)，代表每 300 秒 (5分鐘) 會自動重新抓取最新資料！
# 這完美符合了作業要求中 0-2 分的 Data refresh mechanism！
@st.cache_data(ttl=300)
def load_and_clean_data():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        cleaned_data = []
        for station in data:
            try:
                # 使用你剛剛成功找出的正確欄位
                station_id = station['sno']
                name = station['sna'].replace("YouBike2.0_", "") 
                total_spots = station['Quantity']
                bikes_available = station['available_rent_bikes']
                empty_spots = station['available_return_bikes']
                
                # 計算空車率 (展現 ETL 創意)
                if total_spots > 0:
                    availability_rate = round((bikes_available / total_spots) * 100, 1)
                else:
                    availability_rate = 0.0
                    
                cleaned_station = {
                    "站點代號": station_id,
                    "站點名稱": name,
                    "總車格": total_spots,
                    "可借車輛": bikes_available,
                    "可還空位": empty_spots,
                    "可借比例(%)": availability_rate
                }
                cleaned_data.append(cleaned_station)
            except KeyError:
                continue # 遇到壞資料就跳過
                
        # 將整理好的字典列表轉換為 Pandas 表格格式，方便前端畫圖
        return pd.DataFrame(cleaned_data)
    else:
        return pd.DataFrame()

# 3. 執行資料管線並將資料載入前端
with st.spinner('正在從政府 API 抓取並處理最新資料...'):
    df = load_and_clean_data()

if not df.empty:
    st.success(f"資料管線執行成功！目前共載入 {len(df)} 個站點的即時狀態。")
    
    # 4. 視覺化設計 (對應作業評分標準 Visualization 0-3 分)
    st.subheader("📊 可借車輛最多的 Top 10 站點")
    # 抓出可借車輛最多的前 10 名
    top_10_bikes = df.nlargest(10, "可借車輛")
    # 畫出長條圖
    st.bar_chart(data=top_10_bikes, x="站點名稱", y="可借車輛")
    
    st.subheader("📋 完整即時資料表")
    # 在網頁上顯示可互動的表格
    st.dataframe(df)
else:
    st.error("無法抓取資料，請稍後再試。")