import requests
from pprint import pprint
import json
import pandas as pd
from datetime import datetime
import seaborn as sns
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from subgrounds.subgrounds import Subgrounds
import re
import seaborn as sns
import asyncio
from aiocache import Cache
from aiocache import cached

#config page
st.set_page_config(page_title='Sector Fundamentals Dashboard', layout="centered")

#refresh max once per day
refresh = st_autorefresh(interval=86400, limit=1)


sg = Subgrounds()


#provide lending sector subgraph links
lending_subgraphs = {'benqi':'https://api.thegraph.com/subgraphs/name/messari/benqi-avalanche', \
                 'compound':'https://api.thegraph.com/subgraphs/name/messari/compound-ethereum', \
                 'liquity':'https://api.thegraph.com/subgraphs/name/messari/liquity-ethereum', \
                 'makerdao':'https://api.thegraph.com/subgraphs/name/messari/makerdao-ethereum', \
                 'venus':'https://api.thegraph.com/subgraphs/name/messari/venus-protocol-bsc', \
                 'bastion-protocol':'https://api.thegraph.com/subgraphs/name/messari/bastion-protocol-aurora', \
                 'abracadabra':'https://api.thegraph.com/subgraphs/name/messari/abracadabra-money-ethereum', \
                 'banker-joe':'https://api.thegraph.com/subgraphs/name/messari/banker-joe-avalanche', \
                 'iron-bank-fantom':'https://api.thegraph.com/subgraphs/name/messari/iron-bank-fantom', \
                 'maple-finance-ethereum':'https://api.thegraph.com/subgraphs/name/messari/maple-finance-ethereum', \
                 'aave-v2-ethereum':'https://api.thegraph.com/subgraphs/name/messari/aave-v2-ethereum', \
                 'aave-v2-avalanche':'https://api.thegraph.com/subgraphs/name/messari/aave-v2-avalanche', \
                 'aave-v3-optimism':'https://api.thegraph.com/subgraphs/name/messari/aave-v3-optimism-extended', \
                 'aave-v3-polygon':'https://api.thegraph.com/subgraphs/name/messari/aave-v3-polygon', \
                 'aave-v3-harmony':'https://api.thegraph.com/subgraphs/name/messari/aave-v3-harmony', \
                 'aave-v3-fantom':'https://api.thegraph.com/subgraphs/name/messari/aave-v3-fantom', \
                 'aave-v3-avalanche':'https://api.thegraph.com/subgraphs/name/messari/aave-v3-avalanche', \
                 'aave-v3-arbitrum':'https://api.thegraph.com/subgraphs/name/messari/aave-v3-arbitrum', \
                 #'cream-finance-arbitrum':'https://api.thegraph.com/subgraphs/name/messari/cream-finance-arbitrum', \
                 #'cream-finance-polygon':'https://api.thegraph.com/subgraphs/name/messari/cream-finance-polygon', \
                 #'cream-finance-bsc':'https://api.thegraph.com/subgraphs/name/messari/cream-finance-bsc', \
                 #'cream-finance-ethereum':'https://api.thegraph.com/subgraphs/name/messari/cream-finance-ethereum', \
                 'moonwell-moonriver':'https://api.thegraph.com/subgraphs/name/messari/moonwell-moonriver', \
                 #'moonwell-moonbeam':'https://api.thegraph.com/subgraphs/name/messari/moonwell-moonbeam', \
                 'abracadabra-money-bsc':'https://api.thegraph.com/subgraphs/name/messari/abracadabra-money-bsc', \
                 'abracadabra-money-arbitrum':'https://api.thegraph.com/subgraphs/name/messari/abracadabra-money-arbitrum', \
                 'abracadabra-money-fantom':'https://api.thegraph.com/subgraphs/name/messari/abracadabra-money-fantom', \
                 'abracadabra-money-avalanche':'https://api.thegraph.com/subgraphs/name/messari/abracadabra-money-avalanche', \
                 'qidao-arbitrum':'https://api.thegraph.com/subgraphs/name/messari/qidao-arbitrum', \
                 'qidao-avalanche':'https://api.thegraph.com/subgraphs/name/messari/qidao-avalanche', \
                 'qidao-bsc':'https://api.thegraph.com/subgraphs/name/messari/qidao-bsc', \
                 'qidao-fantom':'https://api.thegraph.com/subgraphs/name/messari/qidao-fantom', \
                 'qidao-polygon':'https://api.thegraph.com/subgraphs/name/messari/qidao-polygon', \
                 #'qidao-moonriver':'https://api.thegraph.com/subgraphs/name/messari/qidao-moonriver', \
                 'qidao-optimism':'https://api.thegraph.com/subgraphs/name/messari/qidao-optimism', \
                 'qidao-gnosis':'https://api.thegraph.com/subgraphs/name/messari/qidao-gnosis'
}


