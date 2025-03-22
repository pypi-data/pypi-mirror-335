import array
from collections import OrderedDict
import asyncio
import datetime as dt
import json
from fastapi import FastAPI
from ib_async import *
import logging
from loguru import logger
import pytz
from sqlalchemy.orm import Session
from optrabot.broker.brokerconnector import BrokerConnector
from optrabot import schemas
from optrabot.broker.brokerfactory import BrokerFactory
from optrabot.marketdatatype import MarketDataType
from optrabot.optionhelper import OptionHelper
import optrabot.config as optrabotcfg
from optrabot.trademanager import TradeManager
from optrabot.tradetemplate.templatefactory import Template
import optrabot.symbolinfo as symbolInfo
from .tradinghubclient import TradinghubClient
import pkg_resources
from .database import *
from . import crud
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def get_version() -> str:
	"""
	Returns the version of the package
	"""
	try:
		return pkg_resources.get_distribution('optrabot').version
	except pkg_resources.DistributionNotFound:
		return '0.14.0' # Set Version to 0.13.9 for the local development environment

class OptraBot():
	def __init__(self, app: FastAPI):
		self.app = app
		self._apiKey = None
		self.thc : TradinghubClient = None
		self._tradingEnabled = False
		self._marketDataType : MarketDataType = None
		self.Version = get_version()
		self._backgroundScheduler = AsyncIOScheduler()
		self._backgroundScheduler.start()
		#logging.getLogger('apscheduler').setLevel(logging.ERROR) # Prevents unnecessary logging from apscheduler
			
	def __setitem__(self, key, value):
		setattr(self, key, value)

	def __getitem__(self, key):
		return getattr(self, key)
	
	async def startup(self):
		logger.info('OptraBot {version}', version=self.Version)
		# Read Config
		conf = optrabotcfg.Config("config.yaml")
		optrabotcfg.appConfig = conf
		self['config'] = conf
		conf.logConfigurationData()
		conf.readTemplates()
		updateDatabase()
		self.thc = TradinghubClient(self)
		if self.thc._apiKey == None:
			return

		try:
			additional_data = {
				'instance_id': conf.getInstanceId(),
				'accounts': self._getConfiguredAccounts()
			}
			await self.thc.connect(additional_data)
		except Exception as excp:
			logger.error('Problem on Startup: {}', excp)
			logger.error('OptraBot halted!')
			return
		
		logger.info('Sucessfully connected to OptraBot Hub')
		await BrokerFactory().createBrokerConnectors()
		self.thc.start_polling(self._backgroundScheduler)
		TradeManager()
		self._backgroundScheduler.add_job(self._statusInfo, 'interval', minutes=5, id='statusInfo', misfire_grace_time=None)
		self._backgroundScheduler.add_job(self._new_day_start, 'cron', hour=0, minute=0, second=0, timezone=pytz.timezone('US/Eastern'), id='day_change', misfire_grace_time=None)

	async def shutdown(self):
		logger.info('Shutting down OptraBot')
		await self.thc.shutdown()
		TradeManager().shutdown()
		await BrokerFactory().shutdownBrokerConnectors()
		self._backgroundScheduler.shutdown()

	async def _new_day_start(self):
		"""
		Perform operations on start of a new day
		"""
		logger.debug('Performing Day Change operations')
		await BrokerFactory().new_day_start()

	def _statusInfo(self):
		siTradingEnabled = 'Yes' if self._tradingEnabled == True else 'No' 
		siPosition = 'Yes' if self.thc._position == True else 'No'
		siHubConnection = 'OK' if self.thc.isHubConnectionOK() == True else 'Problem!'

		managedTrades = TradeManager().getManagedTrades()
		activeTrades = 0
		for managedTrade in managedTrades:
			if managedTrade.isActive():
				activeTrades += 1

		logger.info(f'Status Info: Hub Connection: {siHubConnection} - Active Trades: {activeTrades}')

	def getMarketDataType(self) -> MarketDataType:
		""" Return the configured Market Data Type
		"""
		if self._marketDataType is None:
			config: Config = self['config']
			try:
				confMarketData = config.get('tws.marketdata')
			except KeyError as keyError:
				confMarketData = 'Delayed'
			self._marketDataType = MarketDataType()
			self._marketDataType.byString(confMarketData)
		return self._marketDataType
	
	async def _checkMarketData(self):
		""" Checks if the Market Data Subscription is as configured.
			It requests SPX Options Market Data and checks if the returned Market Data Type
			is Live Market data. If not, trading is prevented.
		"""
		self._tradingEnabled = False
		ib: IB = self['ib']
		if not ib.isConnected():
			return

		marketDataType = self.getMarketDataType()
		logger.debug("Requesting '{}' data from Interactive Brokers", marketDataType.toString())
		ib.reqMarketDataType(marketDataType.Value)

		symbolInformation = symbolInfo.symbol_infos['SPX']
		spx = Index('SPX', symbolInformation.exchange)
		await ib.qualifyContractsAsync(spx)
		for i in range(3):
			[ticker] = await ib.reqTickersAsync(spx)
			ibMarketDataType = MarketDataType(ticker.marketDataType)
			if ibMarketDataType.Value != marketDataType.Value:
				logger.error("IB returned '{}' data for SPX! Trading is deactivated!", ibMarketDataType.toString())
				return
			else:
				logger.info("Received '{}' market data for SPX as expected.", ibMarketDataType.toString())

			logger.debug("Ticker data: Last={} Close={} Market Price={}", ticker.last, ticker.close, ticker.marketPrice())	
			spxPrice = ticker.close
			if util.isNan(spxPrice):
				logger.debug("IB returned no SPX price but just NaN value for last price. Trading is deactivated!")
			else:
				break # no more loop required

		if util.isNan(spxPrice):
			logger.error("IB returned no SPX price, but just NaN value after 3 attempts! Trading is deactivated!")
			return

		chains = await ib.reqSecDefOptParamsAsync(spx.symbol, '', spx.secType, spx.conId)
		chain = next(c for c in chains if c.tradingClass == symbolInformation.trading_class and c.exchange == symbolInformation.exchange)
		if chain == None:
			logger.error("No Option Chain for SPXW and SMARE found! Not able to trade SPX options!")
			return

		current_date = dt.date.today()
		expiration = current_date.strftime('%Y%m%d')

		if int(chain.expirations[0]) > int(expiration):
			logger.warning('There are no SPX options expiring today!')
			expiration = chain.expirations[0]

		strikePrice = OptionHelper.roundToStrikePrice(spxPrice)
		logger.info("Requesting Short Put price of strike {}", strikePrice)
		shortPutContract = Option(spx.symbol, expiration, strikePrice, 'P', symbolInformation.exchange, tradingClass = symbolInformation.trading_class)
		await ib.qualifyContractsAsync(shortPutContract)
		if not OptionHelper.checkContractIsQualified(shortPutContract):
			return
		ticker = None
		[ticker] = await ib.reqTickersAsync(shortPutContract)
		ibMarketDataType = MarketDataType(ticker.marketDataType)
		if ibMarketDataType.Value != marketDataType.Value:
			logger.error("IB returned '{}' data for SPX Option! Trading is deactivated!", ibMarketDataType.toString())
			return
		else:
			logger.info("Received '{}' market data for SPX Option as expected.", ibMarketDataType.toString())
		
		optionPrice = ticker.close
		if util.isNan(optionPrice):
			logger.error("IB returned no price for the SPX option but just a NaN value. Trading is deactivated!")
			return

		logger.success("Market Data subscription checks passed successfully. Options Trading is enabled.")
		self._tradingEnabled = True

	def isTradingEnabled(self) -> bool:
		""" Returns true if trading is enabled after market data subscription checks have passed.
		"""
		return self._tradingEnabled

	def _getConfiguredAccounts(self) -> list:
		""" 
		Returns a list of configured accounts
		"""
		#conf: Config = self['config']
		conf: Config = optrabotcfg.appConfig
		configuredAccounts = None
		for item in conf.getTemplates():
			template : Template = item
			if configuredAccounts == None:
				configuredAccounts = [template.account]
			else:
				if not template.account in configuredAccounts:
					configuredAccounts.append(template.account)
		return configuredAccounts

	@logger.catch
	def handleTaskDone(self, task: asyncio.Task):
		if not task.cancelled():
			taskException = task.exception()
			if taskException != None:
				logger.error('Task Exception occured!')
				raise taskException