import requests
from pprint import pprint
import json
import pandas as pd
from datetime import datetime
import seaborn as sns
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

#config page
st.set_page_config(page_title='Sector Fundamentals Dashboard', layout="centered")

#refresh max once per day
refresh = st_autorefresh(interval=86400, limit=1)


#provide dex sector subgraph links
lending_subgraphs = {'benqi':'https://api.thegraph.com/subgraphs/name/messari/benqi-avalanche', \
                 'compound':'https://api.thegraph.com/subgraphs/name/messari/compound-ethereum', \
                 'liquity':'https://api.thegraph.com/subgraphs/name/messari/liquity-ethereum', \
                 'makerdao':'https://api.thegraph.com/subgraphs/name/messari/makerdao-ethereum', \
                 'venus':'https://api.thegraph.com/subgraphs/name/messari/venus-protocol-bsc', \
                 'bastion-protocol':'https://api.thegraph.com/subgraphs/name/messari/bastion-protocol-aurora', \
                 'abracadabra':'https://api.thegraph.com/subgraphs/name/messari/abracadabra-money-ethereum', \
                 'banker-joe':'https://api.thegraph.com/subgraphs/name/messari/banker-joe-avalanche', \
                 'inverse-finance':'https://api.thegraph.com/subgraphs/name/messari/inverse-finance-ethereum'
}

#for i in dex_subgraphs:
lending_protocols = list(lending_subgraphs)


##query for dex's
query ="""

{
  financialsDailySnapshots (first: 1000, orderBy: timestamp, orderDirection: desc) {
    id
    totalValueLockedUSD
    dailyTotalRevenueUSD
    totalBorrowBalanceUSD
    totalDepositBalanceUSD
    dailyBorrowUSD
    dailyDepositUSD
    timestamp
  }
  usageMetricsDailySnapshots (first: 1000, orderBy: timestamp, orderDirection: desc) {
    id
    dailyActiveUsers
    dailyTransactionCount
  }
}

"""

timestamp_current = []
tvl_current = []
daily_revenue_current = []
daily_borrow_balance_current = []
daily_deposits_balance_current = []
daily_borrows_current = []
daily_deposits_current = []
active_users_current = []
daily_tx_count_current = []

timestamp_90d = []
tvl_90d = []
daily_revenue_90d = []
daily_borrow_balance_90d = []
daily_deposits_balance_90d = []
daily_borrows_90d = []
daily_deposits_90d = []
active_users_90d = []
daily_tx_count_90d = []


# function to use requests.post to make an API call to the subgraph url
def run_query(q, s):
    #request from subgraph
    request = requests.post(s, json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, query))

        

def get_current_data(i):
    result = run_query(query, lending_subgraphs[i])
    timestamp = []
    tvl = []
    daily_revenue = []
    daily_borrow_balance = []
    daily_deposits_balance = []
    daily_borrows = []
    daily_deposits = []
    active_users = []
    daily_tx_count = []
    columns = ['timestamp', 'tvl', 'daily_revenue', 'daily_borrow_balance', 'daily_deposits_balance', 'daily_borrows', 'daily_deposits', 'active_users', 'daily_tx_count']

    for i in result['data']['financialsDailySnapshots']:
        timestamp.append(int(i['timestamp']))
        tvl.append(round(float(i['totalValueLockedUSD'])))
        daily_revenue.append(round(float(i['dailyTotalRevenueUSD'])))
        daily_borrow_balance.append(round(float(i['totalBorrowBalanceUSD'])))
        daily_deposits_balance.append(round(float(i['totalDepositBalanceUSD'])))
        daily_borrows.append(round(float(i['dailyBorrowUSD'])))
        daily_deposits.append(round(float(i['dailyDepositUSD'])))
    for i in result['data']['usageMetricsDailySnapshots']:
        active_users.append(i['dailyActiveUsers'])
        daily_tx_count.append(i['dailyTransactionCount'])
        #total_pool_count.append(i['totalPoolCount'])

    timestamp = [int(i) for i in timestamp]
    timestamp = [(datetime.fromtimestamp(i)).strftime('%Y-%m-%d') for i in timestamp]
    final_list = [timestamp, tvl, daily_revenue, daily_borrow_balance, daily_deposits_balance, daily_borrows, daily_deposits, active_users, daily_tx_count]

    df = pd.DataFrame(final_list)
    df = df.transpose()
    df.columns=columns
    #display(df)
    df = df.iloc[2]
    
    timestamp_current.append(df['timestamp'])
    tvl_current.append(df['tvl'])
    daily_revenue_current.append(df['daily_revenue'])
    daily_borrow_balance_current.append(df['daily_borrow_balance'])
    daily_deposits_balance_current.append(df['daily_deposits_balance'])
    daily_borrows_current.append(df['daily_borrows'])
    daily_deposits_current.append(df['daily_deposits'])
    active_users_current.append(df['active_users'])
    daily_tx_count_current.append(df['daily_tx_count'])

    
