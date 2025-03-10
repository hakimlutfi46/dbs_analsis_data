import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
import seaborn as sns
from geobr import read_state
import streamlit as st
from streamlit_folium import folium_static

try:
    df = pd.read_csv('dashboard/merged_dataset.csv')
except FileNotFoundError:
    df = pd.read_csv('merged_dataset.csv')

df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

st.sidebar.header("Filter")
years = df['order_purchase_timestamp'].dt.year.unique()

selected_years = st.sidebar.multiselect('Pilih Tahun', options=years, default=list(years))
if not selected_years:
    st.warning("Silakan pilih setidaknya satu tahun untuk menampilkan data.")
    st.stop()
filtered_data = df[df['order_purchase_timestamp'].dt.year.isin(selected_years)]

filtered_data['revenue'] = filtered_data['price'] * filtered_data['order_item_id']
total_revenue = filtered_data['revenue'].sum()
total_reviews = filtered_data['review_score'].sum()
total_products_sold = filtered_data['order_item_id'].sum()

st.title("Analisis Data E-commerce Public Dataset")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Pendapatan", value=f"{total_revenue:,.0f}")

with col2:
    st.metric(label="Total Review Score", value=f"{total_reviews:,.0f}")

with col3:
    st.metric(label="Total Produk Terjual", value=f"{total_products_sold:,.0f}")


st.subheader("Penjualan Produk Terlaris dalam Kategori Tertentu")

tab1, tab2 = st.tabs(["Produk Terjual", "Pendapatan Produk"])

with tab1:    
    st.write(""" ##### Berdasarkan Jumlah Produk Terjual """)
    
    category_sales = filtered_data.groupby('product_category_name_english')['order_item_id'].sum().reset_index()
    
    top_categories_sales = category_sales.sort_values(by='order_item_id', ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='order_item_id', y='product_category_name_english', data=top_categories_sales, palette='Blues_r')
    plt.xlabel('Jumlah Produk Terjual')
    plt.ylabel('Kategori Produk')
    plt.title('Top 10 Kategori Produk Terlaris')
    st.pyplot(plt)

    st.write("Top 10 kategori produk dengan jumlah produk terjual tertinggi:")
    st.write(top_categories_sales)

with tab2:    
    st.write(""" ##### Berdasarkan Pendapatan Produk """)
    
    category_revenue = filtered_data.groupby('product_category_name_english')['revenue'].sum().reset_index()
    
    top_categories_revenue = category_revenue.sort_values(by='revenue', ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='revenue', y='product_category_name_english', data=top_categories_revenue, palette='viridis')
    plt.xlabel('Pendapatan')
    plt.ylabel('Kategori Produk')
    plt.title('Top 10 Kategori Produk dengan Pendapatan Tertinggi')
    st.pyplot(plt)

    st.write("Top 10 kategori produk dengan pendapatan tertinggi:")
    st.write(top_categories_revenue)

st.subheader("Rating Produk")
tab1, tab2, tab3 = st.tabs(["Tren Penjualan & Review Score","Tren Review", "Kategori Produk" ])