##get lending sector data
def get_lending_data():
    df_list = []
    for i in lending_subgraphs:
        endpoint = sg.load_subgraph(lending_subgraphs[i])
        
        financial_data = endpoint.Query.financialsDailySnapshots(first=90, orderBy=endpoint.FinancialsDailySnapshot.timestamp, orderDirection='desc')
        financial_df = sg.query_df([
            financial_data.timestamp,
            financial_data.protocol.name,
            financial_data.totalValueLockedUSD,
            financial_data.dailyTotalRevenueUSD,
            financial_data.totalBorrowBalanceUSD,
            financial_data.totalDepositBalanceUSD,
            financial_data.dailyBorrowUSD,
            financial_data.dailyDepositUSD
         ])
        financial_df['financialsDailySnapshots_timestamp'] = financial_df['financialsDailySnapshots_timestamp'].apply(datetime.fromtimestamp).dt.strftime('%Y-%m-%d')
        financial_df = financial_df.rename(columns={'financialsDailySnapshots_totalValueLockedUSD':'totalValueLockedUSD', \
                                                    'financialsDailySnapshots_dailyTotalRevenueUSD':'dailyTotalRevenueUSD', \
                                                    'financialsDailySnapshots_totalBorrowBalanceUSD':'totalBorrowBalanceUSD', \
                                                   'financialsDailySnapshots_totalDepositBalanceUSD':'totalDepositBalanceUSD', \
                                                   'financialsDailySnapshots_dailyBorrowUSD':'dailyBorrowUSD', \
                                                   'financialsDailySnapshots_dailyDepositUSD':'dailyDepositUSD', \
                                                   'financialsDailySnapshots_timestamp':'timestamp', \
                                                   'financialsDailySnapshots_protocol_name':'protocol_name'})
        financial_df['timestamp'] = pd.to_datetime(financial_df['timestamp'], format='%Y-%m-%d')
        today = datetime.today().strftime('%Y-%m-%d')
        financial_df = financial_df[financial_df['timestamp'] != today]


        usage_data = endpoint.Query.usageMetricsDailySnapshots(first=90, orderBy=endpoint.UsageMetricsDailySnapshot.timestamp, orderDirection='desc')
        usage_df = sg.query_df([
            usage_data.timestamp,
            usage_data.dailyActiveUsers,
            usage_data.dailyTransactionCount
        ])

        usage_df['usageMetricsDailySnapshots_timestamp'] = usage_df['usageMetricsDailySnapshots_timestamp'].apply(datetime.fromtimestamp).dt.strftime('%Y-%m-%d')
        usage_df = usage_df.rename(columns={'usageMetricsDailySnapshots_timestamp':'timestamp', \
                                           'usageMetricsDailySnapshots_dailyActiveUsers':'dailyActiveUsers', \
                                           'usageMetricsDailySnapshots_dailyTransactionCount':'dailyTransactionCount'})
        usage_df = usage_df[usage_df['timestamp'] != today]
        usage_df['timestamp'] = pd.to_datetime(financial_df['timestamp'], format='%Y-%m-%d')

        df = pd.merge(financial_df, usage_df, on='timestamp')
        current_values = df.iloc[1]    
        prev_90d_values = df.iloc[-1]
        concat_df = pd.concat([prev_90d_values, current_values], axis=1)
        concat_df = concat_df.transpose()
        concat_df['timestamp'] = concat_df['timestamp'].dt.strftime('%Y-%m')
        df_list.append(concat_df)
        
    df = pd.concat(df_list, axis=0).reset_index(drop=True)
    df['protocol_name'] = df['protocol_name'].str.replace(' v2', '')
    df['protocol_name'] = df['protocol_name'].str.replace(' V3 Extended', '')
    df['protocol_name'] = df['protocol_name'].str.replace(' V3', '')
    df = df.groupby(['timestamp', 'protocol_name']).sum().reset_index()
    df = df.sort_values(by=['protocol_name', 'timestamp']).reset_index(drop=True)
    return df

