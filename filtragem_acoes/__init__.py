import pandas as pd
import yfinance as yf
import pathlib
from flask import *

filtragem_bp = Blueprint('filtragem', __name__)

@filtragem_bp.route('/')
def pagina_iframe_logado():
    actual_dir = pathlib.Path().absolute()
    path = f'{actual_dir}/data/statusinvest-busca-avancada.csv'
    print(path)
    print(gerar_filtragem(path))
    return 'ok'


def gerar_filtragem(path):

    dados = pd.read_csv(path, decimal="," , delimiter=";", thousands=".")

    selecao = dados[['TICKER', 'PRECO', 'DY', 'P/L', 'P/VP', 'MARG. LIQUIDA',
           'DIVIDA LIQUIDA / EBIT', 'ROE']]


    selecao.fillna(0, inplace=True)

    remover = selecao[selecao['PRECO'] == 0].index
    selecao.drop(remover, inplace=True)

    selecao.sort_values(by='DIVIDA LIQUIDA / EBIT', inplace=True)

    remover = selecao[selecao['DIVIDA LIQUIDA / EBIT'] > 4].index

    selecao.drop(remover, inplace=True)

    #remover a coluna preco
    selecao.drop('PRECO', axis=1, inplace=True)

    #remover as linhas que a coluna DY é igual 0
    selecao.drop(selecao[selecao['DY'] == 0].index, inplace=True)

    selecao.drop(index=selecao[selecao['P/L'] <= 0].index, inplace=True)

    selecao.drop(index=selecao[selecao['ROE'] <= 0].index, inplace=True)
    selecao.drop(index=selecao[selecao['DY'] < 6].index, inplace=True)

    selecao.sort_values('DY')

    tickers = [ x + ".SA" for x in selecao['TICKER']]

    median_dy_dict = {}

    for ticker in tickers:
        try:
            div = yf.download(ticker, start='2019-01-01', actions=True)
            if not div.empty and 'Dividends' in div:
                annual_dividends = div['Dividends'].resample('YE').sum()
                stock_prices = div['Adj Close']
                dividend_yield = annual_dividends / stock_prices.resample('YE').last()

                median_dy = dividend_yield.dropna().median()

                median_dy_dict[ticker] = median_dy

        except Exception as e:
            print(f"Erro ao processar {ticker}: {e}")

    for ticker, median_dy in median_dy_dict.items():
        print(f"{ticker}: {median_dy}")

    filtered_median_dy_dict = {
        ticker: median_dy for ticker, median_dy in median_dy_dict.items() if median_dy >= 0.01
    }

    sorted_stocks = dict(sorted(filtered_median_dy_dict.items(), key=lambda item: item[1], reverse=True))

    valuation_list = []

    for ticker, median_dy in sorted_stocks.items():
        try:
            stock_info = yf.Ticker(ticker)

            current_price = stock_info.info.get("currentPrice")

            valuation = (median_dy * current_price) / 0.06

            valuation_list.append(valuation)

            print(f"{ticker}: Mediana DY = {median_dy:.2%}, Valuation = {valuation:.2f}")

        except Exception as e:
            print(f"Erro ao processar {ticker}: {e}")


    valuation_df = pd.DataFrame({'Ticker': list(sorted_stocks.keys()), 'Mediana DY': list(sorted_stocks.values()), 'Valuation': valuation_list})

    valuation_list = []
    for index, row in selecao.iterrows():
      ticker = row['TICKER']
      try:
        median_dy = median_dy_dict[ticker + ".SA"]
        criteria_evaluation = {}

        #  Dividend Yield (DY)
        if row['DY'] >= median_dy * 1.2:  # DY 20% maior q a mediana
          criteria_evaluation['DY'] = 'Bom'
        elif row['DY'] >= median_dy_total:  # Pelo menos a mediana
          criteria_evaluation['DY'] = 'Ok'
        else:
          criteria_evaluation['DY'] = 'Ruim'

        #  P/L
        if row['P/L'] >= 10:
          criteria_evaluation['P/L'] = 'Bom'
        elif row['P/L'] <= 15:
          criteria_evaluation['P/L'] = 'Ok'
        else:
          criteria_evaluation['P/L'] = 'Ruim'

        #  P/VP
        if row['P/VP'] <= 1.5:
          criteria_evaluation['P/VP'] = 'Bom'
        elif row['P/VP'] <= 2:
          criteria_evaluation['P/VP'] = 'Ok'
        else:
          criteria_evaluation['P/VP'] = 'Ruim'

        #  Margem Liquida
        if row['MARG. LIQUIDA'] >= 0.20:
          criteria_evaluation['MARG. LIQUIDA'] = 'Bom'
        elif row['MARG. LIQUIDA'] >= 0.15:
          criteria_evaluation['MARG. LIQUIDA'] = 'Ok'
        else:
          criteria_evaluation['MARG. LIQUIDA'] = 'Ruim'

        #  ROE
        if row['ROE'] >= 0.20:
          criteria_evaluation['ROE'] = 'Bom'
        elif row['ROE'] >= 0.14:
          criteria_evaluation['ROE'] = 'Ok'
        else:
          criteria_evaluation['ROE'] = 'Ruim'

        #  Divida Liquida / EBIT
        if row['DIVIDA LIQUIDA / EBIT'] <= 1.5:
          criteria_evaluation['DIVIDA LIQUIDA / EBIT'] = 'Bom'
        elif row['DIVIDA LIQUIDA / EBIT'] <= 2.5:
          criteria_evaluation['DIVIDA LIQUIDA / EBIT'] = 'Ok'
        else:
          criteria_evaluation['DIVIDA LIQUIDA / EBIT'] = 'Ruim'

       # valuation = (row['DY'] * median_dy)
        current_price = stock_info.info.get("currentPrice")
        valuation = (median_dy * current_price) / 0.06
        valuation_list.append([ticker, row['DY'], median_dy, valuation, criteria_evaluation])
      except KeyError:
        print(f"Median DY not found for {ticker}")

    valuation_df = pd.DataFrame(valuation_list, columns=['Ticker', 'DY', 'Median DY', 'Valuation', 'Criterios Fundamentalistas'])
    valuation_df.sort_values('DY', ascending=False, inplace=True)

    valuation_df['Num_Criterios_Ruim'] = valuation_df['Criterios Fundamentalistas'].apply(lambda x: sum(value == 'Ruim' for value in x.values()))

    valuation_df_sorted = valuation_df.sort_values('Num_Criterios_Ruim')


    top_3_acoes = valuation_df_sorted.head(3)
    print(top_3_acoes)

