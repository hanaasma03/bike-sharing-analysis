import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard_Hana Asma Nabila", layout="centered", initial_sidebar_state="expanded")

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "registered": "sum",
        "casual": "sum"
    }).reset_index()
    return daily_orders_df

def create_monthly_trend_mean_df(df):
    monthly_trend = df.groupby(['yr', 'mnth']).agg({"cnt": "mean"}).reset_index()
    month_names = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                   'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    monthly_trend['month_label'] = monthly_trend['mnth'].apply(lambda x: month_names[x-1])
    return monthly_trend

def create_sum_order_items_df(hour_df):
    sum_order_items_df = hour_df.groupby("hr").cnt.mean().reset_index()
    return sum_order_items_df

def create_workingday_df(df):
    # Mengelompokkan berdasarkan workingday (1: Kerja, 0: Libur/Weekend)
    workingday_df = df.groupby(by="workingday").cnt.mean().reset_index()
    # Mengganti angka 0 & 1 menjadi teks agar jelas di grafik
    workingday_df['day_type'] = workingday_df['workingday'].apply(lambda x: 'Hari Kerja' if x == 1 else 'Hari Libur')
    return workingday_df

def create_season_analysis_df(df):
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    season_df = df.groupby("season").cnt.mean().reset_index()
    season_df['season_label'] = season_df['season'].map(season_map)
    return season_df

def create_temp_binning_df(df):
    df['temp_bin'] = pd.cut(df['temp'], bins=[0, 0.4, 0.7, 1], labels=['Rendah', 'Sedang', 'Tinggi'])
    temp_bin_df = df.groupby('temp_bin', observed=True).cnt.mean().reset_index()
    return temp_bin_df

# Fungsi Load Data
@st.cache_data
def load_data():
    # Pastikan nama file ini sama persis (huruf kecil/besar) dengan di GitHub
    day_df = pd.read_csv("day_clean.csv")
    hour_df = pd.read_csv("hour_clean.csv")
    
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    return day_df, hour_df

day_df, hour_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://url-shortener.me/LLOJ")
    st.title("Bike Sharing 🚴")
    st.markdown("Dashboard penyewaan sepeda tahun 2011-2012")
    st.markdown("---")
    
    # Mengambil tanggal min & max
    min_date = day_df["dteday"].min().date()
    max_date = day_df["dteday"].max().date()

    st.subheader("📊 Filter Data")
   
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Tanggal Mulai", value=min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("Tanggal Selesai", value=max_date, min_value=min_date, max_value=max_date)

    st.markdown("---")
    st.info(f"Analyst: **Hana Asma Nabila**")

# --- LOGIKA FILTER ---
# Memfilter data harian 
main_df = day_df[(day_df["dteday"] >= pd.to_datetime(start_date)) & 
                (day_df["dteday"] <= pd.to_datetime(end_date))]
