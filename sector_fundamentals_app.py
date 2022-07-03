#import requests # TODO, get rid of this
#import time

# For Data Science
import pandas as pd
from datetime import datetime, timedelta

# For plotting
#import matplotlib.pyplot as plt
import seaborn as sns
from messari.messari import Messari
from messari.tokenterminal import TokenTerminal
import streamlit as st


#messari = Messari('28f96cae-9ae0-42f3-9a41-5d862d150406')
# coingecko = CoinGecko()
# defillama = DeFiLlama()
# floor = NFTPriceFloor()
tokenterminal = TokenTerminal(api_key='610b30be-e8b5-4b64-a27d-d59c94132ee4')


start_date = '2022-01-01'
end_date = str(datetime.now().date())


#import dataframe_image for exporting tables to png
layer_one_protocols = ['algorand', 'avalanche', 'binance-smart-chain', 'cardano', 'cosmos', 'ethereum', 'fantom', 'kusama', 'polkadot', 'near-protocol', 'solana']
lending_protocols = ['compound','aave', 'makerdao', 'rari-capital', '88mph', 'benqi', 'euler', 'liquity', 'solend', 'abracadabra-money', 'centrifuge', 'maple-finance', 'venus']
dex_protocols = ['0x','1inch' ,'uniswap', 'sushiswap', 'curve', 'balancer', 'bancor', 'clipper',  'hurricaneswap', 'pancakeswap', 'quickswap', 'saddle-finance', 'spookyswap', 'thorchain', 'trader-joe', 'wakaswap', 'dodo', 'ellipsis-finance', 'kyber', 'pangolin']
perp_protocols = ['dydx', 'futureswap', 'gmx', 'mcdex', 'perpetual-protocol']
options_protocols = ['ribbon-finance']
yield_protocols = ['yearn-finance', 'alpha-finance', 'autofarm', 'convex-finance', 'harvest-finance', 'idle-finance', 'enzyme-finance', 'dhedge', 'index-cooperative','mstable' , 'piedao', 'pooltogether', 'stake-dao', 'vesper-finance', 'yield-yak' ]
synth_protocols = ['synthetix', 'uma']
staking_protocols = ['lido-finance', 'rocket-pool']
web3_protocols = ['arweave', 'filecoin', 'helium', 'livepeer', 'pocket-network', 'the-graph']
project_ids = tokenterminal.get_project_ids()


