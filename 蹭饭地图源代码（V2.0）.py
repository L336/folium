#LHG 2024年3月16日
#V2.0更新：添加了搜索框，解决了重叠点的显示问题，为优化境外使用体验，引入了谷歌地图瓦片服务，另外增加了晨昏线、鼠标位置、使用者位置等插件
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import Search
from folium.plugins import MousePosition
from folium.plugins import Terminator
from folium.plugins import LocateControl
from folium.plugins import MarkerCluster

# 读取Excel表格数据（请替换为自己电脑上的的文件路径）
df = pd.read_excel(r"D:\python\20240315\蹭饭地图开发文档（脱密版）\地理坐标.xlsx")

#电话号码转为整数
df['Phone'] = df['Phone'].apply(lambda x: str(int(x)) if pd.notnull(x) else x)

# 合并电话号码和电邮信息为一列
df['Contact_info'] = df['Phone'].where(df['Phone'].notna(), df['Email'])

# 删除Phone和Email列
df = df.drop(columns=['Phone', 'Email'])

#创建几何对象（Point）
geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]

#创建 GeoDataFrame，设置坐标参考系
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

# 创建地图并设置中心点和缩放级别
m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10, tiles=None)

#添加谷歌、高德瓦片底图
tile_layer_1 = folium.TileLayer(r"https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="<a href=https://www.google.com/maps>谷歌地图</a>", name='谷歌地图')
tile_layer_1.add_to(m)
tile_layer_2 = folium.TileLayer(r"https://webrd04.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}", attr="<a href=https://ditu.amap.com/>高德地图</a>", name='高德地图')
tile_layer_2.add_to(m)

#创建 MarkerCluster 对象，以实现重合点的显示
marker_cluster = MarkerCluster(name="同学信息").add_to(m)

# 添加图层控制，以支持使用者对底图的选择
folium.LayerControl(collapsed=False).add_to(m)

#添加人员位置标记图层
classmate_geo = folium.GeoJson(
    gdf,
    name="同学信息",
    tooltip=folium.GeoJsonTooltip(
        fields=["Name", "Location", "Contact_info"], aliases=["姓名", "位置", "联系方式"],# 可选，设置鼠标悬停提示 
        localize=True,
    ),
).add_to(marker_cluster)

#添加搜索框
citysearch = Search(
    layer=classmate_geo,
    geom_type="Point",
    placeholder="输入姓名搜索", #搜索框提示
    collapsed=False, #搜索框不折叠
    search_label="Name",
    weight=8, #关键词的权重
    search_zoom=15, #搜索结果定位到地图上时的缩放级别
).add_to(m)

#使用 CSS 的 .leaflet-control-search 类选择器来定位搜索框，并设置其宽度为 190 像素、高度为 35 像素
search_box_css = """
<style>
.leaflet-control-search {
    width: 190px;  /* 自定义搜索框宽度 */
    height: 35px;  /* 自定义搜索框高度 */
}
</style>
"""

#通过 get_root().html.add_child() 方法，将 CSS 样式字符串添加到地图对象中
m.get_root().html.add_child(folium.Element(search_box_css))

#使用 CSS 的 .leaflet-control-search .search-input 选择器定位搜索框的输入框，并设置其宽度为 150 像素、高度为 25 像素
search_input_css = """
<style>
.leaflet-control-search .search-input {
    width: 150px;  /* 自定义输入框宽度 */
    height: 25px;  /* 自定义输入框高度 */
}
</style>
"""

#通过 get_root().html.add_child() 方法，将 CSS 样式字符串添加到地图对象中
m.get_root().html.add_child(folium.Element(search_input_css))

#使用 CSS 的 .leaflet-control-search .search-input::placeholder 选择器定位搜索框的提示语，并设置其字体大小为 14 像素
search_placeholder_css = """
<style>
.leaflet-control-search .search-input::placeholder {
    font-size: 14px;  /* 自定义提示语字体大小 */
}
</style>
"""

#通过 get_root().html.add_child() 方法，将 CSS 样式字符串添加到地图对象中
m.get_root().html.add_child(folium.Element(search_placeholder_css))

# 计算所有经纬度的最大最小值
min_lat = df['Latitude'].min()
max_lat = df['Latitude'].max()
min_lon = df['Longitude'].min()
max_lon = df['Longitude'].max()

# 设置地图的初始视图为包含所有Marker的边界框
bounds = [(min_lat, min_lon), (max_lat, max_lon)]
m.fit_bounds(bounds)

# 创建鼠标位置插件，并指定自定义的经纬度格式化函数
formatter = "function(num) {return L.Util.formatNum(num, 3) + ' &deg; ';};"
MousePosition(
    position="topright",#位置在右上角
    separator=" , ",
    empty_string="NaN",
    lng_first=True,num_digits=20,
    prefix="经纬度:",
    lat_formatter=formatter,
    lng_formatter=formatter,
).add_to(m)

#显示使用者的位置
LocateControl(auto_start=False, strings={'title': '点击以获取当前位置'#控件标题
                                         }  ).add_to(m)

#添加实时晨昏线
Terminator().add_to(m)

# 保存地图为HTML文件(文件路径请替换为自己的)
m.save(r"D:\python\20240315\蹭饭地图开发文档（脱密版）\蹭饭地图（V2.0）.html")

# 如果在Jupyter Notebook中运行，则可以直接显示地图
m