async def async_get_lending_data():
    return asyncio.to_thread(get_lending_data)


#calculate pct change values and format
#@st.cache(allow_output_mutation=True)
def get_lending_pct_change_values(df):
    df['totalValueLockedUSD_90d_pct_change'] = df['totalValueLockedUSD'].pct_change()
    df['dailyTotalRevenueUSD_90d_pct_change'] = df['dailyTotalRevenueUSD'].pct_change()
    df['totalBorrowBalanceUSD_90d_pct_change'] = df['totalBorrowBalanceUSD'].pct_change()
    df['totalDepositBalanceUSD_90d_pct_change'] = df['totalDepositBalanceUSD'].pct_change()
    df['dailyActiveUsers_90d_pct_change'] = df['dailyActiveUsers'].pct_change()
    df['dailyTransactionCount_90d_pct_change'] = df['dailyTransactionCount'].pct_change()
    df = df[['timestamp', 'protocol_name', 'totalValueLockedUSD', 'totalValueLockedUSD_90d_pct_change', \
                          'dailyTotalRevenueUSD', 'dailyTotalRevenueUSD_90d_pct_change', \
                          'totalBorrowBalanceUSD', 'totalBorrowBalanceUSD_90d_pct_change', \
                          'totalDepositBalanceUSD', 'totalDepositBalanceUSD_90d_pct_change', \
                          'dailyBorrowUSD', 'dailyDepositUSD', 'dailyActiveUsers', \
                          'dailyActiveUsers_90d_pct_change', 'dailyTransactionCount', \
                          'dailyTransactionCount_90d_pct_change']]
    df = df.reset_index(drop=True)
    df = df.drop([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    df = df.rename(columns={'protocol_name':'Protocol', 'totalValueLockedUSD':'TVL', \
                       'totalValueLockedUSD_90d_pct_change':'TVL 90d % ∆', \
                       'dailyTotalRevenueUSD':'Daily Total Revenue USD', \
                       'dailyTotalRevenueUSD_90d_pct_change':'Daily Total Revenue 90d % ∆', \
                       'totalBorrowBalanceUSD':'Total Borrow Balance USD', \
                       'totalBorrowBalanceUSD_90d_pct_change':'Total Borrow Balance 90d % ∆', \
                       'totalDepositBalanceUSD':'Total Deposit Balance USD', \
                       'totalDepositBalanceUSD_90d_pct_change':'Total Deposit Balance 90d % ∆', \
                       'dailyBorrowUSD':'Daily Borrows USD', 'dailyDepositUSD':'Daily Deposits USD', \
                       'dailyActiveUsers':'Daily Active Users', \
                       'dailyActiveUsers_90d_pct_change':'Daily Active Users 90d % ∆', \
                       'dailyTransactionCount':'Daily Transaction Count', \
                       'dailyTransactionCount_90d_pct_change':'Daily Transaction Count 90d % ∆'})
    df['Collateral Ratio'] = df['Total Deposit Balance USD'] / df['Total Borrow Balance USD']
    df = df.drop(['timestamp'], axis=1)
    df = df.set_index('Protocol')
    return df



dex_subgraphs = {
    'balancer-v2-ethereum':'https://api.thegraph.com/subgraphs/name/messari/balancer-v2-ethereum',
    'balancer-v2-arbitrum':'https://api.thegraph.com/subgraphs/name/messari/balancer-v2-arbitrum',
    #'balancer-v2-polygon':'https://api.thegraph.com/subgraphs/name/messari/balancer-v2-polygon', deprecating code
    #'bancor-v3-ethereum':'https://api.thegraph.com/subgraphs/name/messari/bancor-v3-ethereum',
    #'beethoven-x-optimism':'https://api.thegraph.com/subgraphs/name/messari/beethoven-x-optimism',
    'honeyswap-gnosis':'https://api.thegraph.com/subgraphs/name/messari/honeyswap-gnosis',
    'platypus-finance-avalanche':'https://api.thegraph.com/subgraphs/name/messari/platypus-finance-avalanche',
    'solarbeam-moonriver':'https://api.thegraph.com/subgraphs/name/messari/solarbeam-moonriver',
    'ubeswap-celo':'https://api.thegraph.com/subgraphs/name/messari/ubeswap-celo',
    'sushiswap-ethereum':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-ethereum',
    'sushiswap-celo':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-celo',
    'sushiswap-moonriver':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-moonriver',
    'sushiswap-moonbeam':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-moonbeam',
    'sushiswap-avalanche':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-avalanche',
    'sushiswap-bsc':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-bsc',
    'sushiswap-arbitrum':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-arbitrum',
    'sushiswap-fantom':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-fantom',
    'sushiswap-gnosis':'https://api.thegraph.com/subgraphs/name/messari/sushiswap-gnosis',
#     'uniswap-v3-ethereum':'https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-ethereum', #TVL off
    'uniswap-v3-polygon':'https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-polygon',
    'uniswap-v3-optimism':'https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-optimism',
    'uniswap-v3-arbitrum':'https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-arbitrum'
}

#get dex sector data
def get_dex_data():
    df_list = []
    for i in dex_subgraphs:
        endpoint = sg.load_subgraph(dex_subgraphs[i])
        
        financial_data = endpoint.Query.financialsDailySnapshots(first=90, orderBy=endpoint.FinancialsDailySnapshot.timestamp, orderDirection='desc')
        financial_df = sg.query_df([
            financial_data.timestamp,
            financial_data.protocol.name,
            financial_data.totalValueLockedUSD,
            financial_data.dailyVolumeUSD,
            financial_data.dailySupplySideRevenueUSD,
            financial_data.dailyProtocolSideRevenueUSD,
            financial_data.dailyTotalRevenueUSD
         ])
        financial_df['financialsDailySnapshots_timestamp'] = financial_df['financialsDailySnapshots_timestamp'].apply(datetime.fromtimestamp).dt.strftime('%Y-%m-%d')
        financial_df = financial_df.rename(columns={'financialsDailySnapshots_totalValueLockedUSD':'totalValueLockedUSD', \
                                                    'financialsDailySnapshots_dailyVolumeUSD':'dailyVolumeUSD', \
                                                    'financialsDailySnapshots_dailySupplySideRevenueUSD':'dailySupplySideRevenueUSD', \
                                                   'financialsDailySnapshots_dailyProtocolSideRevenueUSD':'dailyProtocolSideRevenueUSD', \
                                                   'financialsDailySnapshots_dailyTotalRevenueUSD':'dailyTotalRevenueUSD', \
                                                   'financialsDailySnapshots_timestamp':'timestamp', \
                                                   'financialsDailySnapshots_protocol_name':'protocol_name'})
        financial_df['timestamp'] = pd.to_datetime(financial_df['timestamp'], format='%Y-%m-%d')
        today = datetime.today().strftime('%Y-%m-%d')
        financial_df = financial_df[financial_df['timestamp'] != today]


        usage_data = endpoint.Query.usageMetricsDailySnapshots(first=90, orderBy=endpoint.UsageMetricsDailySnapshot.timestamp, orderDirection='desc')
        usage_df = sg.query_df([
            usage_data.timestamp,
            usage_data.dailyActiveUsers,
            usage_data.dailyTransactionCount,
            usage_data.dailySwapCount,
            usage_data.totalPoolCount
        ])

        usage_df['usageMetricsDailySnapshots_timestamp'] = usage_df['usageMetricsDailySnapshots_timestamp'].apply(datetime.fromtimestamp).dt.strftime('%Y-%m-%d')
        usage_df = usage_df.rename(columns={'usageMetricsDailySnapshots_timestamp':'timestamp', \
                                           'usageMetricsDailySnapshots_dailyActiveUsers':'dailyActiveUsers', \
                                           'usageMetricsDailySnapshots_dailyTransactionCount':'dailyTransactionCount', \
                                           'usageMetricsDailySnapshots_dailySwapCount':'dailySwapCount', \
                                           'usageMetricsDailySnapshots_totalPoolCount':'totalPoolCount'})
        usage_df = usage_df[usage_df['timestamp'] != today]
        usage_df['timestamp'] = pd.to_datetime(financial_df['timestamp'], format='%Y-%m-%d')

        df = pd.merge(financial_df, usage_df, on='timestamp')
        current_values = df.iloc[1]    
        prev_90d_values = df.iloc[-1]
        concat_df = pd.concat([prev_90d_values, current_values], axis=1)
        concat_df = concat_df.transpose()
        concat_df['timestamp'] = concat_df['timestamp'].dt.strftime('%Y-%m')
        df_list.append(concat_df)
        
    df = pd.concat(df_list, axis=0).reset_index(drop=True)
    df = df.groupby(['timestamp', 'protocol_name']).sum().reset_index()
    df = df.sort_values(by=['protocol_name', 'timestamp']).reset_index(drop=True)
    return df


async def async_get_dex_data():
    return asyncio.to_thread(get_dex_data)


#calculate pct change values for dex sector
#@st.cache(allow_output_mutation=True)
def get_dex_pct_change_values(df):
    df['totalValueLockedUSD_90d_pct_change'] = df['totalValueLockedUSD'].pct_change()
    df['dailyVolumeUSD_90d_pct_change'] = df['dailyVolumeUSD'].pct_change()
    df['dailySupplySideRevenueUSD_90d_pct_change'] = df['dailySupplySideRevenueUSD'].pct_change()
    df['dailyProtocolSideRevenueUSD_90d_pct_change'] = df['dailyProtocolSideRevenueUSD'].pct_change()
    df['dailyTotalRevenueUSD_90d_pct_change'] = df['dailyTotalRevenueUSD'].pct_change()
    df['dailyActiveUsers_90d_pct_change'] = df['dailyActiveUsers'].pct_change()
    df['dailyTransactionCount_90d_pct_change'] = df['dailyTransactionCount'].pct_change()
    df['dailySwapCount_90d_pct_change'] = df['dailySwapCount'].pct_change()
    df['totalPoolCount_90d_pct_change'] = df['totalPoolCount'].pct_change()
    df = df[['timestamp', 'protocol_name', 'totalValueLockedUSD', 'totalValueLockedUSD_90d_pct_change', \
                          'dailyVolumeUSD', 'dailyVolumeUSD_90d_pct_change', \
                          'dailySupplySideRevenueUSD', 'dailySupplySideRevenueUSD_90d_pct_change', \
                          'dailyProtocolSideRevenueUSD', 'dailyProtocolSideRevenueUSD_90d_pct_change', \
                          'dailyTotalRevenueUSD', 'dailyTotalRevenueUSD_90d_pct_change', \
                          'dailyActiveUsers', 'dailyActiveUsers_90d_pct_change', \
                          'dailyTransactionCount', 'dailyTransactionCount_90d_pct_change', \
                          'dailySwapCount', 'dailySwapCount_90d_pct_change', \
                          'totalPoolCount', 'totalPoolCount_90d_pct_change']]
    df = df.reset_index(drop=True)
    df = df.drop([0, 2, 4, 6, 8, 10, 12])
    df = df.rename(columns={'protocol_name':'Protocol', 'totalValueLockedUSD':'TVL', \
                       'totalValueLockedUSD_90d_pct_change':'TVL 90d % ∆', \
                       'dailyVolumeUSD':'Daily Volume USD', \
                       'dailyVolumeUSD_90d_pct_change':'Daily Volume 90d % ∆', \
                       'dailySupplySideRevenueUSD':'Daily Supply Side Revenue USD', \
                       'dailySupplySideRevenueUSD_90d_pct_change':'Daily Supply Side Revenue 90d % ∆', \
                       'dailyProtocolSideRevenueUSD':'Daily Protocol Side Revenue USD', \
                       'dailyProtocolSideRevenueUSD_90d_pct_change':'Daily Protocol Side Revenue 90d % ∆', \
                       'dailyTotalRevenueUSD':'Daily Total Revenue USD', \
                       'dailyTotalRevenueUSD_90d_pct_change':'Daily Total Revenue 90d % ∆', \
                       'dailyActiveUsers':'Daily Active Users', \
                       'dailyActiveUsers_90d_pct_change':'Daily Active Users 90d % ∆', \
                       'dailyTransactionCount':'Daily Transaction Count', \
                       'dailyTransactionCount_90d_pct_change':'Daily Transaction Count 90d % ∆', \
                       'dailySwapCount':'Daily Swap Count', \
                       'dailySwapCount_90d_pct_change':'Daily Swap Count 90d % ∆', \
                       'totalPoolCount':'Total Pool Count', \
                       'totalPoolCount_90d_pct_change':'Total Pool Count 90d % ∆'})
    df = df.drop(['timestamp'], axis=1)
    df = df.set_index('Protocol')
    return df


#main, run dex, and lending sector get_data() functions concurrently
@cached(ttl=None, cache=Cache.MEMORY)
async def main():
    result = await asyncio.gather(*[
        await async_get_lending_data(),
        await async_get_dex_data()
    ])

    return result

variable = asyncio.run(main())

df1 = variable[0] #lending
df2 = variable[1] #dex

lending_df = get_lending_pct_change_values(df1)
dex_df = get_dex_pct_change_values(df2)


#create cmaps for table
cmap = sns.diverging_palette(0, 150, s=75, as_cmap=True)
cmap_r = sns.diverging_palette(150, 0, s=75, as_cmap=True)

#create dex style object
dex_df_styler = dex_df.style\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[0]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[1]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[2]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[3]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[4]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[5]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[6]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[7]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[8]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[9]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[10]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[11]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[12]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[13]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[14]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[15]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[16]))\
    .background_gradient(axis=0, cmap=cmap, subset=(dex_df.index, dex_df.columns[17]))\
    .format({'TVL': '${0:,.0f}', 'TVL 90d % ∆':'{0:,.2%}', 'Daily Volume USD':'${0:,.0f}', \
             'Daily Volume 90d % ∆':'{0:,.2%}', 'Daily Supply Side Revenue USD':'${0:,.0f}', \
             'Daily Supply Side Revenue 90d % ∆':'{0:,.2%}', 'Daily Protocol Side Revenue USD':'${0:,.0f}', \
             'Daily Protocol Side Revenue 90d % ∆':'{0:,.2%}', 'Daily Total Revenue USD':'${0:,.0f}', \
             'Daily Total Revenue 90d % ∆':'{0:,.2%}', 'Daily Active Users':'{0:,.0f}', \
             'Daily Active Users 90d % ∆':'{0:,.2%}', 'Daily Transaction Count':'{0:,.0f}', \
             'Daily Transaction Count 90d % ∆':'{0:,.2%}', 'Daily Swap Count':'{0:,.0f}', \
             'Daily Swap Count 90d % ∆':'{0:,.2%}', 'Total Pool Count':'{0:,.0f}', \
             'Total Pool Count 90d % ∆':'{0:,.2%}'
            })