#this function gathers data by sector, taking the lists above and pulling data from token terminal api. 
#calculates 90d percent change and compiles all to a final dataframe
#sectors are defined above
def gather_sector_data(sector):
    df = tokenterminal.get_protocol_data(sector, start_date=start_date, end_date=end_date)
    df.index = pd.to_datetime(df.index)
    df = df.iloc[-2]


    current_price = []
    current_market_cap = []
    current_volume = []
    current_pe = []
    current_ps = []
    current_tvl = []
    current_gmv = []
    current_revenue = []
    current_revenue_supply_side = []
    current_revenue_protocol = []
    columns = sector 

    #current values
    for i in columns:
        current_price.append(df[i, 'price'])
        current_market_cap.append(df[i, 'market_cap'])
        current_volume.append(df[i, 'volume'])
        current_pe.append(df[i, 'pe'])
        current_ps.append(df[i, 'ps'])
        current_tvl.append(df[i, 'tvl'])
        current_gmv.append(df[i, 'gmv'])
        current_revenue.append(df[i, 'revenue'])
        current_revenue_supply_side.append(df[i, 'revenue_supply_side'])
        current_revenue_protocol.append(df[i, 'revenue_protocol'])

        #get values from 90 days ago for %change calculations
        df2 = tokenterminal.get_protocol_data(sector, start_date=start_date, end_date=end_date)
        df2.index = pd.to_datetime(df2.index)
        df2 = df2.iloc[-90]

    prev_90_tvl = []
    prev_90_gmv = []
    prev_90_revenue = []
    prev_90_revenue_supply_side = []
    prev_90_revenue_protocol = []

    #append values 90 days prior to lists above 
    for i in columns:
        prev_90_tvl.append(df2[i, 'tvl'])
        prev_90_gmv.append(df2[i, 'gmv'])
        prev_90_revenue.append(df2[i, 'revenue'])
        prev_90_revenue_supply_side.append(df2[i, 'revenue_supply_side'])
        prev_90_revenue_protocol.append(df2[i, 'revenue_protocol'])

    #create lists w/ current and previous values, convert to df, run % change, and export back to lists
    tvl_list = [prev_90_tvl, current_tvl]
    tvl_df = pd.DataFrame(tvl_list, columns=columns)
    tvl_df = tvl_df.pct_change()
    tvl_90d_pct_change = tvl_df.iloc[1].values.tolist()

    gmv_list = [prev_90_gmv, current_gmv]
    gmv_df = pd.DataFrame(gmv_list, columns=columns)
    gmv_df = gmv_df.pct_change()
    gmv_90d_pct_change = gmv_df.iloc[1].values.tolist()  

    revenue_list = [prev_90_revenue, current_revenue]
    revenue_df = pd.DataFrame(revenue_list, columns=columns)
    revenue_df = revenue_df.pct_change()
    revenue_90d_pct_change = revenue_df.iloc[1].values.tolist() 

    ss_revenue_list = [prev_90_revenue_supply_side, current_revenue_supply_side]
    ss_revenue_df = pd.DataFrame(ss_revenue_list, columns=columns)
    ss_revenue_df = ss_revenue_df.pct_change()
    ss_revenue_90d_pct_change = ss_revenue_df.iloc[1].values.tolist() 

    p_revenue_list = [prev_90_revenue_protocol, current_revenue_protocol]
    p_revenue_df = pd.DataFrame(p_revenue_list, columns=columns)
    p_revenue_df = p_revenue_df.pct_change()
    p_revenue_90d_pct_change = p_revenue_df.iloc[1].values.tolist()

    final = [current_price, current_market_cap, current_volume, current_pe, current_ps, current_tvl, tvl_90d_pct_change, current_gmv, gmv_90d_pct_change, current_revenue, revenue_90d_pct_change, current_revenue_supply_side, ss_revenue_90d_pct_change, current_revenue_protocol, p_revenue_90d_pct_change]
    index_list = ['Price', 'Market Cap', 'Volume (Daily)', 'P/E', 'P/S', 'TVL', 'TVL 90d % ∆', 'GMV', 'GMV 90d % ∆', 'Revenue (Daily)', 'Revenue 90d % ∆', 'Supply Side Revenue (Daily)', 'Supply Side Revenue 90d % ∆', 'Protocol Revenue (Daily)', 'Protocol Revenue 90d % ∆']

    final_df = pd.DataFrame(final, columns=columns, index=index_list)

    return(final_df)



##Lenders
#call function for lending
final_lending_df = gather_sector_data(lending_protocols)

#customize df based on data
final_lending_df = final_lending_df.drop(['centrifuge', 'rari-capital', '88mph', 'euler', 'abracadabra-money', 'venus'], axis=1)
final_lending_df.loc['Collateral Ratio'] = (final_lending_df.loc['TVL'] / final_lending_df.loc['GMV'])
final_lending_df = final_lending_df.transpose()
final_lending_df = final_lending_df.drop(['Price', 'P/E', 'Supply Side Revenue (Daily)', 'Supply Side Revenue 90d % ∆', 'Protocol Revenue (Daily)', 'Protocol Revenue 90d % ∆'], axis=1)

#create cmaps for table
cmap = sns.diverging_palette(0, 150, s=75, as_cmap=True)
cmap_r = sns.diverging_palette(150, 0, s=75, as_cmap=True)

#create style object
lending_df_styler = final_lending_df.style\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[0]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[1]))\
    .background_gradient(axis=0, cmap=cmap_r, subset=(final_lending_df.index, final_lending_df.columns[2]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[3]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[4]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[5]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[6]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[7]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[8]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_lending_df.index, final_lending_df.columns[9]))\
    .format({'Market Cap': '${0:,.0f}', 'Volume (Daily)':'${0:,.0f}', 'P/E':'{0:,.2f}', 'P/S':'{0:,.2f}', 'TVL':'${0:,.0f}', 'TVL 90d % ∆':'{0:,.2%}', 'GMV':'${0:,.0f}',\
            'GMV 90d % ∆':'{0:,.2%}', 'Revenue (Daily)':'${0:,.0f}', 'Revenue 90d % ∆':'{0:,.2%}',\
            'Supply Side Revenue (Daily)':'${0:,.0f}', 'Supply Side Revenue 90d % ∆':'{0:,.2%}',\
            'Protocol Revenue (Daily)':'${0:,.0f}', 'Protocol Revenue 90d % ∆':'{0:,.2%}', 'Collateral Ratio':'{0:,.2f}'})
 

