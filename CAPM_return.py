#importing Dependecies

import streamlit as st 
import pandas as pd 
import yfinance as yf 
import datetime
import pandas_datareader.data as web
import capm_function

st.set_page_config(
    page_title="CAPM",
    page_icon="chart_with_upwards_trends",
    layout="wide"
)

st.title("Capital Asset Pricing Model")

#getting input from user

col1,col2 = st.columns([1,1])

with col1:
    stock_list=st.multiselect("Choose 4 stocks",('TSLA','AAPL','NFLIX','MGM','AMZN','NVDA','GOOGL'),['TSLA','AMZN','AAPL','GOOGL'])

with col2:
    year=st.number_input("Choose Number of years",1,10)


#downloading data for sp500
try:
    end = datetime.date.today()
    start= datetime.date(datetime.date.today().year - year,datetime.date.today().month,datetime.date.today().day)
    SP500 = web.DataReader(['sp500'],'fred',start,end)
    stock_df = pd.DataFrame()


    for stock in stock_list:
        data = yf.download(stock,period=f'{year}y')
        stock_df[f'{stock}']=data['Close']
        
    stock_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)
    SP500.columns = ['Date','sp500']

    stock_df = pd.merge(stock_df,SP500,on='Date',how='inner')

    col1,col2 = st.columns([1,1])
    with col1:
        st.markdown("#### Dataframe Head")
        st.dataframe(stock_df.head(),use_container_width = True)


    with col2:
        st.markdown("#### Dataframe Tail")
        st.dataframe(stock_df.tail(),use_container_width = True)


    col1,col2 = st.columns([1,1])

    with col1:
        st.markdown("#### Price of all the stocks")
        st.plotly_chart(capm_function.interactive_plot(stock_df))

    with col2:
        
        st.markdown("#### Price of all the stocks (After Normalization)")
        st.plotly_chart(capm_function.interactive_plot(capm_function.normalize(stock_df)))


    stock_daily_return = capm_function.daily_return(stock_df)

    print(stock_daily_return.head())

    beta = {}
    alpha = {}

    for i in stock_daily_return.columns:
        if i !='Date' and i!='sp500':
            b,a = capm_function.calculate_beta(stock_daily_return,i)

            beta[i]=b
            alpha[i] =a
    print(beta,alpha)

    beta_df = pd.DataFrame(columns=['Stocks','Beta Value'])
    beta_df['Stocks'] = beta.keys()
    beta_df['Beta Value']= [str(round(1,2))for i in beta.values()]

    with col1:
        st.markdown("#### Calculated Beta Value")
        st.dataframe(beta_df,use_container_width=True)

    rf=0
    rm = stock_daily_return['sp500'].mean() * 252 

    return_df = pd.DataFrame()
    return_value = []

    for stock,value in beta.items():
        return_value.append(str(round(rf +(value * (rm-rf)),2)))

    return_df['Stock']= stock_list 
    return_df['Return Value'] = return_value  

    with col2:
        st.markdown("### Calculated Return using CAPM")
        st.dataframe(return_df,use_container_width=True)

except Exception as e:
    st.write(f"Error occurred: {e}")