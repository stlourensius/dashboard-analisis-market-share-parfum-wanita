import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def load_data(file_name):
    df = pd.read_excel(file_name)

    # Create a new column "Volume"
    patterns = [r'\d+ml', r'\d+\s*ml']

    volume = []
    for i in range(len(df)):
        product_name = df.loc[i, "Product Name"]
        
        for pattern in patterns:
            match = re.search(pattern, product_name)
            
            if match:
                vol = match.group()
                vol = re.search(r'\d+', vol).group()
                volume.append(vol)
                break

    volume = pd.Series(volume).unique()
    df["Volume"] = np.nan
    aggregate_by_vol = pd.DataFrame(columns = df.describe().transpose().columns)

    for vol in volume:
        index_ = df[(df["Product Name"].str.contains(f"{vol} ml")) | (df["Product Name"].str.contains(f"{vol}ml"))].index
        
        vol_describe = df[(df["Product Name"].str.contains(f"{vol} ml")) | (df["Product Name"].str.contains(f"{vol}ml"))].describe().transpose().loc["Current Price"]
        aggregate_by_vol = pd.concat([aggregate_by_vol, pd.DataFrame(vol_describe.rename(vol)).transpose()])
        
        for index in index_:
            df.loc[index, "Volume"] = int(vol)

    aggregate_by_vol = aggregate_by_vol.reset_index(names = "Volume")
    aggregate_by_vol["Volume"] = aggregate_by_vol["Volume"].astype("int64")
    aggregate_by_vol = aggregate_by_vol.sort_values("Volume").reset_index(drop = True)

    return df, aggregate_by_vol

def filter_data(data_frame, filter):
    filtered_data = data_frame[data_frame["Current Price"] <= filter].reset_index(drop = True)
    return filtered_data

def bar_store_most_sales(df):
    store_most_sales = df.groupby("Store Name").sum(numeric_only = True).sort_values("Number Sold", ascending = False).reset_index()

    other_store_sales = df.loc[21:, "Number Sold"].sum()
    other_store_sales = pd.DataFrame(data = {"Store Name" : "Other Store",
                                            "Current Price" : np.nan,
                                            "Discount" : np.nan,
                                            "Price Before Discount" : np.nan,
                                            "Rating" : np.nan,
                                            "Number Sold" : other_store_sales},
                                    index = [0])

    store_most_sales = store_most_sales.iloc[0:20].sort_values("Number Sold", ascending = True)
    store_most_sales = pd.concat([other_store_sales, store_most_sales])

    fig = px.bar(store_most_sales, x = "Number Sold", y = "Store Name",  title = "20 Toko Penjualan Terbanyak",
             text_auto = True, labels = {"Number Sold" : "Terjual", "Store Name" : "Toko"},
             color_discrete_sequence = px.colors.qualitative.Set3)
    fig.update_layout(xaxis = {"showgrid" : True})

    return fig

def pie_five_most_sales(df):
    five_most_sales = df.groupby("Store Name").sum(numeric_only = True).sort_values("Number Sold", ascending = False).reset_index()

    other_store_sales = df.loc[6:, "Number Sold"].sum()
    other_store_sales = pd.DataFrame(data = {"Store Name" : "Other Store",
                                            "Current Price" : np.nan,
                                            "Discount" : np.nan,
                                            "Price Before Discount" : np.nan,
                                            "Rating" : np.nan,
                                            "Number Sold" : other_store_sales},
                                    index = [0])

    five_most_sales = five_most_sales.iloc[0:5].sort_values("Number Sold", ascending = True)
    five_most_sales = pd.concat([other_store_sales, five_most_sales])

    fig = px.pie(five_most_sales, values = "Number Sold", names = "Store Name", title = "Persentase Lima Toko Penjualan Terbanyak", 
                 color_discrete_sequence = px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def hist_price_to_sales(df, nbins):
    fig = px.histogram(df, x = "Current Price", y = "Number Sold", title = "Harga vs Penjualan",
                   nbins = nbins, template = "simple_white", labels = {"Number Sold" : "Terjual", "Current Price" : "Harga"},
                   color_discrete_sequence = px.colors.qualitative.Set3)
    
    fig.update_layout(title_x = 0.5, yaxis = {"title" : "Total Terjual", 
                                              "showgrid" : True})
    return fig

def bar_ad_to_sales(df):
    ad = df.groupby("Ad").sum(numeric_only = True).reset_index()

    fig = px.bar(ad, x = "Ad", y = "Number Sold", title = "Perbandingan Promosi (Ad) vs Tidak Promosi (Not Ad)",
                template = "simple_white", labels = {"Number Sold" : "Terjual", "Ad" : "Jenis Postingan"}, 
                color_discrete_sequence = px.colors.qualitative.Set3)
    fig.update_layout(yaxis = {"showgrid" : True})
    return fig

def bar_store_type_sales(df):
    store_type_sales = df.groupby(["Store Class", "Ad"]).sum(numeric_only = True).reset_index()

    fig = px.bar(store_type_sales, x = "Store Class", y = "Number Sold", title = "Penjualan Berdasarkan Tipe Toko", color = "Ad",
                template = "simple_white", labels = {"Number Sold" : "Terjual", "Store Class" : "Tipe Toko"}, 
                color_discrete_sequence = px.colors.qualitative.Set3)
    fig.update_layout(yaxis = {"showgrid" : True})
    return fig

def hist_vol_price(df, nbins, x, y):
    fig = px.histogram(df, x = x, y = y, title = "Histogram Harga-Volume Parfum",
                   nbins = nbins, template = "simple_white", histfunc = "avg", 
                   color_discrete_sequence = px.colors.qualitative.Set3)
    
    return fig