#DEX's
#call function to get dex_df
final_dex_df = gather_sector_data(dex_protocols)

#customize below depending on data
final_dex_df = final_dex_df.drop(['0x', '1inch', 'clipper', 'hurricaneswap', 'pancakeswap', 'saddle-finance', 'thorchain', 'wakaswap', 'dodo', 'ellipsis-finance'], axis=1)
final_dex_df.loc['Capital Efficiency'] = (final_dex_df.loc['GMV'] / final_dex_df.loc['TVL'])

#create cmaps for table
cmap = sns.diverging_palette(0, 150, s=75, as_cmap=True)
cmap_r = sns.diverging_palette(150, 0, s=75, as_cmap=True)

#transpose to format cell data by column
final_dex_df = final_dex_df.transpose()
final_dex_df = final_dex_df.drop(['Price', 'P/E', 'Supply Side Revenue (Daily)', 'Supply Side Revenue 90d % ∆', 'Protocol Revenue (Daily)', 'Protocol Revenue 90d % ∆'], axis=1)

#create style object
dex_df_styler = final_dex_df.style\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[0]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[1]))\
    .background_gradient(axis=0, cmap=cmap_r, subset=(final_dex_df.index, final_dex_df.columns[2]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[3]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[4]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[5]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[6]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[7]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[8]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_dex_df.index, final_dex_df.columns[9]))\
    .format({'Market Cap':'${0:,.0f}', 'Volume (Daily)':'${0:,.0f}', 'P/S':'{0:,.2f}', 'TVL':'${:,.0f}', 'TVL 90d % ∆':'{0:,.2%}', 'GMV':'${0:,.0f}',\
            'GMV 90d % ∆':'{0:,.2%}', 'Revenue (Daily)':'${0:,.0f}', 'Revenue 90d % ∆':'{0:,.2%}',\
            'Supply Side Revenue (Daily)':'${0:,.0f}', 'Supply Side Revenue 90d % ∆':'{0:,.2%}',\
            'Protocol Revenue (Daily)':'${0:,.0f}', 'Protocol Revenue 90d % ∆':'{0:,.2%}', 'Capital Efficiency':'{0:,.2f}'})


##Perps
final_perp_df = gather_sector_data(perp_protocols)

#drop protocols w/ no data
final_perp_df = final_perp_df.drop(['futureswap', 'perpetual-protocol'], axis=1)

#transpose so I can format data by column
final_perp_df = final_perp_df.transpose()
final_perp_df = final_perp_df.drop(['Price', 'P/E', 'Supply Side Revenue (Daily)', 'Supply Side Revenue 90d % ∆', 'Protocol Revenue (Daily)', 'Protocol Revenue 90d % ∆'], axis=1)

#color maps
cmap = sns.diverging_palette(0, 150, s=75, as_cmap=True)
cmap_r = sns.diverging_palette(150, 0, s=75, as_cmap=True)


#create style object
perp_df_styler = final_perp_df.style\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[0]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[1]))\
    .background_gradient(axis=0, cmap=cmap_r, subset=(final_perp_df.index, final_perp_df.columns[2]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[3]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[4]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[5]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[6]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[7]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_perp_df.index, final_perp_df.columns[8]))\
    .format({'Market Cap':'${0:,.0f}', 'Volume (Daily)':'${0:,.0f}', 'P/S':'{0:,.2f}', 'TVL':'${:,.0f}', 'TVL 90d % ∆':'{0:,.2%}', 'GMV':'${0:,.0f}',\
            'GMV 90d % ∆':'{0:,.2%}', 'Revenue (Daily)':'${0:,.0f}', 'Revenue 90d % ∆':'{0:,.2%}',\
            'Supply Side Revenue (Daily)':'${0:,.0f}', 'Supply Side Revenue 90d % ∆':'{0:,.2%}',\
            'Protocol Revenue (Daily)':'${0:,.0f}', 'Protocol Revenue 90d % ∆':'{0:,.2%}'})
    

#Layer Ones
final_l1_df = gather_sector_data(layer_one_protocols)

