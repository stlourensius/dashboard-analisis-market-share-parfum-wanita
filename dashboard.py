from module import *
import streamlit as st
from PIL import Image

st.set_page_config(page_title = "Dashboard Analisis Market Share Parfum Wanita",
                   layout = "wide")

df, volume_to_price = load_data("female_perfume_cleaned.xlsx")

reduce_header_height_style = """
                                <style>
                                        div.block-container {padding-top : 1rem;
                                        div.block-container {padding-bottom : 1rem;
                                </style>
                            """

st.markdown(reduce_header_height_style, unsafe_allow_html = True)

if 'price_to_sales_slider' not in st.session_state:
    st.session_state['price_to_sales_slider'] = 10
if "volume_price_slider" not in st.session_state:
    st.session_state["volume_price_slider"] = 5     

st.title("Dashboard Analisis Market Share Parfum Wanita")
st.divider()
st.subheader("Tentang Dashboard")

col1, col2 = st.columns(2)
with col1:
    image = Image.open("tokopedia.png")
    st.image(image, caption = "Tokopedia Search Result")

with col2:
    st.write("""Data yang digunakan dalam analisis ini diperoleh dari hasil scrapping pada e-commerce Tokopedia. 
             Keyword yang digunakan pada pencarian produk adalah "parfum wanita". Scraping dilakukan hingga halaman pencarian paling akhir yaitu pada halaman 100.
             Terdapat 7974 produk parfurm yang berhasil diperoleh. Secara default, dashboard ini hanya menganalisis parfurm dengan harga dibawah Rp500.000. Pengaturan filter dapat dilakukan pada sidebar dashboard ini.
             Dashboard ini ditujukan untuk memperoleh informasi toko mana saja yang memiliki penjualan parfum terbanyak dan parfurm apa saja yang paling diminati oleh wanita.""")
    
with st.expander("Pengaturan Filter Data"):
    filter = st.slider("Data dapat diatur sesuai dengan rentang harga parfurm yang diinginkan", 50000, 2000000, 500000, 25000)
    st.write(f"Data diambil dari rentang harga Rp0 - Rp{filter}")
    filtered_df = filter_data(df, filter)
    st.subheader("Raw Data")
    st.write(filtered_df)

st.divider()
st.subheader("Toko apa saja yang memiliki penjualan terbanyak?")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(bar_store_most_sales(filtered_df), use_container_width = True)

with col2:
    st.plotly_chart(pie_five_most_sales(filtered_df), use_container_width = True)
    
st.divider()
st.markdown("<h5>Bagaimana pengaruh penggunaan promosi berbayar terhadap penjualan dan bagaimana kinerja dari setiap tipe toko?</h4>", unsafe_allow_html = True)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(bar_ad_to_sales(filtered_df), use_container_width = True)

with col2:
    st.plotly_chart(bar_store_type_sales(filtered_df), use_container_width = True)

st.divider()
st.subheader("Bagaimana tingkat penjualan pada rentang harga tertentu?")
st.plotly_chart(hist_price_to_sales(filtered_df, st.session_state["price_to_sales_slider"]), use_container_width = True)
st.slider("Pengaturan banyaknya bin", 1, 25, step = 1, key = "price_to_sales_slider")

st.divider()
st.subheader("Bagaimana harga parfum untuk volume parfum tertentu?")

col1, col2= st.columns(2)
with col1:
    @st.cache_data
    def change_y():
        if st.session_state["radio_x"] == "Harga":
            st.session_state["radio_y"] = "Volume"
        else:
            st.session_state["radio_y"] = "Harga"

    st.radio("Pilih Variabel untuk Sumbu X",
             ["Harga", "Volume"],
             key = "radio_x",
             on_change = change_y)
    
    if st.session_state["radio_x"] == "Harga":
        st.session_state["radio_y"] = "Volume"
    else:
        st.session_state["radio_y"] = "Harga"
with col2:
    @st.cache_data
    def change_x():
        if st.session_state["radio_y"] == "Volume":
            st.session_state["radio_x"] = "Harga"
        else:
            st.session_state["radio_x"] = "Volume"

    st.radio("Pilih Variabel untuk Sumbu Y",
             ["Harga", "Volume"],
             key = "radio_y",
             on_change = change_x)

if st.session_state["radio_x"] == "Harga":
    radio_input1 = "Current Price"
    radio_input2 = "Volume"
else:
    radio_input1 = "Volume"
    radio_input2 = "Current Price"
st.plotly_chart(hist_vol_price(filtered_df, st.session_state["volume_price_slider"],
                               radio_input1, radio_input2), use_container_width = True)
st.slider("Pengaturan banyaknya bin", 1, 20, step = 1, key = "volume_price_slider")

col1, col2 = st.columns(2)
with col1:
    st.write("Deskriptif statistik untuk setiap volume parfum")
    st.write(volume_to_price.sort_values("Volume").reset_index(drop = True))

with col2:
    selected_vol = st.selectbox("Tampilkan parfum dengan volume ....", volume_to_price["Volume"].unique())
    df_selected_vol = filtered_df[(filtered_df["Product Name"].str.contains(f"{selected_vol} ml")) | (filtered_df["Product Name"].str.contains(f"{selected_vol}ml"))]
    st.write(df_selected_vol)