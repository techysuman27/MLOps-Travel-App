"""The public UI calls Flask; it never trains or transforms model inputs."""
import os
from datetime import date
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title='Voyage Analytics', page_icon='✈', layout='wide')
API = os.environ.get('API_URL', 'http://127.0.0.1:8000').rstrip('/')
st.markdown('''<style>
.stApp {background: #f5f7fa;} h1,h2,h3 {color:#12344a;}
[data-testid="stMetric"] {background:white;border:1px solid #dbe5eb;border-radius:12px;padding:18px;}
.hero {background:#12344a;color:#fff;padding:30px 34px;border-radius:18px;margin-bottom:24px;}
.hero h1 {color:white;margin:0;} .hero p {color:#c8dde8;margin-bottom:0;}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>Voyage Analytics</h1><p>Explore travel patterns. Estimate flight prices. Find your next stay.</p></div>', unsafe_allow_html=True)
st.sidebar.title('Voyage')
page = st.sidebar.radio('Explore', ['Flight estimator', 'Hotel explorer', 'Project insights', 'Classification lab'])
st.sidebar.caption('AlmaBetter • Productionization of ML Systems\n\nHistorical educational demo. No live fares or availability.')


def get(path):
    response = requests.get(API + path, timeout=15)
    response.raise_for_status()
    return response.json()


def post(path, data):
    try:
        response = requests.post(API + path, json=data, timeout=30)
        body = response.json()
        if response.status_code != 200:
            st.error(body.get('error', 'Prediction service unavailable'))
            return None
        return body
    except (requests.RequestException, ValueError):
        st.error('The prediction service could not be reached. Please try again shortly.')
        return None


try:
    catalogue = get('/api/v1/catalogue')
    info = get('/api/v1/model-info')
except (requests.RequestException, ValueError):
    st.warning('The prediction service is starting or unavailable. Refresh once it is ready.')
    st.stop()

if page == 'Flight estimator':
    st.subheader('Plan a journey')
    st.write('Estimate a price using routes represented in the course dataset.')
    with st.form('flight'):
        left, right = st.columns(2)
        origin = left.selectbox('From', catalogue['cities'])
        destination = right.selectbox('To', catalogue['cities'], index=1)
        cabin = left.selectbox('Cabin', catalogue['flight_types'])
        agency = right.selectbox('Agency', catalogue['agencies'])
        duration = left.number_input('Flight duration (hours)', min_value=0.1, max_value=48.0, value=2.0, step=0.1)
        distance = right.number_input('Distance (dataset distance units)', min_value=1.0, max_value=20000.0, value=800.0, step=10.0)
        day = left.date_input('Travel date', value=date(2023, 6, 15), min_value=date(2019, 1, 1), max_value=date(2035, 12, 31))
        submitted = st.form_submit_button('Estimate flight price', type='primary')
    if submitted:
        with st.spinner('Preparing your estimate…'):
            result = post('/api/v1/flights/predict', {'from': origin, 'to': destination, 'flightType': cabin, 'agency': agency, 'time': duration, 'distance': distance, 'date': day.isoformat()})
        if result:
            st.metric('Estimated price · dataset currency units', f"{result['predicted_price']:,.2f}")
            for warning in result['warnings']:
                st.caption(warning)
            with st.expander('Prediction details'):
                st.json(result)
elif page == 'Hotel explorer':
    st.subheader('Find a stay in the historical catalogue')
    st.info('The dataset contains nine hotels, one per destination. Choosing a destination narrows the catalogue to one hotel.')
    with st.form('hotels'):
        a, b = st.columns(2)
        location = a.selectbox('Destination', ['Explore all'] + catalogue['cities'])
        budget = b.number_input('Maximum historical nightly price', min_value=1.0, value=500.0)
        returning = a.checkbox('Use a dataset user’s booking history')
        user = b.number_input('Dataset user code', min_value=0, max_value=1000000, value=0)
        go = st.form_submit_button('Suggest stays', type='primary')
    if go:
        data = {'budget': budget, 'k': 3}
        if location != 'Explore all': data['destination'] = location
        if returning: data['user_code'] = user
        result = post('/api/v1/hotels/recommend', data)
        if result:
            if not result['recommendations']:
                st.warning('No recorded hotel matches this budget and destination.')
            for item in result['recommendations']:
                with st.container(border=True):
                    st.subheader(item['hotel'])
                    st.write(item['place'])
                    st.metric('Historical nightly price', f"{item['historical_nightly_price']:,.2f}")
                    st.caption(item['reason'])
            st.caption(result['note'])
elif page == 'Project insights':
    st.subheader('From historical data to a working ML service')
    columns = st.columns(3)
    for column, name in zip(columns, ['flights', 'hotels', 'users']):
        column.metric(name.title() + ' records', f"{catalogue['counts'][name]:,}")
    st.markdown('**Historical hotel booking counts**')
    hotels = pd.DataFrame(catalogue['hotel_catalogue'])
    st.bar_chart(hotels.set_index('name')['bookings'])
    st.markdown('**Independent holdout results**')
    for task, details in info.items():
        with st.expander(task.title(), expanded=task == 'flights'):
            st.write('Selected model:', details['selected'])
            st.json(details['test_metrics'])
            for limitation in details['limitations']: st.caption(limitation)
            st.caption('Model version: ' + details['version'])
else:
    st.subheader('Educational classification lab')
    st.warning('This model predicts source dataset labels from company and age. It does not establish someone’s gender. The label “none” has no documented meaning.')
    with st.form('classification'):
        company = st.selectbox('Company', catalogue['companies'])
        age = st.number_input('Age', min_value=18, max_value=100, value=30)
        go = st.form_submit_button('Run educational example')
    if go:
        result = post('/api/v1/classification/predict', {'company': company, 'age': age})
        if result:
            st.write('Predicted source label:', result['predicted_dataset_label'])
            st.bar_chart(pd.Series(result['probabilities'], name='Model probability'))
            st.caption(result['warning'])
    if 'classification' in info:
        st.write('Measured holdout performance:', info['classification']['test_metrics'])