#transpose so I can format data by column
final_l1_df = final_l1_df.transpose()
final_l1_df = final_l1_df.drop(['Price', 'P/E', 'TVL', 'TVL 90d % ∆', 'GMV', 'GMV 90d % ∆', 'Supply Side Revenue (Daily)', 'Supply Side Revenue 90d % ∆', 'Protocol Revenue (Daily)', 'Protocol Revenue 90d % ∆'], axis=1)

#color maps
cmap = sns.diverging_palette(0, 150, s=75, as_cmap=True)
cmap_r = sns.diverging_palette(150, 0, s=75, as_cmap=True)


#create style object
l1_df_styler = final_l1_df.style\
    .background_gradient(axis=0, cmap=cmap, subset=(final_l1_df.index, final_l1_df.columns[0]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_l1_df.index, final_l1_df.columns[1]))\
    .background_gradient(axis=0, cmap=cmap_r, subset=(final_l1_df.index, final_l1_df.columns[2]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_l1_df.index, final_l1_df.columns[3]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_l1_df.index, final_l1_df.columns[4]))\
    .format({'Price':'${0:,.2f}', 'Market Cap':'${0:,.0f}', 'Volume (Daily)':'${0:,.0f}', 'P/S':'{0:,.2f}', 'Revenue (Daily)':'${0:,.0f}', 'Revenue 90d % ∆':'{0:,.2%}',\
            })

    
#Web3 Infrastructure
#call function for lending
final_web3_df = gather_sector_data(web3_protocols)

#customize df based on data
final_web3_df = final_web3_df.drop(['pocket-network', 'the-graph'], axis=1)
final_web3_df = final_web3_df.transpose()
final_web3_df = final_web3_df.drop(['Price', 'P/E', 'TVL', 'TVL 90d % ∆', 'GMV', 'GMV 90d % ∆'], axis=1)

#create cmaps for table
cmap = sns.diverging_palette(0, 150, s=75, as_cmap=True)
cmap_r = sns.diverging_palette(150, 0, s=75, as_cmap=True)

#create style object
web3_df_styler = final_web3_df.style\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[0]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[1]))\
    .background_gradient(axis=0, cmap=cmap_r, subset=(final_web3_df.index, final_web3_df.columns[2]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[3]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[4]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[5]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[6]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[7]))\
    .background_gradient(axis=0, cmap=cmap, subset=(final_web3_df.index, final_web3_df.columns[8]))\
    .format({'Market Cap':'${0:,.0f}', 'Volume (Daily)': '${0:,.0f}', 'P/S':'{0:,.2f}', 'Revenue (Daily)':'${0:,.0f}', 'Revenue 90d % ∆':'{0:,.2%}',\
            'Supply Side Revenue (Daily)':'${0:,.0f}', 'Supply Side Revenue 90d % ∆':'{0:,.2%}',\
            'Protocol Revenue (Daily)':'${0:,.0f}', 'Protocol Revenue 90d % ∆':'{0:,.2%}'})
    









#config page
st.set_page_config(page_title='Sector Fundamentals Dashboard', layout="centered")

#Header
st.title('Sector Fundamentals Dashboard')

st.write('\n \n This dashboard visualizes protocol fundamentals by sector, making it easy to compare competitors/peers. \n \
(Data Source: Token Terminal. In the future I will gather this data directly from our subgraphs.)\n \n')

st.markdown("""
    Skip to: \n \n
    [Lending Protocols](#lending-protocols) \n \n
    [Decentralized Exchange Protocols](#decentralized-exchange-protocols) \n \n
    [Perpetual Protocols](#perpetual-protocols) \n \n
    [Layer One Protocols](#layer-one-protocols) \n \n
    [Web3 Infrastructure](#web3-infrastructure) \n \n
    [Glossary](#glossary)
""", unsafe_allow_html=True)

##Lending
st.subheader('Lending Protocols:')
st.write(lending_df_styler, '\n')
col1, col2 = st.columns(2)
with col1:
    st.write('Market Cap:')
    st.bar_chart(final_lending_df['Market Cap'], use_container_width=True)
    st.write('Volume (Daily):')
    st.bar_chart(final_lending_df['Volume (Daily)'], use_container_width=True)
    st.write('Revenue (Daily):')
    st.bar_chart(final_lending_df['Revenue (Daily)'], use_container_width=True)