# Memnfilter data jam 
main_hour_df = hour_df[(hour_df["dteday"] >= pd.to_datetime(start_date)) & 
                      (hour_df["dteday"] <= pd.to_datetime(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
trend_mean_df = create_monthly_trend_mean_df(main_df)
hour_mean_df = create_sum_order_items_df(main_hour_df)
workingday_df = create_workingday_df(main_df)
season_df = create_season_analysis_df(main_df)
temp_bin_df = create_temp_binning_df(main_df)

st.title('🚴 Bike Sharing Dashboard 🚴')

st.caption("""
           Dashboard ini menampilkan analisis penyewaan sepeda berdasarkan: 
           - Jenis hari 
           - Pengaruh suhu
           - Tren bulanan
           - Pola waktu selama tahun 2012
           """)

st.markdown(
    f"""
    <div style="background-color: #e1f5fe; padding: 10px; border-radius: 10px; border: 1px solid #b3e5fc;">
        <p style="margin: 0; color: #01579b; font-weight: bold;">
            Menampilkan data {start_date} hingga {end_date}
        </p>
    </div>
    <br>
    """, 
    unsafe_allow_html=True
)

st.header("Daily Orders Summary")
m1, m2, m3 = st.columns(3)

with m1:
    total_rentals = daily_orders_df['cnt'].sum()
    st.metric("Total Rentals", value=f"{total_rentals:,}")

with m2:
    total_registered = daily_orders_df['registered'].sum()
    st.metric("Total Registered", value=f"{total_registered:,}")

with m3:
    total_casual = daily_orders_df['casual'].sum()
    st.metric("Total Casual", value=f"{total_casual:,}")

st.markdown("---")

# --- PERBANDINGAN PENYEWAAN SEPEDA ---

st.header("Perbandingan Rata-rata Penyewaan: Hari Kerja vs Hari Libur")

fig4, ax4 = plt.subplots(figsize=(16, 10))
sns.barplot(
    x='day_type', 
    y='cnt', 
    data=workingday_df, 
    palette=['#FC4F4F', "#3781B5"], 
    ax=ax4
)

for p in ax4.patches:
    ax4.annotate(f'{p.get_height():.2f}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha = 'center', va = 'center', 
                xytext = (0, 10), 
                textcoords = 'offset points',
                fontsize=12)

ax4.set_title("Perbandingan Penyewaan Sepeda", fontsize=25)
ax4.set_xlabel("Jenis Hari", fontsize=22)
ax4.set_ylabel("Rata-rata Jumlah Sewa", fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
st.pyplot(fig4)

with st.expander("Insight:"):
    st.markdown("""
    Rata-rata penyewaan sepeda pada hari kerja cenderung lebih tinggi dibandingkan pada hari libur.
    Hal ini menunjukkan bahwa, sepeda banyak digunakan sebagai penunjang alat transportasi untuk kerja.
    """)

st.markdown("---")

# --- TREN PENYEWAAN SEPEDA ---
st.header("Tren Penyewaan Sepeda")

# Tren jumlah penyewaan 2011-2012
st.subheader("Tren Penyewaan Bulanan (2011-2012)")
monthly_all_df = main_df.resample(rule='M', on='dteday').agg({"cnt": "sum"}).reset_index()
monthly_all_df['month_year'] = monthly_all_df['dteday'].dt.strftime('%Y-%m')

fig_all, ax_all = plt.subplots(figsize=(16, 10))
ax_all.plot(monthly_all_df['month_year'], monthly_all_df['cnt'], marker='o', linewidth=3, color='#2B3467', markersize=15)
ax_all.set_title("Total Penyewaan per Bulan (2011-2012)", fontsize=25, pad=25)
ax_all.set_xlabel("Bulan", fontsize=22)
ax_all.set_ylabel("Jumlah Penyewaan Sepeda", fontsize=22)
plt.xticks(rotation=45, fontsize=18)
plt.yticks(fontsize=18)
ax_all.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
st.pyplot(fig_all)

# Tren rata-rata penyewaan 2011
st.subheader("Tren Rata-rata Penyewaan Tahun 2011")
t11 = trend_mean_df[trend_mean_df['yr'] == 0]

if not t11.empty:
    f1, a1 = plt.subplots(figsize=(13, 7))
    a1.plot(t11['month_label'], t11['cnt'], marker='o', color='#3F72AF', linewidth=3, markersize=10)
    a1.fill_between(t11['month_label'], t11['cnt'], color='#3F72AF', alpha=0.1)
    a1.set_title("Rata-rata Penyewaan Sepeda per Bulan (2011)", fontsize=22)
    a1.set_xlabel("Bulan", fontsize=20)
    a1.set_ylabel("Rata-rata Penyewaan Sepeda", fontsize = 20)
    plt.xticks(rotation=45, fontsize=18)
    plt.yticks(fontsize=18)
    a1.grid(True, alpha=0.5)
    plt.tight_layout()
    st.pyplot(f1)
else:
    st.info("Data tahun 2011 tidak tersedia untuk rentang waktu yang dipilih.")

# Rata-rata penyewaan 2012
st.subheader("Tren Rata-rata Penyewaan Tahun 2012")
t12 = trend_mean_df[trend_mean_df['yr'] == 1]

if not t12.empty:
    f2, a2 = plt.subplots(figsize=(13, 7))
    a2.plot(t12['month_label'], t12['cnt'], marker='o', color='#3F72AF', linewidth=3, markersize=10)
    a2.fill_between(t12['month_label'], t12['cnt'], color='#3F72AF', alpha=0.1)
    a2.set_title("Rata-rata Penyewaan Sepeda per Bulan (2012)", fontsize=22)
    a2.set_xlabel("Bulan", fontsize=20)
    a2.set_ylabel("Rata-rata Penyewaan Sepeda", fontsize=20)
    plt.xticks(rotation=45, fontsize=18)
    plt.yticks(fontsize=18)
    a2.grid(True, alpha=0.5)
    plt.tight_layout()
    st.pyplot(f2)
else:
    st.info("Data tahun 2012 tidak tersedia untuk rentang waktu yang dipilih.")

with st.expander("Insight:"):
    st.markdown("""
    **Analisis Tren:**
    * Dapat dilihat bahwa rata-rata penyewaan sepeda membentuk pola musiman
    * Pada tahun 2011 maaupun 2012, rata-rata penyewaan sepeda cenderung meningkat hingga pertengahan tahun
    """) 

st.markdown("---")

# --- RATA-RATA PENYEWAAN SEPEDA PADA HARI KERJA (2012)--- 
st.header("🕒 Pola Jam Sibuk Tahun 2012")
peak_hour = hour_mean_df.loc[hour_mean_df['cnt'].idxmax(), 'hr']
peak_value = hour_mean_df['cnt'].max()

fig3, ax3 = plt.subplots(figsize=(12, 6))
ax3.fill_between(hour_mean_df['hr'], hour_mean_df['cnt'], color='#00ADB5', alpha=0.15)
sns.lineplot(
    x='hr', 
    y='cnt', 
    data=hour_mean_df, 
    color='#00ADB5', 
    linewidth=3, 
    marker='o', 
    markersize=10, 
    ax=ax3
)

ax3.axvline(x=peak_hour, color='#FC4F4F', linestyle='--', alpha=0.7)
ax3.annotate(f'Puncak: Jam {int(peak_hour)}', 
             xy=(peak_hour, peak_value), 
             xytext=(peak_hour + 1, peak_value),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
             fontsize=12,
             fontweight='bold')

ax3.set_xticks(range(0, 24))
ax3.set_xlabel("Jam", fontsize=15)
ax3.set_ylabel("Rata-rata Penyewaan", fontsize=15)
ax3.set_title("Rata-rata Penyewaan Pada Hari Kerja (2012)", fontsize=22, pad=20)

ax3.grid(False)
sns.despine(left=False, bottom=False)

plt.tight_layout()
st.pyplot(fig3)

with st.expander("Insight"):
    st.markdown("""
    Puncak penyewaan sepeda terjadi pada jam 17. Namun, pada jam 8 rata-rata sewa terjadi peningkatan yang signifikan.
    Pada jam 2-4 dini hari menunjukkan bahwa penyewaan sangat rendah. Hal ini berarti, sepeda banyak disewa pada jam sibuk (berangkat/pulang kerja)
    """) 

st.markdown("---")

# --- ANALISIS PENGARUH SUHU DAN MUSIM ---
st.header("Analisis Pengaruh Musim & Suhu")
col_a, col_b = st.columns(2)

with col_a:
    st.write("**Rata-rata Sewa Berdasarkan Musim**")
    fig_s, ax_s = plt.subplots()
    sns.barplot(x='season_label', y='cnt', data=season_df, palette='Blues', ax=ax_s)
    ax_s.set_xlabel("Musim", fontsize=15)
    ax_s.set_ylabel("Rata-rata sewa", fontsize=15)
    st.pyplot(fig_s)

with col_b:
    st.write("**Rata-rata Sewa Berdasarkan Kategori Suhu**")
    fig_t, ax_t = plt.subplots()
    sns.barplot(x='temp_bin', y='cnt', data=temp_bin_df, palette='coolwarm', ax=ax_t)
    ax_t.set_xlabel("Suhu", fontsize=15)
    ax_t.set_ylabel("Rata-rata sewa", fontsize=15)
    st.pyplot(fig_t)

with st.expander("Insight"):
    st.markdown("""
    Berdasarkan grafik tersebut, dapat dilihat bahwa suhu dan musim memengaruhi rata-rata sewa, 
    di mana pada saat kondisi suhu yang rendah atau pada musim dingin tidak mendukung untuk aktivitas
    bersepeda, dan sebaliknya.
    """) 

st.markdown("---")

st.caption('Copyright (c) Hana Asma Nabila 2026')