with tab1: 
    monthly_sales = filtered_data.groupby(filtered_data['order_purchase_timestamp'].dt.to_period("M")).agg({
        'order_item_id': 'sum',  
        'review_score': 'mean'   
    }).reset_index()

    monthly_sales['order_purchase_timestamp'] = monthly_sales['order_purchase_timestamp'].astype(str)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=monthly_sales, 
        x='order_purchase_timestamp', 
        y='order_item_id', 
        marker='o', 
        color='b', 
        label='Total Produk Terjual', 
        ax=ax1
    )

    ax2 = ax1.twinx()
    sns.lineplot(
        data=monthly_sales, 
        x='order_purchase_timestamp', 
        y='review_score', 
        marker='s', 
        color='r', 
        linestyle='dashed', 
        label='Rata-rata Review Score', 
        ax=ax2
    )

    ax1.set_xlabel('Bulan', fontsize=12)
    ax1.set_ylabel('Total Produk Terjual', fontsize=12, color='b')
    ax2.set_ylabel('Rata-rata Review Score', fontsize=12, color='r')
    plt.title('Tren Penjualan dan Rata-rata Review Score per Bulan', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    st.pyplot(fig)
    
with tab2:
    st.write(""" #### Tren Rating Berdasarkan Waktu """)

    monthly_rating = filtered_data.groupby(filtered_data['order_purchase_timestamp'].dt.to_period("M")).agg({
        'review_score': 'mean'
    }).reset_index()

    monthly_rating['order_purchase_timestamp'] = monthly_rating['order_purchase_timestamp'].astype(str)

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_rating, x='order_purchase_timestamp', y='review_score', marker='o', color='orange')
    plt.xlabel('Bulan', fontsize=12)
    plt.ylabel('Rata-rata Review Score', fontsize=12)
    plt.title('Tren Rating Pelanggan per Bulan', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    st.pyplot(plt)



with tab3:    
    st.write(""" ##### Distribusi Rating per Kategori Produk """)
    category_reviews = filtered_data.groupby('product_category_name_english')['review_score'].mean().reset_index()

    plt.figure(figsize=(12, 6))
    sns.barplot(data=category_reviews, x='product_category_name_english', y='review_score', palette='coolwarm')
    plt.xlabel('Kategori Produk')
    plt.ylabel('Rata-rata Review Score')
    plt.title('Rata-rata Review Score per Kategori Produk')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt)

df_cluster = filtered_data[['customer_state', 'order_item_id']].copy()
df_cluster = df_cluster.groupby('customer_state').sum().reset_index()

# Kategorisasi berdasarkan kuantil
bins = [df_cluster['order_item_id'].min(), 
        df_cluster['order_item_id'].quantile(0.33), 
        df_cluster['order_item_id'].quantile(0.66), 
        df_cluster['order_item_id'].max()]

labels = ['Low Sales Region', 'Medium Sales Region', 'High Sales Region']
df_cluster['Sales_Category'] = pd.cut(df_cluster['order_item_id'], bins=bins, labels=labels, include_lowest=True)

# Load batas wilayah Brasil
brazil_states = read_state()
# Gabungkan dengan data sales berdasarkan customer_state
brazil_states = brazil_states.merge(df_cluster, left_on='abbrev_state', right_on='customer_state', how='left')


st.subheader("Analisis Lanjutan: Pengelompokan Wilayah Berdasarkan Penjualan Menggunakan Metode Binning")
tab1, tab2 = st.tabs(["Distribusi Wilayah", "Bar Chart Penjualan"])

with tab1:    
    st.write(""" ##### Distribusi Penjualan Berdasarkan Wilayah """)
    m = folium.Map(location=[-14.235, -51.9253], zoom_start=5, max_zoom=7, min_zoom=4)
    
    choropleth = folium.Choropleth(
        geo_data=brazil_states,
        name='choropleth',
        data=brazil_states,
        columns=['abbrev_state', 'order_item_id'],
        key_on='feature.properties.abbrev_state',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Total Produk Terjual'
    ).add_to(m)
        
    for _, row in brazil_states.iterrows():
        if pd.notna(row['geometry']):
            centroid = row['geometry'].centroid
            folium.Marker(
                location=[centroid.y, centroid.x],
                icon=folium.DivIcon(html=f'<div style="font-size: 12px; font-weight: bold; color: black;">{int(row["order_item_id"])}</div>')
            ).add_to(m)    
    folium_static(m)

with tab2:        
    st.write(""" ##### Total Produk Terjual per Wilayah """)
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        x=df_cluster["customer_state"],
        y=df_cluster["order_item_id"],
        hue=df_cluster["Sales_Category"],
        palette=sns.color_palette("viridis", 3)
    )
    plt.xlabel("Wilayah")
    plt.ylabel("Total Produk Terjual")
    plt.title("Pengelompokan Wilayah Berdasarkan Penjualan")
    plt.xticks(rotation=45)
    plt.legend(title="Kategori Penjualan")
    plt.grid()            
    st.pyplot(plt)