#create lending style object
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
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[10]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[11]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[12]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[13]))\
    .background_gradient(axis=0, cmap=cmap, subset=(lending_df.index, lending_df.columns[14]))\
    .format({'TVL': '${0:,.0f}', 'TVL 90d % ∆':'{0:,.2%}', 'Daily Total Revenue USD':'${0:,.0f}', \
             'Daily Total Revenues 90d % ∆':'{0:,.2%}', 'Total Borrow Balance USD':'${0:,.0f}', \
             'Total Borrow Balance 90d % ∆':'{0:,.2%}', 'Total Deposit Balance USD':'${0:,.0f}', \
             'Total Deposit Balance 90d % ∆':'{0:,.2%}', 'Daily Borrows USD':'${0:,.0f}', \
             'Daily Deposits USD':'${0:,.0f}', 'Daily Active Users':'{0:,.0f}', \
             'Daily Active Users 90d % ∆':'{0:,.2%}', 'Daily Transaction Count':'{0:,.0f}', \
             'Daily Transaction Count 90d % ∆':'{0:,.2%}', 'Collateral Ratio':'{0:,.2f}'})



st.title('Sector Fundamentals Dashboard')
st.write('\n \n This dashboard visualizes protocol fundamentals by sector, making it easy to compare competitors/peers. \n \
(Data Source: Messari Subgraphs)\n \n')


