import pandas as pd
import calculus as cc
from datetime import datetime

def buy(cur_val, prev_val, stoch_rule, minus_di_rule, ma_rule):
	'''
	:param cur_val: Market and Indicators current data
	:param prev_val: Market and Indicators previous data
	:param stoch_rule: int,
		if 50: STOCH_5FAST_3SLOW_TYPE1_%K < 50
		if 30: STOCH_5FAST_3SLOW_TYPE1_%K < 30
		if 25: STOCH_5FAST_3SLOW_TYPE1_%K < 25
	:param minus_di_rule: int,
		if 30: MINUS_DI_3_20 > 30
		if 25: MINUS_DI_3_20 > 25
		if 20: MINUS_DI_3_20 > 20
	:param ma_rule: object,
		if WMA: Close_WMA_X will be used
		if SMA: Close_SMA_X will be used
	:return: Returns if is a moment to buy
	'''

	if cur_val['MINUS_DI_3_20'] > minus_di_rule:
		if cur_val['STOCH_5FAST_3SLOW_TYPE1_%K'] < stoch_rule:
			if cur_val['Close_' + ma_rule + '_9'] < cur_val['Close_' + ma_rule + '_14']:
				if cur_val['MINUS_DI_14_20'] > prev_val['MINUS_DI_14_20']:
					if cur_val['STOCH_5FAST_3SLOW_TYPE1_%K'] > prev_val['STOCH_5FAST_3SLOW_TYPE1_%K']:
						return True

	return False


def put_stop_sell_stoch(cur_val, prev_val, stoch_rule):
	if prev_val['STOCH_5FAST_3SLOW_TYPE1_%K'] > (100 - stoch_rule):
		if cur_val['STOCH_5FAST_3SLOW_TYPE1_%K'] < prev_val['STOCH_5FAST_3SLOW_TYPE1_%K']:
			return True

	return False


def sell(cur_val, prev_val, stoch_rule, minus_di_rule, ma_rule):
	if cur_val['PLUS_DI_3_20'] > minus_di_rule:															# +DI (3, 20) > 30, 25, 20
		if cur_val['STOCH_5FAST_3SLOW_TYPE1_%K'] > 100 - stoch_rule:									# Stoch (5, 3, EMA) > 50, 75, 80
			if cur_val['Close_' + ma_rule + '_9'] > cur_val['Close_' + ma_rule + '_14']:				# MA 9 > MA 14
				if cur_val['PLUS_DI_3_20'] > prev_val['PLUS_DI_3_20']:									# +DI (14, 20) Uptrend
					if cur_val['STOCH_5FAST_3SLOW_TYPE1_%K'] < prev_val['STOCH_5FAST_3SLOW_TYPE1_%K']:	# Stoch (5, 3, EMA) Downtrend
						return True

	return False


def put_stop_buy_stoch(cur_val, prev_val, stoch_rule):
	if prev_val['STOCH_5FAST_3SLOW_TYPE1_%K'] < (stoch_rule):
		if cur_val['STOCH_5FAST_3SLOW_TYPE1_%K'] > prev_val['STOCH_5FAST_3SLOW_TYPE1_%K']:
			return True

	return False


source = pd.read_csv('bmf/WDO_5MIN.csv')[-30570:].reset_index()  # 2500 -> 1 mês
source = source.drop(columns="index")

# DMIs
source = cc.dmi(source, 3, 20)
source = cc.dmi(source, 14, 20)

# MAs
source = cc.averages(source, 'SMA', [9, 14, 50, 100, 200], 'Close')
source = cc.averages(source, 'EMA', [9, 14], 'Close')
source = cc.averages(source, 'WMA', [9, 14], 'Close')
source = cc.averages(source, 'KAMA', [9, 14], 'Close')
source = cc.averages(source, 'DEMA', [9, 14], 'Close')
source = cc.averages(source, 'TEMA', [9, 14], 'Close')

# Stoch
source = cc.stoch(source, 5, 3, 1)

best_factor = 0
best_param = ''

# Results (Ago/2018 to Jan/2019):
# COMPRADO E VENDIDO:	[0.5 35 25 EMA] Mean: 115.75 Std: 83.41 Factor: 95.62
# COMPRADO:				[0.5 15 40 WMA] Mean: 62.00  Std: 78.01 Factor: 52.57
# VENDIDO:				[1.0 40 35 WMA]

# Results (Jan/2018 to Jan/2019):
# COMPRADO E VENDIDO:
# COMPRADO:				[0.0 0.5 45 25 WMA] Mean: 55.57  Std: 84.44 Factor: 37.96
# VENDIDO:

for entry_pts in [0, 1.0]:
	for stop_pts in [0.5, 1.0, 1.5]:
		for stoch_rule in [60, 55, 50]:
			for minus_di_rule in [15, 10, 5, 0]:
				for ma_rule in ['WMA', 'EMA', 'KAMA']:

					cur_position = 0  # no of contracts
					entry = 0
					stop_gain = 0
					stop_entry = 0
					balance = 0
					month = 0
					month_profit = []

					print('----------------------------------', entry_pts, stop_pts, stoch_rule, minus_di_rule, ma_rule)

					for i in range(200, len(source)):

						cur_val = source.iloc[i]
						prev_val = source.iloc[i-1]

						cur_date = datetime.strptime(cur_val['Date'].replace('\t', ''), '%Y.%m.%d %H:%M')

						# Restart month profit
						if cur_date.month != month:
							if month != 0:
								month_profit.append(balance)
							month = cur_date.month
							balance = 0

						# End operations
						if cur_date.hour == 18 and cur_date.minute == 10 and cur_position != 0:
							if cur_position > 0:

								#print(cur_val['Date'], '\tClose Buy @ ', cur_val['Close'], '>> Profit:', cur_position * (cur_val['Close'] - entry))
								balance += cur_position * (cur_val['Close'] - entry)
								cur_position = 0
								stop_gain = 0
								stop_entry = 0
								#print('\t\t\t\t\tBalance:', balance)

							elif cur_position < 0:

								#print(cur_val['Date'], '\tClose Sell @ ', cur_val['Close'], '>> Profit:', cur_position * (cur_val['Close'] - entry))
								balance += cur_position * (cur_val['Close'] - entry)
								cur_position = 0
								stop_gain = 0
								stop_entry = 0
								#print('\t\t\t\t\tBalance:', balance)

						# if cur_position == 0 or cur_position > 0:
						#
						# 	if stop_entry != 0 and cur_val['High'] > stop_entry:
						# 		#print(cur_val['Date'], '\tBuy @ ', stop_entry)
						# 		entry = stop_entry if cur_position == 0 else (abs(cur_position) * entry + stop_entry) / (abs(cur_position) + 1)
						# 		stop_entry = 0
						# 		cur_position += 1
						#
						# 	# signal
						# 	if buy(cur_val, prev_val, stoch_rule, minus_di_rule, ma_rule):
						# 		stop_entry = cur_val['Close'] if entry_pts == 0 else cur_val['High'] + entry_pts
						# 		#print(cur_val['Date'], '\tStop entry to Buy: ', stop_entry)
						# 		continue

						# O BUG QUE DEU BOM
						if cur_position == 0 or cur_position < 0:

							if stop_entry != 0 and cur_val['Low'] < stop_entry:
								#print(cur_val['Date'], '\tSell @ ', stop_entry)
								entry = stop_entry if cur_position == 0 else (abs(cur_position) * entry + stop_entry) / (abs(cur_position) + 1)
								stop_entry = 0
								cur_position -= 1

							# signal
							if sell(cur_val, prev_val, stoch_rule, minus_di_rule, ma_rule):
								stop_entry = cur_val['Close'] if entry_pts == 0 else cur_val['Low'] - entry_pts
								#print(cur_val['Date'], '\tStop entry to Sell: ', stop_entry)
								continue

						if cur_position > 0:

							if stop_gain != 0 and cur_val['Low'] <= stop_gain:
								#print(cur_val['Date'], '\tClose Buy @ ', stop_gain, '>> Profit:', cur_position * (stop_gain - entry))
								balance += cur_position * (stop_gain - entry)
								cur_position = 0
								stop_gain = 0
								#print('\t\t\t\t\tBalance:', balance)
							elif put_stop_sell_stoch(cur_val, prev_val, stoch_rule):
								stop_gain = cur_val['Low'] - stop_pts
								#print(cur_val['Date'], '\tPut Stop Sell @ ', stop_gain)

						elif cur_position < 0:

							if stop_gain != 0 and cur_val['High'] >= stop_gain:
								#print(cur_val['Date'], '\tClose Sell @ ', stop_gain, '>> Profit:', cur_position * (stop_gain - entry))
								balance += cur_position * (stop_gain - entry)
								cur_position = 0
								stop_gain = 0
								#print('\t\t\t\t\tBalance:', balance)
							elif put_stop_buy_stoch(cur_val, prev_val, stoch_rule):
								stop_gain = cur_val['High'] + stop_pts
								#print(cur_val['Date'], '\tPut Buy Sell @ ', stop_gain)

					month_df = pd.DataFrame({'V': month_profit})
					factor = month_df['V'].mean() * (1 - month_df['V'].std() ** 2 / 22500)

					print(month_profit)
					print(month_df['V'].mean(), month_df['V'].std())
					print('Factor:', factor)

					if factor > best_factor:
						best_factor = factor
						best_param = entry_pts, stop_pts, stoch_rule, minus_di_rule, ma_rule

print(best_factor)
print(best_param)

'''

Verificar horarios: Start 9h15/30/45, 10h Stop 17h00/30/45
Regra do Stoch só para o prev [20, 15, 10]
Quando comprar e quando vender (SMA 200, etc)
Breakeven
+ Regras de Alvo
Maior Loss e Maximo negativo

'''