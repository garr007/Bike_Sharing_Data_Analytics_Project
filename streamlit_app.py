import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='darkgrid')


def create_by_season_df(df):
    by_season_df = df.groupby(by='season').cnt.sum().reset_index()
    by_season_df['season'] = by_season_df['season'].replace({
        1: 'Springer',
        2: 'Summer',
        3: 'Fall',
        4: 'Winter'
    })
    by_season_df.rename(columns={'cnt': 'total_rent'}, inplace=True)
    return by_season_df


def create_by_weathersit(df):
    by_weather_df = df.groupby(by='weathersit').cnt.sum().reset_index()
    by_weather_df.rename(columns={'cnt': 'total_rent'}, inplace=True)
    return by_weather_df

def create_by_hour_group(df):
    df['hour_group'] = df['hr'].apply(
        lambda x: 'Early Morning' if 0 <= x < 6 else
        ('Morning' if 6 <= x < 12 else ('Noon' if 12 <= x < 15 else (
            'Afternoon' if 15 <= x < 19 else 'night'))))

    by_hour_group_df = df.groupby(by='hour_group').cnt.sum().reset_index()
    by_hour_group_df.rename(columns={'cnt': 'total_rent'}, inplace=True)
    return by_hour_group_df


def create_daily_rented_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    daily_rented_df = df.resample(rule='D', on='dteday').agg({
        'cnt':
        'sum',
        'casual':
        'sum',
        'registered':
        'sum',
        'workingday':
        'sum'
    })
    daily_rented_df = daily_rented_df.reset_index()
    daily_rented_df.rename(columns={'cnt': 'total_rent'}, inplace=True)
    return daily_rented_df


def create_year_month_df(df):
    df['year_month'] = df['dteday'].dt.to_period('M')
    year_month_df = df.groupby('year_month').cnt.sum().reset_index()
    year_month_df.rename(columns={'cnt': 'total_rent'}, inplace=True)
    return year_month_df


day_df = pd.read_csv('day_data.csv')
hour_df = pd.read_csv('hour_data.csv')
hour_df.head()

day_df.sort_values(by='dteday', inplace=True)
day_df.reset_index(inplace=True)
for column in day_df['dteday']:
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

with st.sidebar:
    st.image("bicycle.png", width=250)

    start_date, end_date = st.date_input(label='Choose a Range Date',
                                         min_value=min_date,
                                         max_value=max_date,
                                         value=[min_date, max_date])

main_df = day_df[(day_df['dteday'] >= str(start_date))
                 & (day_df['dteday'] <= str(end_date))]

main_hour_df = hour_df[(hour_df['dteday'] >= str(start_date))
                       & (hour_df['dteday'] <= str(end_date))]

daily_rented_df = create_daily_rented_df(main_df)
by_season_df = create_by_season_df(day_df)
by_weather_df = create_by_weathersit(day_df)
by_hour_df = create_by_hour_group(main_hour_df)
year_month_df = create_year_month_df(day_df)

st.header('Bike Sharing Dashboard 🚴‍♂️')
st.text(f'📅 Date Range: {start_date} - {end_date} 📅')
st.subheader('Daily Bike Rentals')

total_rent = daily_rented_df.total_rent.sum()
st.metric('Total Rent', value=total_rent)

#All Rent
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(daily_rented_df['dteday'],
        daily_rented_df['total_rent'],
        marker='o',
        linewidth=1,
        markersize=4,
        color="#1f77b4")
ax.set_xlabel(None)
ax.set_ylabel('Number of Rentals', fontsize=15)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

#Working day and non Working day
st.subheader('Exploring the Dynamics: Working Days vs Non-Working Days')
col1, col2 = st.columns(2)
with col1:
    total_workingday_rent = daily_rented_df[daily_rented_df['workingday'] ==
                                            1]['total_rent'].sum()
    st.metric('Total Working day Rentals', value=total_workingday_rent)
with col2:
    total_non_workingday_rent = daily_rented_df[daily_rented_df['workingday']
                                                == 0]['total_rent'].sum()
    st.metric('Total Non-Working Day Rentals', value=total_non_workingday_rent)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(daily_rented_df[daily_rented_df['workingday'] == 1]['dteday'],
        daily_rented_df[daily_rented_df['workingday'] == 1]['total_rent'],
        label='Working Day',
        color='red')
