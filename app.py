import matplotlib.pyplot as plt
from binance.client import Client
import pandas as pd
import streamlit as st

def get_top_returns(timeframe, lookback_period, nlargest):
    api_key = "698fxbgZzGtMht0gbeAJYsNgd93qX1oNbNSJTjqzzisb6wRvsm1VFhUPn8GlHAZr"
    api_secret = "Rqi2tpN8SoRqImbFhrxr2KGWPzBwU44Iq4yUf7acsq8Zz0kPBXXOX7wAuQTGpZUy"
    
    client = Client(api_key, api_secret)
    
    info = client.get_exchange_info()
    symbols = [x['symbol'] for x in info['symbols']]
    exclude = ['UP', 'DOWN', 'BEAR', 'BULL']
    non_lev = [symbol for symbol in symbols if all(excludes not in symbol for excludes in exclude)]
    
    relevant = [symbol for symbol in non_lev if symbol.endswith('USDT')]
    
    klines = {}
    
    with st.spinner("Please Wait while we Fetch Data from the Binance Exchange ..."):
        progress_bar = st.progress(0)
        progress_text = st.empty()
        for i, symbol in enumerate(relevant):
            klines[symbol] = client.get_historical_klines(symbol, timeframe, f'{lookback_period} min ago UTC')
            progress_bar.progress((i + 1) / len(relevant))
            progress_text.text(f"Progress: {i + 1} / {len(relevant)}")
    
    returns, symbols = [], []
    for symbol in relevant:
        if len(klines[symbol]) > 0:
            cumret = (pd.DataFrame(klines[symbol])[4].astype(float).pct_change() + 1).prod() - 1
            returns.append(cumret)
            symbols.append(symbol)
    
    retdf = pd.DataFrame(returns, index=symbols, columns=['ret'])
    top_returns = retdf.ret.nlargest(nlargest)
    
    return top_returns

def plot_price_chart(symbol):
    api_key = "698fxbgZzGtMht0gbeAJYsNgd93qX1oNbNSJTjqzzisb6wRvsm1VFhUPn8GlHAZr"
    api_secret = "Rqi2tpN8SoRqImbFhrxr2KGWPzBwU44Iq4yUf7acsq8Zz0kPBXXOX7wAuQTGpZUy"
    
    client = Client(api_key, api_secret)
    
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
    df = pd.DataFrame(klines, columns=["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"])
    df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
    df.set_index("Open Time", inplace=True)
    
    fig, ax = plt.subplots()
    ax.plot(df["Close"])
    ax.set(xlabel="Time", ylabel="Price", title=f"{symbol} Price Chart")
    ax.grid()
    
    return fig

def main():
    st.title("Profitable USDT-Pair Finder")
    st.subheader("Based on Data from Binance Exchange")
    st.divider()
    
    a,b,c = st.columns(3)
    with a:
        timeframe = st.radio("Select timeframe (minutes)", ['1m', '5m', '15m', '30m', '1h'])    
    with b:
        lookback_period = st.radio("Select lookback period (minutes)", [30, 60, 180, 360, 1440])        
    with c:
        nlargest = st.radio("Select number of pairs to display", [5, 10, 15, 20, 25])  
    
    show_table = False
    
    if st.button("Get Top Pairs"):
        top_returns = get_top_returns(timeframe, lookback_period, nlargest)
        show_table = True
    
    if show_table:
        st.table(top_returns)
        
        col1, col2= st.columns([1,5])
        
        if col1.button("Reset Data"):
            show_table = False
            st.experimental_rerun()
        
        if top_returns.shape[0] > 0:
            top_symbol = top_returns.index[0]
            fig = plot_price_chart(top_symbol)
            col2.pyplot(fig)

if __name__ == "__main__":
    main()