lending_df.index.name = 'Protocol'
dex_df.index.name = 'Protocol'

options = ['Lending', "DEX's"]
sector = st.sidebar.selectbox(
    'Sector:',
    options,
    key='sector'
)

if sector == 'Lending':
    st.subheader('Lending Protocols:')
    st.write(lending_df_styler)
    chart_data = ["TVL", "TVL 90d % ∆", "Daily Total Revenue USD", "Daily Total Revenue 90d % ∆", "Total Borrow Balance USD", \
        "Total Borrow Balance 90d % ∆", "Total Deposit Balance USD", "Total Deposit Balance 90d % ∆", "Daily Borrows USD", \
        "Daily Deposits USD", "Daily Active Users", "Daily Active Users 90d % ∆", "Daily Transaction Count", \
        "Daily Transaction Count 90d % ∆", "Collateral Ratio"]
    select_y = st.selectbox('Chart:', chart_data)


    #chart object
    fig = px.bar(lending_df, y=select_y, x=lending_df.index)

    #display df and bar chart
    st.write(fig)

elif sector == "DEX's":
    st.subheader('Dex Protocols:')
    st.write(dex_df_styler)
    st.write('Note: Uniswap-v3 does not include Ethereum mainnet')
    chart_data = ["TVL", "TVL 90d % ∆", "Daily Volume USD", "Daily Volume 90d % ∆", "Daily Supply Side Revenue USD", "Daily Supply Side Revenue 90d % ∆", \
    "Daily Protocol Side Revenue USD", "Daily Protocol Side Revenue 90d % ∆", "Daily Total Revenue USD", "Daily Total Revenue 90d % ∆", \
    "Daily Active Users", "Daily Active Users 90d % ∆", "Daily Transaction Count", "Daily Transaction Count 90d % ∆", \
    "Daily Swap Count", "Daily Swap Count 90d % ∆", "Total Pool Count", "Total Pool Count 90d % ∆"]
    select_y = st.selectbox('Chart:', chart_data)


    #chart object
    fig = px.bar(dex_df, y=select_y, x=dex_df.index)

    #display df and bar chart
    st.write(fig)