def get_prev_data(i):
    result = run_query(query, lending_subgraphs[i])
    timestamp = []
    tvl = []
    daily_revenue = []
    daily_borrow_balance = []
    daily_deposits_balance = []
    daily_borrows = []
    daily_deposits = []
    active_users = []
    daily_tx_count = []
    columns = ['timestamp', 'tvl', 'daily_revenue', 'daily_borrow_balance', 'daily_deposits_balance', 'daily_borrows', 'daily_deposits', 'active_users', 'daily_tx_count']

    for i in result['data']['financialsDailySnapshots']:
        timestamp.append(int(i['timestamp']))
        tvl.append(round(float(i['totalValueLockedUSD'])))
        daily_revenue.append(round(float(i['dailyTotalRevenueUSD'])))
        daily_borrow_balance.append(round(float(i['totalBorrowBalanceUSD'])))
        daily_deposits_balance.append(round(float(i['totalDepositBalanceUSD'])))
        daily_borrows.append(round(float(i['dailyBorrowUSD'])))
        daily_deposits.append(round(float(i['dailyDepositUSD'])))
    for i in result['data']['usageMetricsDailySnapshots']:
        active_users.append(i['dailyActiveUsers'])
        daily_tx_count.append(i['dailyTransactionCount'])

    timestamp = [int(i) for i in timestamp]
    timestamp = [(datetime.fromtimestamp(i)).strftime('%Y-%m-%d') for i in timestamp]

    final_list = [timestamp, tvl, daily_revenue, daily_borrow_balance, daily_deposits_balance, daily_borrows, daily_deposits, active_users, daily_tx_count]

    df = pd.DataFrame(final_list)
    df = df.transpose()
    df.columns=columns
    df = df.iloc[90]
    
    timestamp_90d.append(df['timestamp'])
    tvl_90d.append(df['tvl'])
    daily_revenue_90d.append(df['daily_revenue'])
    daily_borrow_balance_90d.append(df['daily_borrow_balance'])
    daily_deposits_balance_90d.append(df['daily_deposits_balance'])
    daily_borrows_90d.append(df['daily_borrows'])
    daily_deposits_90d.append(df['daily_deposits'])
    active_users_90d.append(df['active_users'])
    daily_tx_count_90d.append(df['daily_tx_count'])
    