ax.plot(daily_rented_df[daily_rented_df['workingday'] == 0]['dteday'],
        daily_rented_df[daily_rented_df['workingday'] == 0]['total_rent'],
        label='Non-Working Day',
        color='green')

ax.set_xlabel(None)
ax.set_ylabel('Number of Rentals', size=15)
ax.legend(title='Day Type', loc='upper left')

st.pyplot(fig)

#casual vs registered
st.subheader('Total Casual vs Registered Rentals Overview')
col1, col2 = st.columns(2)
with col1:
    total_casual_rent = daily_rented_df.casual.sum()
    st.metric('Total Casual Rentals', value=total_casual_rent)

with col2:
    total_registered_rent = daily_rented_df.registered.sum()
    st.metric('Total Registered Rentals', value=total_registered_rent)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(daily_rented_df['dteday'],
        daily_rented_df['casual'],
        color='#ff7f0e',
        label='Casual')
ax.plot(daily_rented_df['dteday'],
        daily_rented_df['registered'],
        color='#1f77b4',
        label='Registered')
ax.set_xlabel(None)
ax.set_ylabel('Number of Rentals', size=15)

ax.legend(title='User Type', loc='upper left', labels=['Casual', 'Registered'])
st.pyplot(fig)

#byhour group
st.subheader('Bike Rental Trends across the Day')
fig, ax = plt.subplots(figsize=(12, 5))
colors = ["#FF5733", "#3498db", "#3498db", "#3498db", "#3498db"]
sns.barplot(x="total_rent",
            y="hour_group",
            data=by_hour_df.sort_values(by="total_rent", ascending=False),
            palette=colors,
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8,
            ax=ax)
ax.set_ylabel(None)
ax.set_xlabel("Number of Rentals")
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

#By Season
st.subheader('Number of Rented Bikes by Season')
fig, ax = plt.subplots(figsize=(12, 5))
colors = "#3498db"
colors = ["#FF5733", "#3498db", "#3498db", "#3498db", "#3498db"]
sns.barplot(y='total_rent',
            x='season',
            data=by_season_df.sort_values(by='total_rent', ascending=False),
            palette=colors,
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8,
            ax=ax)

ax.set_ylabel('Number of Rentals (Million)')
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

#By Weather
st.subheader('Percentage Distribution of Bike Rentals by Weather Conditions')
fig, ax = plt.subplots(figsize=(12, 5))
weather_counts = day_df.groupby(by='weathersit').cnt.sum().sort_values(
    ascending=False)
colors = ('#93C572', '#C4C1A4', '#8B4513')
explode = (0, 0, 0)
labels = {
    1: 'Clear',
    2: 'Mist',
    3: 'Snow/Rain',
}

labels_list = [labels[weather] for weather in by_weather_df['weathersit']]

ax.pie(x=weather_counts,
       labels=labels_list,
       autopct='%1.1f%%',
       colors=colors,
       explode=explode,
       textprops={
           'fontsize': 14,
       })

st.pyplot(fig)

#Best and Worst Month
st.subheader('Best and Worst Month by Number of Rented')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
colors = ["#FF5733", "#3498db", "#3498db", "#3498db", "#3498db"]
sns.barplot(x='total_rent',
            y='year_month',
            data=year_month_df.sort_values(by='total_rent',
                                           ascending=False).head(3),
            palette=colors,
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8,
            ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Month", loc="center", fontsize=20)
ax[0].tick_params(axis='y', labelsize=12)

sns.barplot(x='total_rent',
            y='year_month',
            data=year_month_df.sort_values(by='total_rent',
                                           ascending=True).head(3),
            palette=colors,
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8,
            ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Month", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=12)
st.pyplot(fig)

#Temp and Count Correlation
st.subheader('Exploring the Temperature Impact on Bike Rental Numbers')
fig, ax = plt.subplots(figsize=(12, 5))
sns.scatterplot(x='temp', y='cnt', data=day_df)
ax.set_xlabel('Temperature (normalized)')
ax.set_ylabel(None)
st.pyplot(fig)
correlation_coefficient = day_df['temp'].corr(day_df['cnt'])
st.text(
    f"The Correlation Coefficient between Temperature and Bike Rental: {correlation_coefficient:.2f}"
)

correlation_coefficient = day_df['temp'].corr(day_df['cnt'])

