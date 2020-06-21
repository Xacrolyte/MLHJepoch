from covid_india import states
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import plotly_express as px
import requests
from bs4 import BeautifulSoup
import seaborn as sns

rcParams.update({'figure.autolayout': True})

SUBHEAD_TITLE = "COVID-19 Dashboard and Vulnerability Analysis"
SUBHEAD_CREDITS = "Made by Epochalypse Team for HackJaipur 2020"

def get_ui_for_data(data_input):
    column_properties = "margin:3%; float:right; width:15%; text-align: right"
    base_card_styling = "margin:1%; padding:1%; " \
                        "text-align:center;" \
                        "width:16%; " \
                        "box-shadow:0 4px 8px 0 rgba(0,0,0,0.2);"
    return f"<div class='row'>" \
           f"<h5 style='color:black; {column_properties}'>{data_input[0]}</h5>" \
           f"<h5 style='color:blue; {base_card_styling}'><h6>Total</h6>{data_input[1]}</h5> " \
           f"<h5 style='color:red; {base_card_styling}'><h6>Active</h6>{data_input[2]}</h5> " \
           f"<h5 style='color:green; {base_card_styling}'><h6>Saved</h6>{data_input[3]}</h5> " \
           f"<h5 style='color:orange; {base_card_styling}'><h6>Deaths</h6>{data_input[4]}</h5> " \
           f"</div>"

@st.cache
def load_global_death_data():
   data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv', error_bad_lines=False)
   data.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
   data = data.groupby(['Country/Region']).sum()
   return data

def date_convert(df):
    df_tran = df.transpose().reset_index()
    df_tran.rename({'index': 'Date'}, axis=1, inplace=True)
    df_tran['Date'] =  pd.to_datetime(df_tran['Date'])
    return df_tran

def tidy_death_data(df,group):
    df_tidy = pd.melt(df, id_vars=['Date'])
    df_tidy.drop(df_tidy[df_tidy['value'] < 10].index, inplace=True) # Drop all dates and countries with less than 10 recorded deaths
    df_tidy = df_tidy.assign(Days=df_tidy.groupby(group).Date.apply(lambda x: x - x.iloc[0]).dt.days) # Calculate # of days since 10th death by country
    df_tidy['daily_change'] = df_tidy.sort_values([group,'Days']).groupby(group)['value'].diff()
    df_tidy['daily_pct_change'] = df_tidy.sort_values([group,'Days']).groupby(group)['value'].pct_change() * 100
    df_tidy['daily_roll_avg'] = df_tidy.groupby(group)['daily_change'].rolling(7).mean().round().reset_index(0,drop= True)
    df_tidy['daily_pctchange_roll_avg'] = df_tidy.groupby(group)['daily_pct_change'].rolling(7).mean().round().reset_index(0,drop= True)
    df_tidy['daily_change'].fillna(0, inplace=True)
    df_tidy['daily_pct_change'].fillna(0, inplace=True)
    df_tidy['daily_roll_avg'].fillna(df_tidy['daily_change'], inplace=True)
    df_tidy['daily_pctchange_roll_avg'].fillna(df_tidy['daily_pct_change'], inplace=True)
    return df_tidy

