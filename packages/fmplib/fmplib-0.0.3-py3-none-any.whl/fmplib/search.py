import requests
import os

from .const import _BASE_URL_V3_, _BASE_URL_V4_, _BASE_URL_STABLE_
from .fmputils import is_valid_date

class FmpLib:
    def __init__(self, api_key: str = None):
        self._api_key = api_key or os.getenv("FMP_API_KEY")
        if not self._api_key:
            raise ValueError("The FMP API key is required. Set FMP_API_KEY in your .env file or pass it as an argument.")
    #
    # Stock list section
    # https://site.financialmodelingprep.com/developer/docs#stock-list
    #
    
    def get_stock_list(self):
        """
        Find symbols for traded and non-traded stocks with our Symbol List. 
        This comprehensive list includes over 80,000 stocks.
        Retourne:
            json format
        """
        endpoint = f"{_BASE_URL_STABLE_}/stock-list"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_etf_list(self):
        """
        Get a full list of ETFs FMP cover, including Name, Symbol, Exchange, and Price.

        Retourne:
            json format
        """
        endpoint = f"{_BASE_URL_V3_}/etf/list"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_statement_symbols_list(self):
        """
        Get all companies with financial statements available on FMP API

        Retourne:
            json format
        """
        endpoint = f"{_BASE_URL_V3_}/financial-statement-symbol-lists"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_CoT_report(self):
        """
        Get Commitment of Traders Report, a weekly report from the Commodity Futures Trading Commission (CFTC) that provides insights into the positions of market participants in various markets.

        Retourne:
            json format
        """
        endpoint = f"{_BASE_URL_V4_}/commitment_of_traders_report/lists"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    #
    # Quote section
    # https://site.financialmodelingprep.com/developer/docs#quote
    #
     
    def get_price(self, ticker: str) -> int:
        """
        Get the price for a ticker. 

        Parameters:
            ticker: Le symbole boursier de l'entreprise (par exemple, "AAPL").

        Retourne:
            float: Un float représentant le prix du ticker.
        """
        if(isinstance(ticker, str)):
            endpoint = f"{_BASE_URL_STABLE_}/quote?symbol={ticker}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200 and len(response.json())>0:
                return response.json()[0]['price']
            else:
                response.raise_for_status()
        else:
            raise TypeError("Only strings are allowed") 
    
    def get_prices(self, tickers: list[str]) -> dict:
        """
        Get the prices for a list of tickers. 

        Parameters:
            tickers: List of stock symbols.

        Retourne:
            list[float]: List of tickers prices.
        """
        if(isinstance(tickers, list)):
            tickers = ",".join(tickers)
            endpoint = f"{_BASE_URL_V3_}/batch-quote?symbols={tickers}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                json_response = response.json()
                if json_response:
                    return {ticker_data['symbol']: ticker_data['price'] for ticker_data in response.json() if 'symbol' in ticker_data and 'price' in ticker_data}
                else:
                    return {}
            else:
                response.raise_for_status()
        else:
            raise TypeError("Only a list is allowed.") 
     
    def get_company_name(self, ticker: str) -> str:
        """
        Get the company name for a ticker. 

        Parameters:
            ticker: Company symbol e.g. "AAPL".

        Retourne:
            str: Company name.
        """
        if(isinstance(ticker, str)):
            endpoint = f"{_BASE_URL_STABLE_}/search-symbol?query={ticker}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200 and len(response.json())>0:
                return response.json()[0]['name']
            else:
                response.raise_for_status()
        else:
            raise TypeError("Only strings are allowed")

    def get_volume(self, ticker):
        """
        Get the volume for a ticker.

        Parameters:
            ticker: Ticker symbol 

        Retourne:
            int: The volume as an int 
        """
        if(isinstance(ticker, str)):
            endpoint = f"{_BASE_URL_V3_}/quote-short/{ticker}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200 and len(response.json())>0:
                return response.json()[0]['volume']
            else:
                response.raise_for_status()
        else:
            raise TypeError("Only strings are allowed") 
    
    def get_historical_price(self, ticker, from_date, to_date):
        """
        Fetch end of the day historical data for  specified ticker
        Endpoint documentation: https://site.financialmodelingprep.com/developer/docs/stable/historical-price-eod-light

        Parameters:
            ticker: Ticker symbol

        Return:
            dict: Dictionnary containing date(str):price(float) format
        """
        if(isinstance(ticker, str) and is_valid_date(from_date) and is_valid_date(to_date)):
            endpoint = f"{_BASE_URL_STABLE_}/quote-short/{ticker}"
            params = {"from": from_date,
                    "to": to_date,
                    "apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200 and len(response.json())>0:
                return {item["date"]: item["price"] for item in response.json()}
            else:
                response.raise_for_status()
        else:
            raise TypeError("Only strings are allowed or date is in the wrong format, should be YYYY-MM-DD") 
        
    def get_stock_full_quote(self, ticker):
        """
        Récupère les données de cotation en bourse pour une entreprise donnée.

        Parameters:
            ticker: Le symbole boursier de l'entreprise (par exemple, "AAPL").

        Retourne:
            dict: Un dictionnaire contenant les informations de la cotation.
        """
        if(isinstance(ticker, str)):
            endpoint = f"{_BASE_URL_V3_}/quote/{ticker}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
        else:
            raise TypeError("Only strings are allowed") 

    # Fonction pour récupérer les données de cotation en bourse d'une entreprise
    def get_stock_short_quote(self, ticker):
        """
        Get a simple quote for a stock, including the price, change, and volume. This endpoint can be used to get a quick snapshot of a stock's performance or to calculate its valuation.

        Parameters:
            ticker: Le symbole boursier de l'entreprise (par exemple, "AAPL").

        Retourne:
            dict: Un dictionnaire contenant les informations de la cotation.
        """
        if(isinstance(ticker, str)):
            endpoint = f"{_BASE_URL_V3_}/quote-short/{ticker}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
        else:
            raise TypeError("Only strings are allowed") 
        
    # Fonction pour récupérer en batch les données de cotation en bourse d'une entreprise
    def get_stock_batch_quote(self, tickers: list):
        """
        This endpoint gives you quotes for multiple stocks at once.

        Parameters:
            tickers: Liste de symboles

        Retourne:
            dict: Un dictionnaire contenant les informations de la cotation.
        """
        tickers = ",".join(tickers)
        endpoint = f"{_BASE_URL_V3_}/quote-short/{tickers}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Fonction pour récupérer les états financiers d'une entreprise
    def get_financial_statements(self, ticker, statement_type):
        """
        Récupère les états financiers (income statement, balance sheet, cash flow) d'une entreprise donnée.

        Parameters:
            ticker (str): Le symbole boursier de l'entreprise (par exemple, "AAPL").
            statement_type (str): Le type d'état financier ("income-statement", "balance-sheet-statement", "cash-flow-statement").

        Retourne:
            pd.DataFrame: Un DataFrame contenant les données de l'état financier.
        """
        endpoint = f"{_BASE_URL_V3_}/{statement_type}/{ticker}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Fonction pour récupérer les informations du profil d'une entreprise
    def get_company_profile(self, ticker):
        """
        Récupère les informations de profil d'une entreprise donnée.

        Parameters:
            ticker (str): Le symbole boursier de l'entreprise (par exemple, "AAPL").

        Retourne:
            dict: Un dictionnaire contenant les informations de profil de l'entreprise.
        """
        endpoint = f"{_BASE_URL_V3_}/profile/{ticker}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

        #
        # Commodities section
        # https://site.financialmodelingprep.com/developer/docs#commodities
        #

    #
    # Forex section
    # https://site.financialmodelingprep.com/developer/docs#forex
    #
    # Fonction pour récupérer une liste de toutes les devises disponibles sur le marché
    def get_forex_list(self):
        """
        Fournit une liste de toutes les paires de devises négociées sur le marché.

        Return :
            dict : Un dictionnaire contenant une liste de toutes les paires de FOREX.

        """
        
        endpoint = f"{_BASE_URL_V3_}/symbol/available-forex-currency-pairs"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Fonction pour récupérer les cotations de toutes les paires de devise sur le marché
    def get_forex_quotes(self):
        """
        Fournit les cotations complètes de toutes les paires de devises disponibles sur le marché.

        Return :
            dict : Un dictionnaire contenant les cotations des paire de devises.

        """
        endpoint = f"{_BASE_URL_V3_}/quotes/forex"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Fonction pour récupérer la cotation d'une paire de devises spécifique
    def get_full_forex_quote(self, ticker):
        """
        Fournit la cotation complète d'une paire de devises spécifique.

        Paramètres :
            ticker (str) : La nommation de la paire de devises (ex. EURUSD)

        Return :
            dict : Un dictionnaire contenant les cotations d'une paire de devises spécifique.

        """
        endpoint = f"{_BASE_URL_V3_}/quote/{ticker}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Fonction pour récupérer la cotation intrajournalière 
    def get_intraday_forex(self, ticker, timeframe, startdate, enddate):
        """
        Fournit la cotation intrajournalière d'une paire de devise spécifique

        Paramètres :
            ticker (str) : La nommation de la paire de devises (ex. EURUSD)
            timeframe (str): Le laps de temps (ex. 5min, 1hour)
            startdate (date): Date d'ouverture (ex. 2023-08-10)
            enddate (date): Date de fermeture (ex. 2023-09-10)

        Return :
            dict : Un dictionnaire contenant les cotations intrajournalières d'une paire de devises spécifique.

        """
        endpoint = f"{_BASE_URL_V3_}/historical-chart/{timeframe}/{ticker}?from={startdate}&to={enddate}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Fonction pour récupérer les données journalières d'une paire de devises 
    def get_forex_daily_price(self, ticker):
        """
        Fournit les données journalières générales d'une paire de devises.

        Paramètres : 
            ticker (str) : La nommation de la paire de devises (ex. EURUSD)

        Return : 
            dict : Un dictionnaire contenant les informations journalière de la paire de devises.
        """
        endpoint = f"{_BASE_URL_V3_}/historical-price-full/{ticker}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    #
    # Crypto section
    # https://site.financialmodelingprep.com/developer/docs#crypto
    #

    # Function that gets all the traded cryptocurrencies
    def get_crypto_list(self):
        """
        Gets data on all available cryptocurrencies on FMP

        Return : 
            dict : Dictionnary of all the available cryptocurrencies on FMP
        """
        endpoint = f"{_BASE_URL_V3_}/symbol/available-cryptocurrencies"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Function that gets quotes of all available cryptocurrencies
    def get_crypto_quotes(self):
        """
        Gets all the quotes of every crypto available on FMP

        Return : 
            dict : Dictionnary that return the quotes of all trading cryptocurrencies
        """
        endpoint = f"{_BASE_URL_V3_}/quotes/crypto"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Function to get a quote on a specific cryptocurrency
    def get_full_crypto_quote(self, ticker):
        """
        Gets the quotes of a specific cryptocurrency

        Paramètres : 
            ticker (str) : Symbol of the cryptocurrency (ex. BTCUSD)

        Return : 
            dict : Dictionnary with the full quotes of a specific cryptocurrency
        """
        endpoint = f"{_BASE_URL_V3_}/quote/{ticker}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Function to get intraday data for a specific cryptocurrency
    def get_intraday_crypto(self, symbol, timeframe, from_date, to_date):
        """
        Gets intraday data for a specific cryptocurrency

        Paramètres :
            symbol (str) : Symbol of the cryptocurrency (ex. BTCUSD)
            timeframe (str): The timeframe (ex. 5min, 1hour)
            from_tdate (date): Opening date (ex. 2023-08-10)
            to_date (date): Closing date (ex. 2023-09-10)

        Return :
            dict : A dictionnary containing intraday  quotes for a specific cryptocurrency

        """
        endpoint = f"{_BASE_URL_V3_}/historical-chart/{timeframe}/{symbol}?from={from_date}&to={to_date}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    # Function to get daily data of a specific cryptocurrency
    def get_crypto_daily_price(self, symbol):
        """
        Gets the daily data for a specific cryptocurrency

        Paramètres : 
            symbol (str) : Symbol of the cryptocurrency (ex. BTCUSD)

        Return : 
            dict : A dictionnary containing daily data for a specific cryptocurrency
        """
        endpoint = f"{_BASE_URL_V3_}/historical-price-full/{symbol}"
        params = {"apikey": self._api_key}
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    #
    # Constituents section
    # https://site.financialmodelingprep.com/developer/docs#constituents
    #

    def get_SP500_constituents(self):
            """
            Get a list of all companies that are included in the S&P 500 index.

            Return:
                json
            """
            endpoint = f"{_BASE_URL_V3_}/sp500_constituent"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

    #
    # Senate section
    # https://site.financialmodelingprep.com/developer/docs#senate
    #

    # Function that tracks the activity of the US Senators
    def get_senate_trading(self, ticker):
            """
            Get a list of all the activity of the US Senators for a specific stock

            Parameters:
                ticker : stock symbol (ex. RIVN)

            Return:
                dict : a dictionnary with the US senators activity for a certain stock
            """
            endpoint = f"{_BASE_URL_V4_}/senate-trading?symbol={ticker}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

    # Function that tracks the activity of the US Senators with the FMP Senate RSS Feed
    def get_senate_trading_rss_feed(self, page_number):
            """
            Get a list of all the activity of the US Senators for a specific stock

            Parameters:
                page_number : page number of the RSS feed (ex. 5)

            Return:
                dict : a dictionnary with the US senators activity for a certain page
            """
            endpoint = f"{_BASE_URL_V4_}/senate-trading-rss-feed?page={page_number}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

    # Function that show the House disclosure for a certain stock
    def get_house_disclosure(self, ticker):
            """
            House disclosure

            Parameters:
                ticker : stock symbol (ex. RIVN)

            Return:
                dict : a dictionnary with the US House disclosure for a certain stock
            """
            endpoint = f"{_BASE_URL_V4_}/senate-disclosure?symbol={ticker}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    # Function that show the House disclosure with the FMP RSS Feed
    def get_house_disclosure_rss_feed(self, page_number):
            """
            Shows the House disclosure with FMP's RSS Feed

            Parameters:
                page_number : page number of the RSS feed (ex. 5)

            Return:
                dict : a dictionnary with the House disclosure for a certain page
            """
            endpoint = f"{_BASE_URL_V4_}/senate-disclosure-rss-feed?page={page_number}"
            params = {"apikey": self._api_key}
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()