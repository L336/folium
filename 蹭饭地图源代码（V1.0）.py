#LHG 2024年3月15日 V1.0 原始版本
import pandas as pd
import folium
from folium import Map, Marker, Popup

# 读取Excel表格数据（请替换为自己电脑上的的文件路径）
df = pd.read_excel(r"D:\python\20240315\蹭饭地图开发文档（脱密版）\地理坐标.xlsx")

#电话号码转为整数
df['Phone'] = df['Phone'].apply(lambda x: str(int(x)) if pd.notnull(x) else x)

# 创建地图并设置中心点和缩放级别，同时添加高德地图作为底图
m = Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)
tile_layer = folium.TileLayer(r"https://webrd04.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}", attr="<a href=https://ditu.amap.com/>高德地图</a>")
tile_layer.add_to(m)

# 遍历数据，为每个人添加标记和弹出窗口内容
for index, row in df.iterrows():
    popup_content = f'<b>姓名:</b> {row["Name"]}<br><b>所在地:</b> {row["Location"]}'
    
    contact_info = row['Phone'] if pd.notna(row['Phone']) else row['Email']
    popup_content += f'<br><b>联系方式:</b> {contact_info}'

    marker = Marker(location=[row['Latitude'], row['Longitude']], popup=Popup(popup_content))
    marker.add_to(m)

# 计算所有经纬度的最大最小值
min_lat = df['Latitude'].min()
max_lat = df['Latitude'].max()
min_lon = df['Longitude'].min()
max_lon = df['Longitude'].max()

# 设置地图的初始视图为包含所有Marker的边界框
bounds = [(min_lat, min_lon), (max_lat, max_lon)]
m.fit_bounds(bounds)

# 保存地图为HTML文件(文件路径请替换为自己的)
m.save(r"D:\python\20240315\蹭饭地图开发文档（脱密版）\蹭饭地图（V1.0）.html")