def global_plot_create(data, x, y, title, xaxis, yaxis):
    fig = px.line(data, x=x, y=y, color='Country/Region', width=800, height=600)
    fig.update_layout(title=title, 
                      xaxis_title= xaxis, 
                      yaxis_title = yaxis,
                      legend_title_text='Countries',
                      yaxis_type="log", 
                      yaxis_tickformat = 'f',
                      xaxis_gridcolor = 'LightBlue',
                      yaxis_gridcolor = 'LightBlue',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    return fig    

def load_data_and_return_dataframe():
    all_cases = states.getdata()
    data = []
    for state in all_cases:
        temp = []
        temp.append(state)
        for key in all_cases[state]:
            temp.append(all_cases[state][key])
        data.append(temp)
    return pd.DataFrame(data, columns=["State", "Total", "Active", "Cured", "Death"])

df = load_data_and_return_dataframe()
def main():
    page = st.sidebar.selectbox("Choose a feature", ['Homepage', 'Global' ,'INDIA', 'Map Visualization'])

    if page == 'Homepage':
        st.title("COVID-19 Dashboard")
        st.header("Exploration of COVID-19 related deaths around the world")
        st.subheader("Use the Selection Panel on the left sidebar, to navigate to respective features available.")
        st.markdown("This is a Covid-19 Dashboard, made purely using Python and Streamlit. Streamlit makes it super easy to make any sort of Python apps like Machine Learning and Data Science Apps.")
        st.write("We have explored the Indian as well Global representation of Covid-related statistics and the effects of the pandemic since January 2020.")
        st.subheader("Contributing:")
        st.markdown("The project is Open-Sourced on [GitHub](https://github.com/Xacrolyte/MLHJepoch), under the MIT Licence. Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.")

    elif page == 'Global':
        global_data = load_global_death_data()
        global_data = date_convert(global_data)
        global_deaths = tidy_death_data(global_data, group = 'Country/Region')

        st.title('Global COVID-19 Deaths')
        st.header('Daily COVID-19 deaths, sorted by country, from Jan 22, 2020 - Present.')
        st.write("Raw Data:", global_data)

        cols = list(global_data[global_data.columns.difference(['Date'])])
        countries = st.multiselect('Select countries to display', cols, ["US", "India", "China"])

        global_deaths.set_index('Country/Region', inplace=True)
        data_plot = global_deaths.loc[countries] 
        data_plot.reset_index(inplace=True)

        cols = ['Total Confirmed Deaths', 'Deaths per Day','Daily Percentage Change']
        variable = st.selectbox('Select Statistic to be displayed:', cols)

        if variable == 'Total Confirmed Deaths':
            fig=global_plot_create(data = data_plot, 
                        x = 'Days',
                        y = 'value',
                        title = 'Global COVID-19 Deaths - Total',
                        xaxis = 'Number of days since 10th death',
                        yaxis = 'Confirmed Deaths')
            st.plotly_chart(fig)

        elif variable == 'Deaths per Day':
            fig=global_plot_create(data = data_plot, 
                        x = 'Days',
                        y = 'daily_roll_avg',
                        title = 'Average death rate worldwide',
                        xaxis = 'Number of days',
                        yaxis = 'Average Deaths')
            st.plotly_chart(fig)

        elif variable == 'Daily Percentage Change':
            fig=global_plot_create(data = data_plot, 
                        x = 'Days',
                        y = 'daily_pctchange_roll_avg',
                        title = 'Daily percentage change globally',
                        xaxis = 'Number of days',
                        yaxis = 'Change in percentage')
            st.plotly_chart(fig)

    elif page == 'INDIA':
        st.title("COVID19 India DashBoard")
        st.header("COVID19 Dashboard made using Python and Streamlit")
        st.subheader("Check any State Status")
        sel_state = st.multiselect(label="Select State", options=df["State"])
        if sel_state:
            states = []
            for c in sel_state:
                states.append(df[df["State"] == c].values)
            for arr in states:
                data = arr[0]
                st.markdown(get_ui_for_data(data), unsafe_allow_html=True)

        st.markdown("<h2>Top 10 States affected</h2>", unsafe_allow_html=True)
        top_10 = df.nlargest(10, ["Total"])
        fig = go.Figure(data = [
            go.Bar(name="Total", x=top_10["State"], y=top_10["Total"]),
            go.Bar(name="Active", x=top_10["State"], y=top_10["Active"]),
            go.Bar(name="Cured", x=top_10["State"], y=top_10["Cured"]),
            go.Bar(name="Deaths", x=top_10["State"], y=top_10["Death"])
        ])
        st.plotly_chart(fig, use_container_width=True)

        for data in df.nlargest(10, ["Total"]).values:
            st.markdown(get_ui_for_data(data), unsafe_allow_html=True)

        st.markdown("<h3> All States Data</h3>", unsafe_allow_html=True)
        st.dataframe(df.style.background_gradient(cmap='Blues',subset=["Total"])\
                        .background_gradient(cmap='Reds',subset=["Active"])\
                        .background_gradient(cmap='Greens',subset=["Cured"])\
                        .background_gradient(cmap='Purples',subset=["Death"]))

        locations = {
        "Kerala" : [10.8505,76.2711],
        "Maharashtra" : [19.7515,75.7139],
        "Karnataka": [15.3173,75.7139],
        "Telangana": [18.1124,79.0193],
        "Uttar Pradesh": [26.8467,80.9462],
        "Rajasthan": [27.0238,74.2179],
        "Gujarat":[22.2587,71.1924],
        "Delhi" : [28.7041,77.1025],
        "Punjab":[31.1471,75.3412],
        "Tamil Nadu": [11.1271,78.6569],
        "Haryana": [29.0588,76.0856],
        "Madhya Pradesh":[22.9734,78.6569],
        "Jammu and Kashmir":[33.7782,76.5762],
        "Ladakh": [34.1526,77.5770],
        "Andhra Pradesh":[15.9129,79.7400],
        "West Bengal": [22.9868,87.8550],
        "Bihar": [25.0961,85.3131],
        "Chhattisgarh":[21.2787,81.8661],
        "Chandigarh":[30.7333,76.7794],
        "Uttarakhand":[30.0668,79.0193],
        "Himachal Pradesh":[31.1048,77.1734],
        "Goa": [15.2993,74.1240],
        "Odisha":[20.9517,85.0985],
        "Andaman and Nicobar Islands": [11.7401,92.6586],
        "Puducherry":[11.9416,79.8083],
        "Manipur":[24.6637,93.9063],
        "Mizoram":[23.1645,92.9376],
        "Assam":[26.2006,92.9376],
        "Meghalaya":[25.4670,91.3662],
        "Tripura":[23.9408,91.9882],
        "Arunachal Pradesh":[28.2180,94.7278],
        "Jharkhand" : [23.6102,85.2799],
        "Nagaland": [26.1584,94.5624],
        "Sikkim": [27.5330,88.5122],
        "Dadra and Nagar Haveli":[20.1809,73.0169],
        "Lakshadweep":[10.5667,72.6417],
        "Daman and Diu":[20.4283,72.8397]    
        }
        map_data = pd.DataFrame.from_dict(locations, orient='index',
                                columns=['latitude','longitude'])
        st.map(map_data)
        st.write("Raw Data:", df)

    elif page == 'Map Visualization':
        st.title("Global Map Live Visualization")
        st.header("Please drag the pointer over the map to scroll. Hover over a region for related info:")
        st.header("Scroll-Down for Zoom-Out; Scroll-Up for Zoom-In")
        from datetime import date, timedelta

        today = date.today()
        yesterday = today - timedelta(days=1)

        d1 = yesterday.strftime("%m-%d-%Y")
        file_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + d1 + '.csv'
        dfg = pd.read_csv(file_url)
        data = dfg[['Confirmed','Lat','Long_','Country_Region','Recovered','Deaths']]
        data.rename( columns={'Lat':'lat','Long_':'lon'},inplace = True)
        data = data.dropna()
        fig = px.scatter_mapbox(data,lat="lat", lon="lon", hover_name="Country_Region", hover_data=["Confirmed",'Recovered','Deaths'],
                                color_discrete_sequence=["firebrick"], zoom=3, height=300)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
        
st.sidebar.title(SUBHEAD_TITLE)
st.sidebar.subheader(SUBHEAD_CREDITS)
if __name__ == '__main__':
    main()
