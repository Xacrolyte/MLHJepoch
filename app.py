from covid_india import states
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# common variables
# GITHUB_REFERENCE = "<h5><a href='https://github.com/ChiragSaini/' target='_blank'>Github</a></h5>"
# LINKED_IN_REFERENCE = "<h5><a href='https://www.linkedin.com/in/chiragsaini97/' target='_blank'>LinkedIn</a></h5>"
# TWITTER_REFERENCE = "<h5><a href='https://twitter.com/ChiragSaini97' target='_blank'>Twitter</a></h5>"
SUBHEAD_TITLE = "COVID Dashboard and Vulnerability Analysis"
SUBHEAD_CREDITS = "Made by Epochalypse Team"
# c = covid.Covid()


# converts DataFrame to presentable card view in rows
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
st.dataframe(df)

# navigation (sidebar) properties
st.sidebar.subheader(SUBHEAD_TITLE)
st.sidebar.subheader(SUBHEAD_CREDITS)

#st.sidebar.markdown(GITHUB_REFERENCE, unsafe_allow_html=True)
#st.sidebar.markdown(LINKED_IN_REFERENCE, unsafe_allow_html=True)
#st.sidebar.markdown(TWITTER_REFERENCE, unsafe_allow_html=True)
