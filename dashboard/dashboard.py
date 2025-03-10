import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# path kalo run deploy
# df = pd.read_csv('dashboard/full_data.csv')

# path kalo run local
df = pd.read_csv('full_data.csv')

df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

st.sidebar.header("Filter")
years = df['order_purchase_timestamp'].dt.year.unique()
selected_years = st.sidebar.multiselect('Pilih Tahun', options=years, default=list(years))

filtered_data = df[df['order_purchase_timestamp'].dt.year.isin(selected_years)]
filtered_data['revenue'] = filtered_data['price'] * filtered_data['order_item_id']
total_revenue = filtered_data['revenue'].sum()
total_reviews = filtered_data['review_score'].sum()
total_products_sold = filtered_data['order_item_id'].sum()

st.title("Analisis Data E-commerce Public Dataset")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Pendapatan", value=f"Rp {total_revenue:,.0f}")

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

    filtered_data['revenue'] = filtered_data['price'] * filtered_data['order_item_id']
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
    

# Dictionary Mapping Kode Wilayah ke Nama Lengkap
state_mapping = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins"
}

df_cluster = df[['customer_state', 'order_item_id']].copy()
df_cluster = df_cluster.groupby('customer_state').sum().reset_index()

# df_cluster['customer_state'] = df_cluster['customer_state'].map(state_mapping)

# Binning berdasarkan aturan bisnis
bins = [df_cluster['order_item_id'].min(), 
        df_cluster['order_item_id'].quantile(0.33), 
        df_cluster['order_item_id'].quantile(0.66), 
        df_cluster['order_item_id'].max()]

labels = ['Low Sales Region', 'Medium Sales Region', 'High Sales Region']
df_cluster['Sales_Category'] = pd.cut(df_cluster['order_item_id'], bins=bins, labels=labels, include_lowest=True)

st.subheader("Analisis Lanjutan: Pengelompokan Wilayah Berdasarkan Penjualan Menggunakan Metode Binning")

tab1, tab2 = st.tabs(["Bar Chart Penjualan", "Distribusi Wilayah"])
with tab1:    
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

with tab2:        
    st.write(""" ##### Distribusi Penjualan Berdasarkan Wilayah """)
    plt.figure(figsize=(12, 6))
    sns.scatterplot(
        x=df_cluster["customer_state"],
        y=df_cluster["order_item_id"],
        hue=df_cluster["Sales_Category"],
        palette=sns.color_palette("viridis", 3),
        s=100
    )
    plt.xlabel("Wilayah")
    plt.ylabel("Total Produk Terjual")
    plt.title("Scatter Plot Distribusi Penjualan per Wilayah")
    plt.xticks(rotation=45)
    plt.legend(title="Kategori Penjualan")
    plt.grid()
    st.pyplot(plt)
