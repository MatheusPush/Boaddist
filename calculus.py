import pandas as pd
import numpy as np
import talib
import plotly.plotly as py
import plotly.graph_objs as go
from datetime import datetime


def find_filters(source, bottoms, sta):
	filters = {}
	acc = 0

	for f in sta['Names']:
		sub_filters = filters.copy()
		sub_filters[f] = sta[sta['Names'] == f]['Is'].values[0]

		bottoms_f = bottoms
		for sf in sub_filters.keys():
			bottoms_f = bottoms_f[bottoms_f[sf] == sub_filters[sf]]
		bottoms_f_in_bottoms = len(bottoms_f) / len(bottoms)

		source_minus_bottom = pd.concat([source, bottoms]).drop_duplicates(keep=False)
		# source_minus_bottom = source[source['Bottom'] == False]
		source_minus_bottom_f = source_minus_bottom
		for sf in sub_filters.keys():
			source_minus_bottom_f = source_minus_bottom_f[source_minus_bottom_f[sf] == sub_filters[sf]]
		source_minus_bottom_f_in_source_minus_bottom = len(source_minus_bottom_f) / len(source_minus_bottom)

		new_acc = (2 * (1 - source_minus_bottom_f_in_source_minus_bottom) + bottoms_f_in_bottoms) / 3

		if new_acc > acc:
			acc = new_acc
			filters = sub_filters
			print(filters)
			print("Acc: " + format(acc, '.2f'))
		else:
			break

	return filters


def stat2(source, bottom):
	proportion = len(bottom) / len(source)
	print("% Proportion: " + format(proportion, '.4f'))
	names = []
	n = []
	in_source = []
	in_bottom = []
	in_bottom_to_source = []
	in_bottom_no_source = []
	factor = []
	for column in list(source):
		if column != 'Date' and column != 'Close' and column != 'IS_TOP' and column != 'IS_BOTTOM':
			source_true = len(source[source[column] == True]) / len(source[column])
			bottom_true = len(bottom[bottom[column] == True]) / len(bottom[column])
			names.append(column)
			n.append(bottom_true >= 0.5)
			if bottom_true < 0.5:
				source_true = 1 - source_true
				bottom_true = 1 - bottom_true
			in_source.append(source_true)
			in_bottom.append(bottom_true)
			bottom_to_source = bottom_true * proportion
			in_bottom_to_source.append(bottom_to_source)
			bottom_no_source = (source_true - bottom_to_source) / (1 - proportion)
			in_bottom_no_source.append(bottom_no_source)
			factor.append((2 * (1 - bottom_no_source) + bottom_true) / 3)
	return pd.DataFrame({"Names": names, "Is": n, "In Source": in_source, "In Bottom": in_bottom,
						 "In Bottom to Source": in_bottom_to_source, "In Bottom no Source": in_bottom_no_source,
						 "Factor": factor})


def new_stat(source, compare, filters):
	compare_source = len(compare) / len(source)

	print("% of Compare on Source: " + format(compare_source, '.4f'))

	names = []
	n = []
	in_source = []
	in_compare = []
	acc = []

	for column in list(source):
		if column != 'Date' and column != 'TOPS_BOTTOMS' and column not in filters.keys():
			source_true = len(source[source[column] == True]) / len(source[column])
			compare_true = len(compare[compare[column] == True]) / len(compare[column])
			names.append(column)

			n.append(compare_true >= 0.5)

			if compare_true < 0.5:
				source_true = 1 - source_true
				compare_true = 1 - compare_true

			in_source.append(source_true)
			in_compare.append(compare_true)

			sub_acc = compare_true * compare_source

			acc.append(sub_acc / source_true)

	return pd.DataFrame({"Names": names, "Is": n, "In Source": in_source, "In_Compare": in_compare, "Acc": acc})


def statistcs(source):
	for column in list(source):
		if column != 'Date' and column != 'TOPS_BOTTOMS':
			print("COLUMN: \t" + column)
			true = len(source[source[column] == True]) / len(source[column])
			print("\t\t\tTRUE PCT: " + format(true, '.4f'))


def statistcs_filter(source, filters):
	total = len(source)

	for f in filters.keys():
		source = source[source[f] == filters[f]]

	print("PCT: " + format(len(source) / total, '.4f'))

	return source


def averages(source, type, periods, basis):
	price = source[basis]

	for p in periods:
		sma_name = basis + '_' + type + '_' + str(p)
		source = source.join(pd.Series(getattr(talib, type)(price, p), name=sma_name))

	return source


def hilo(source, type, p):
	hi = source['High']
	lo = source['Low']

	hi_name = type + '_HI_' + str(p)
	lo_name = type + '_LO_' + str(p)
	source = source.join(pd.Series(getattr(talib, type)(hi, p), name=hi_name))
	source = source.join(pd.Series(getattr(talib, type)(lo, p), name=lo_name))

	return source


def didi(source, short, mid, long, type):
	price = source['Close']

	short_sma = getattr(talib, type)(price, short)
	mid_sma = getattr(talib, type)(price, mid)
	long_sma = getattr(talib, type)(price, long)
	didi_short = short_sma - mid_sma
	didi_long = long_sma - mid_sma

	long_name = "DIDI_LONG_" + str(short) + "/" + str(mid) + "/" + str(long) + "_TYPE" + type
	short_name = "DIDI_SHORT_" + str(short) + "/" + str(mid) + "/" + str(long) + "_TYPE" + type

	source = source.join(pd.Series(didi_short, name=short_name))
	source = source.join(pd.Series(didi_long, name=long_name))

	return source