with col2:
    st.write('TVL:')
    st.bar_chart(final_lending_df['TVL'], use_container_width=True)
    st.write('GMV:')
    st.bar_chart(final_lending_df['GMV'], use_container_width=True)
    st.write('Collateral Ratio:')
    st.bar_chart(final_lending_df['Collateral Ratio'], use_container_width=True)

st.markdown("\n\n[Back to Top](#sector-fundamentals-dashboard)\n\n")


##DEX's
st.subheader('Decentralized Exchange Protocols:')
st.write(dex_df_styler, '\n')
col1, col2 = st.columns(2)
with col1:
    st.write('Market Cap:')
    st.bar_chart(final_dex_df['Market Cap'], use_container_width=True)
    st.write('Volume (Daily):')
    st.bar_chart(final_dex_df['Volume (Daily)'], use_container_width=True)
    st.write('Revenue (Daily):')
    st.bar_chart(final_dex_df['Revenue (Daily)'], use_container_width=True)

with col2:
    st.write('TVL:')
    st.bar_chart(final_dex_df['TVL'], use_container_width=True)
    st.write('GMV:')
    st.bar_chart(final_dex_df['GMV'], use_container_width=True)
    st.write('Capital Efficiency:')
    st.bar_chart(final_dex_df['Capital Efficiency'], use_container_width=True)

st.markdown("\n\n[Back to Top](#sector-fundamentals-dashboard)\n\n")


##Perps
st.subheader('Perpetual Protocols:')
st.write(perp_df_styler, '\n')
col1, col2 = st.columns(2)
with col1:
    st.write('Market Cap:')
    st.bar_chart(final_perp_df['Market Cap'], use_container_width=True)
    st.write('Volume (Daily):')
    st.bar_chart(final_perp_df['Volume (Daily)'], use_container_width=True)
    st.write('Revenue (Daily):')
    st.bar_chart(final_perp_df['Revenue (Daily)'], use_container_width=True)

with col2:
    st.write('TVL:')
    st.bar_chart(final_perp_df['TVL'], use_container_width=True)
    st.write('GMV:')
    st.bar_chart(final_perp_df['GMV'], use_container_width=True)

st.markdown("\n\n[Back to Top](#sector-fundamentals-dashboard)\n\n")


##L1's
st.subheader("Layer One Protocols:")
st.write(l1_df_styler, '\n')

st.write('Market Cap:')
st.bar_chart(final_l1_df['Market Cap'], use_container_width=True)
st.write('Volume (Daily):')
st.bar_chart(final_l1_df['Volume (Daily)'], use_container_width=True)
st.write('Revenue (Daily):')
st.bar_chart(final_l1_df['Revenue (Daily)'], use_container_width=True)

st.markdown("\n\n[Back to Top](#sector-fundamentals-dashboard)\n\n")


##Web3 Infra
st.subheader('Web3 Infrastructure:')
st.write(web3_df_styler, '\n')

st.write('Market Cap:')
st.bar_chart(final_web3_df['Market Cap'], use_container_width=True)
st.write('Volume (Daily):')
st.bar_chart(final_web3_df['Volume (Daily)'], use_container_width=True)
st.write('Revenue (Daily):')
st.bar_chart(final_web3_df['Revenue (Daily)'], use_container_width=True)

st.markdown("\n\n[Back to Top](#sector-fundamentals-dashboard)\n\n")


st.subheader('Glossary:')
st.write("""
Volume - Protocol token volume \n \n
P/S - fully diluted market cap divided by annualized total revenue. \n \n
TVL - total value locked is the value of assets deposited in the project’s smart contracts. \n \n
GMV - Gross Merchandise Value - equal to the total value of sales. For blockchains, it is the total transaction volume. For dapps, it the total trading volume of their product. For example, for lending protocols, it is the total borrowing volume, and for exchanges, it is the total trading volume. \n \n
Revenue - total revenue is equal to total fees paid by the users. \n \n
Supply Side Revenue - supply-side revenue is equal to the amount of revenue the project pays to the supply-side participants (for example, liquidity providers). \n
Protocol Revenue - Protocol revenue is equal to the amount of revenue that is distributed to tokenholders. \n \n
Collateral Ratio - TVL / GMV \n \n
Capital Efficiency - GMV / TVL

""")

st.markdown("\n\n[Back to Top](#sector-fundamentals-dashboard)\n\n")




