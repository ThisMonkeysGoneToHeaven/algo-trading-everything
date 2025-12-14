import yfinance as yf

df = yf.download("RELIANCE.NS", interval="5m", period="60d")

df = df.dropna().sort_index()
df.index = df.index.tz_convert("Asia/Kolkata")

df.to_csv("reliance_5m.csv")