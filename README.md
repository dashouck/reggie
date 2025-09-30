# Reggie — Detecting Market Regimes to Reduce Cognitive Bias in Investment Decisions

Reggie is a research project and interactive tool designed to help retail investors recognize **market regime shifts** and avoid common cognitive biases such as panic selling and fear-driven buying. 
 
It combines **Hidden Markov Models (HMMs)** with well-established **technical indicators** to visualize market states and encourage more disciplined decision-making.

---

## 📄 Featured Paper

The ideas and methods behind Reggie are explained in detail in the accompanying paper:

➡️ [**Read the paper (PDF)**](docs/Reggie_John-Houck.pdf)

*Citation:*  
John Houck, *Combating Cognitive Bias in Financial Decision-Making with Regime Detection*, Georgia Tech, 2025.

---

## 🧑‍💻 Code Overview

All code lives in the [`src/`](src) directory:

- **`app.py`** — main entry point, a Dash web app with interactive Plotly charts  
- **`data.py`** — utilities for loading OHLCV data via `Tiingo`, with caching  
- **`regime_change.py`** — Hidden Markov Model–based regime detection  
- **`tech_analysis.py`** — technical indicators (SMA, Bollinger Bands, RSI, Stochastic)  
- **`tickers.txt`** — list of stock tickers for analysis  
- **`quotes.txt`** — inspirational investor quotes used in the UI  

### Flow
1. `data.py` fetches historical market data  
2. `regime_change.py` classifies bull/bear/neutral regimes  
3. `tech_analysis.py` overlays indicators  
4. `app.py` presents interactive dashboards in the browser  

---

## ▶️ Run the Dash App

Install dependencies (Python 3.10+ recommended):

```sh
pip install -r requirements.txt
```

Request a free api key from [Tiingo](https://www.tiingo.com/about/pricing) and paste it into the following file:

```sh
src/api_token.txt
```

Run the application (custom Plotly charts):

```sh
python src/app.py
``` 