# ADXR?			> https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/momentum_indicators.md
def dmi(source, dmi_period, dmi_smooth):
	minus_name = "MINUS_DI_" + str(dmi_period) + "_" + str(dmi_smooth)
	plus_name = "PLUS_DI_" + str(dmi_period) + "_" + str(dmi_smooth)
	adx_name = "ADX_" + str(dmi_period) + "_" + str(dmi_smooth)

	source = source.join(
		pd.Series(talib.MINUS_DI(source['High'], source['Low'], source['Close'], timeperiod=dmi_period),
				  name=minus_name))
	source = source.join(pd.Series(talib.PLUS_DI(source['High'], source['Low'], source['Close'], timeperiod=dmi_period),
								   name=plus_name))
	source = source.join(pd.Series(talib.ADX(source['High'], source['Low'], source['Close'], timeperiod=dmi_smooth),
								   name=adx_name))

	return source


def bbands(source, p, d, i):
	price = source['Close']

	bbands_name = '_TYPE' + str(i) + '_' + str(p) + 'P_' + str(d) + 'DEV'
	upperband, middleband, lowerband = talib.BBANDS(price, p, d, d, matype=i)
	source = source.join(pd.Series(upperband, name='UPPERBAND' + bbands_name))
	source = source.join(pd.Series(lowerband, name='LOWERBAND' + bbands_name))

	return source


def stoch(source, fastk_p, slow_p, type):
	high = source['High']
	low = source['Low']
	close = source['Close']

	stoch_name = 'STOCH_' + str(fastk_p) + 'FAST_' + str(slow_p) + 'SLOW_TYPE' + str(type) + '_'
	slowk, slowd = talib.STOCH(high, low, close, fastk_p, slow_p, type, slow_p, type)
	source = source.join(pd.Series(slowk, name=stoch_name + '%K'))
	source = source.join(pd.Series(slowd, name=stoch_name + '%D'))

	return source


def rsi(source, p):
	price = source['Close']

	rsi_name = 'RSI_' + str(p)
	rsi = talib.RSI(price, p)
	source = source.join(pd.Series(rsi, name=rsi_name))

	return source


def trix(source, p):
	price = source['Close']

	trix_name = 'TRIX_' + str(p)
	rsi = talib.TRIX(price, p)
	source = source.join(pd.Series(rsi, name=trix_name))

	return source


def classification(source, size):
	size2 = size - 1
	top = [None] * size2
	bottom = [None] * size2

	for i in range(size2, len(source) - size2):
		# Top Class
		is_top, is_bottom = classify(source.iloc[i - size2:i + size].reset_index(), size2)
		top.append(is_top)
		bottom.append(is_bottom)

	top += [None] * size2
	bottom += [None] * size2

	source = source.join(pd.Series(top, name='IS_TOP'))
	source = source.join(pd.Series(bottom, name='IS_BOTTOM'))

	return source


def classify(array: pd.DataFrame, size):
	top_idx = array['High'].idxmax()
	bottom_idx = array['Low'].idxmin()

	return int(top_idx == size), int(bottom_idx == size)


'''

print("\nBOTTOMS:")
# statistcs(bottoms)
filters = {'DIDI_LONG_20/8_ABOVE_0': True, 'DIDI_SHORT_8/20_ABOVE_0': False,
		   'DIDI_SHORT_3/8_OVER_DIDI_LONG_20/8': False, 'DIDI_LONG_13/6_ABOVE_0': True,
		   'DIDI_SHORT_2/6_OVER_DIDI_LONG_13/6': False, 'DIDI_SHORT_3/8_ABOVE_0': False, 'DIDI_LONG_8/3_ABOVE_0': True,
		   'DIDI_SHORT_1/3_OVER_DIDI_LONG_8/3': False}
filtereds = statistcs_filter(bottoms, filters)

# PLOTLY

trace_filtereds = go.Scatter(
	x=filtereds['Date'],
	y=filtereds['Close'],
	mode='markers',
	name='filtereds',
	marker=dict(
		size=5,
		color='rgba(255, 0, 0, .9)',
		line=dict(
			width=1,
		)
	)
)

trace_bottoms = go.Scatter(
	x=bottoms['Date'],
	y=bottoms['Close'],
	mode='markers',
	name='bottoms',
	marker=dict(
		size=5,
		color='rgba(0, 255, 0, .9)',
		line=dict(
			width=1,
		)
	)
)

trace_tops = go.Scatter(
	x=tops['Date'],
	y=tops['Close'],
	mode='markers',
	name='bottoms',
	marker=dict(
		size=5,
		color='rgba(0, 0, 0, .9)',
		line=dict(
			width=1,
		)
	)
)

trace_source = go.Scatter(
	x=source['Date'],
	y=source['Close'],
	mode='lines',
	name='source'
)

data = [trace_source, trace_bottoms, trace_tops]
py.plot(data, filename='scatter-mode')

# print("\nTOPS:")
# statistcs(tops)

'''
