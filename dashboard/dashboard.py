import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    
    categories = df['product_category_name_english'].unique()
    selected_category = st.selectbox("Pilih Kategori Produk", options=categories)

    category_data = filtered_data[filtered_data['product_category_name_english'] == selected_category]
    
    top_products = category_data.groupby('product_id')['order_item_id'].sum().reset_index()
    top_products = top_products.sort_values(by='order_item_id', ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='order_item_id', y='product_id', data=top_products, palette='Blues_r')
    plt.xlabel('Jumlah Produk Terjual')
    plt.ylabel('Product ID')
    plt.title(f'Top 10 Produk Terlaris dalam Kategori {selected_category}')
    st.pyplot(plt)

    st.write(f"Top 10 produk terlaris dalam kategori '{selected_category}':")
    st.write(top_products)

with tab2:    
    st.write(""" ##### Berdasarkan Pendapatan Produk """)

    selected_category_rev = st.selectbox("Pilih Kategori Produk untuk Analisis Pendapatan", options=categories)
    category_data_rev = filtered_data[filtered_data['product_category_name_english'] == selected_category_rev]

    category_data_rev['revenue'] = category_data_rev['price'] * category_data_rev['order_item_id']
    revenue_data = category_data_rev.groupby('product_id')['revenue'].sum().reset_index()
    revenue_data = revenue_data.sort_values(by='revenue', ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='revenue', y='product_id', data=revenue_data, palette='viridis')
    plt.xlabel('Pendapatan')
    plt.ylabel('Product ID')
    plt.title(f'Top 10 Produk dengan Pendapatan Tertinggi dalam Kategori {selected_category_rev}')
    st.pyplot(plt)

    st.write(f"Top 10 produk dengan pendapatan tertinggi dalam kategori '{selected_category_rev}':")
    st.write(revenue_data)


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



st.subheader("Total Penjualan Produk per Wilayah")

state_mapping = {
    'BA': 'Bahia',
    'DF': 'Distrito Federal',
    'SP': 'São Paulo',
    'RJ': 'Rio de Janeiro',
    'MG': 'Minas Gerais',
    'RS': 'Rio Grande do Sul',
    'PR': 'Paraná',
    'SC': 'Santa Catarina',
    'PE': 'Pernambuco',
    'CE': 'Ceará',
}

region_sales_data = filtered_data.copy()
total_sales_by_state = region_sales_data.groupby('customer_state')['order_item_id'].sum().reset_index()
total_sales_by_state['customer_state'] = total_sales_by_state['customer_state'].map(state_mapping)
top_states_sales = total_sales_by_state.sort_values(by='order_item_id', ascending=False)

fig, ax = plt.subplots(figsize=(14, 7))
sns.barplot(data=top_states_sales, x='customer_state', y='order_item_id', palette='viridis')
plt.xlabel('Wilayah Pengiriman', fontsize=12)
plt.ylabel('Total Produk Terjual', fontsize=12)
plt.title('Total Penjualan Produk per Wilayah Pengiriman', fontsize=14, fontweight='bold')

for p in ax.patches:
    ax.annotate(f'{p.get_height():,.0f}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                fontsize=12, color='black', 
                xytext=(0, 9), textcoords='offset points')

st.pyplot(fig)

