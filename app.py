import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import requests

def prepare_data(data, сity):
    city_data = data[data['city'] == сity]
    city_data['timestamp'] = pd.to_datetime(city_data['timestamp'])
    city_data.sort_values(by='timestamp', ascending=True, inplace=True)

    city_data['temperature_avg'] = city_data.groupby('season')['temperature'].transform(lambda row: row.mean())
    city_data['temperature_std'] = city_data.groupby('season')['temperature'].transform(lambda row: row.std())

    city_data['is_anomaly'] = (city_data['temperature'] > city_data['temperature_avg'] + 2 * city_data['temperature_std'])|(city_data['temperature'] < city_data['temperature_avg'] - 2 * city_data['temperature_std'])
    return city_data

def plot_data(city_data, city):
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_facecolor('white')
    sns.lineplot(data=city_data, x='timestamp', y='temperature', label='Температура', color='blue', ax=ax)

    sns.scatterplot(data=city_data[city_data['is_anomaly']],
                    x='timestamp',
                    y='temperature',
                    color='red',
                    label='Аномалии',
                    ax=ax)

    ax.axhline(y=temperature_min, color='blue', linestyle='--', label=f'Минимальная температура ({temperature_min:.1}°C)')
    ax.axhline(y=temperature_max, color='orange', linestyle='--', label=f'Максимальная температура ({temperature_max:.1f}°C)')
    ax.axhline(y=temperature_avg, color='green', linestyle='--', label=f'Средняя температура ({temperature_avg:.1f}°C)')

    ax.set_title(f'Температура города {city}')
    ax.set_xlabel('Дата')
    ax.set_ylabel('Температура')
    ax.legend()

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.tight_layout()
    st.pyplot(fig)
    #plt.show()

st.title("Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API")
st.header("Шаг 1: Загрузка данных")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=['csv'])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.dataframe(data.head())

if uploaded_file is not None:
    st.header("Шаг 2: Выбор города")
    сity_list = data['city'].unique()
    city = st.selectbox("Выберите город", ["Список городов"] + list(сity_list))

if uploaded_file is not None:
    st.header("Шаг 3: Описательная статистика")
    if st.checkbox("Показать статистику:"):
        st.write(data[data['city'] == city].describe(include='all'))

if uploaded_file is not None:

    st.header("Шаг 4: Получение текущей температуры")
    api_key = st.text_input("Введите Ваш API key:")

    if not api_key:
        st.warning("API key отсутствует")
    if api_key:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city,
                  "appid": api_key,
                  "units": "metric"}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            df = response.json()
            temperature = df["main"]["temp"]
            time = df["sys"]["sunrise"]
            season = pd.to_datetime(time, unit='s').month

            st.header(f"Шаг 5: Визуализация статистики по температуре в городе {city}")
            city_data = prepare_data(data, city)
         
            temperature_min = city_data['temperature'].min()
            temperature_max = city_data['temperature'].max()
            temperature_avg = city_data['temperature'].mean()

            plot_data(city_data, city)

            city_data = city_data[city_data["timestamp"].dt.month == season]

            min = city_data.iloc[0]['temperature_avg'] - 2 * city_data.iloc[0]['temperature_std']
            max = city_data.iloc[0]['temperature_avg'] + 2 * city_data.iloc[0]['temperature_std']
            st.write(f"Текущая температура: {temperature}")

            if min <= temperature <= max:
                st.write(f"Температура в пределах средних значений")
                st.write(f"Средняя температура: {temperature_min:.2f}")
            else:
                st.write(f"Температура аномальна")
                st.write(f"Средняя температура: {temperature_min:.2f}")