@st.cache(allow_output_mutation=True)
def compile_df():
    for i in lending_protocols:
        get_current_data(i)
        get_prev_data(i)
        


    #create lists w/ current and previous values, convert to df, run % change, and export back to lists
    tvl_list = [tvl_90d, tvl_current]
    tvl_df = pd.DataFrame(tvl_list)
    tvl_df = tvl_df.pct_change()
    tvl_90d_pct_change = tvl_df.iloc[1].values.tolist()
     
    revenue_list = [daily_revenue_90d, daily_revenue_current]
    revenue_df = pd.DataFrame(revenue_list)
    revenue_df = revenue_df.pct_change()
    revenue_90d_pct_change = revenue_df.iloc[1].values.tolist() 

    daily_borrow_list = [daily_borrow_balance_90d, daily_borrow_balance_current]
    daily_borrow_df = pd.DataFrame(daily_borrow_list)
    daily_borrow_df = daily_borrow_df.pct_change()
    daily_borrow_90d_pct_change = daily_borrow_df.iloc[1].values.tolist() 

    daily_deposits_list = [daily_deposits_balance_90d, daily_deposits_balance_current]
    daily_deposits_df = pd.DataFrame(daily_deposits_list)
    daily_deposits_df = daily_deposits_df.pct_change()
    daily_deposits_90d_pct_change = daily_deposits_df.iloc[1].values.tolist() 

    borrows_list = [daily_borrows_90d, daily_borrows_current]
    borrows_df = pd.DataFrame(borrows_list)
    borrows_df = borrows_df.pct_change()
    borrows_90d_pct_change = borrows_df.iloc[1].values.tolist() 

    deposits_list = [daily_deposits_90d, daily_deposits_current]
    deposits_df = pd.DataFrame(deposits_list)
    deposits_df = deposits_df.pct_change()
    deposits_90d_pct_change = deposits_df.iloc[1].values.tolist() 

    active_users_list = [active_users_90d, active_users_current]
    active_users_df = pd.DataFrame(active_users_list)
    active_users_df = active_users_df.pct_change()
    active_users_90d_pct_change = active_users_df.iloc[1].values.tolist()

    daily_tx_count_list = [daily_tx_count_90d, daily_tx_count_current]
    daily_tx_count_df = pd.DataFrame(daily_tx_count_list)
    daily_tx_count_df = daily_tx_count_df.pct_change()
    daily_tx_count_90d_pct_change = daily_tx_count_df.iloc[1].values.tolist()


    final_list = [tvl_current, tvl_90d_pct_change, daily_revenue_current, revenue_90d_pct_change, \
                    daily_borrow_balance_current, daily_deposits_balance_current, daily_borrows_current, \
                    daily_deposits_current, active_users_current, active_users_90d_pct_change, daily_tx_count_current]

    columns = lending_protocols
    index = ['TVL', 'TVL 90d % ∆', 'Daily Revenue', 'Daily Revenue 90d % ∆', 'Daily Borrow Balance', \
             'Daily Deposit Balance', 'Daily Borrows', \
             'Daily Deposits', 'Active Users', 'Active Users 90d % ∆', \
             'Daily Tx Count']
    lending_df = pd.DataFrame(final_list, columns=columns, index=index)
    pd.options.display.float_format = '{:.2f}'.format
    #display(lending_df)


    #customize df based on data
    lending_df.loc['Collateral Ratio'] = (lending_df.loc['TVL'] / lending_df.loc['Daily Borrow Balance'])
    lending_df = lending_df.transpose()
    lending_df = lending_df.drop(['Daily Borrow Balance', 'Daily Deposit Balance'], axis=1)

    return lending_df


lending_df = compile_df()

#create cmaps for table
cmap = sns.diverging_palette(0, 150, s=75, as_cmap=True)
cmap_r = sns.diverging_palette(150, 0, s=75, as_cmap=True)

#create style object
lending_df_styler = lending_df.style\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[0]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[1]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[2]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[3]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[4]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[5]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[6]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[7]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[8]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[9]))\
    .format({'TVL': '${0:,.0f}', 'TVL 90d % ∆':'{0:,.2%}', 'Daily Revenue':'${0:,.0f}', \
             'Daily Revenue 90d % ∆':'{0:,.2%}', 'Daily Borrow Balance':'${0:,.0f}', \
             'Daily Deposit Balance':'${0:,.0f}', 'Daily Borrows':'${0:,.0f}', \
            'Daily Deposits':'${0:,.0f}', 'Active Users':'{0:,.0f}', 'Active Users 90d % ∆':'{0:,.2%}', \
            'Daily Tx Count':'{0:,.0f}', 'Collateral Ratio':'{0:,.2f}'})


lending_df = lending_df.reset_index()
lending_df = lending_df.rename(columns={'index':'Lending Protocols'})




#Header
st.title('Sector Fundamentals Dashboard')

st.write('\n \n This dashboard visualizes protocol fundamentals by sector, making it easy to compare competitors/peers. \n \
(Data Source: Messari Subgraphs)\n \n')


st.subheader('Lending Protocols:')

st.write(lending_df_styler, '\n')


#chart selections
tvl_chart = lending_df['TVL']
tvl_pct_change_chart = lending_df['TVL 90d % ∆']
daily_revenue_chart = lending_df['Daily Revenue']
daily_revenue_pct_change_chart = lending_df['Daily Revenue 90d % ∆']
daily_borrows_chart = lending_df['Daily Borrows']
daily_deposits_chart = lending_df['Daily Deposits']


chart_data = st.radio("Chart: ", ("TVL", "TVL 90d % ∆", "Daily Revenue", "Daily Revenue 90d % ∆", "Daily Borrows", "Daily Deposits", \
    "Active Users", "Active Users 90d % ∆", "Daily Tx Count", "Collateral Ratio"), horizontal=True)


#chart object
fig = px.bar(lending_df, y=chart_data, x=lending_df['Lending Protocols'])

#display df and bar chart
st.write(fig)







