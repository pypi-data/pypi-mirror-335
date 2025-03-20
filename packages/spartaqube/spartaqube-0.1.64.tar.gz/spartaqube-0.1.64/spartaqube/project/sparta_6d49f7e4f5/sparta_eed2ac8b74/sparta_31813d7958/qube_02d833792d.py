_M='{\n        "showTicks": True,\n        "renderTicks": {\n            "showTicks": True,\n            "divisions": 10,\n        },\n    }'
_L='Example to plot a simple shaded background chart with lightweight chart'
_K='12px'
_J='center'
_I='blue'
_H='font-size'
_G='text-align'
_F='color'
_E='from spartaqube import Spartaqube as Spartaqube'
_D='code'
_C='sub_description'
_B='description'
_A='title'
import json
from django.conf import settings as conf_settings
def sparta_edc59ce8d9(type='candlestick'):B='Example to plot a simple candlestick chart with lightweight chart';A=_E;C={_F:_I,_G:_J,_H:_K};D=_M;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  ohlcv=[apple_price_df['Open'], apple_price_df['High'], apple_price_df['Low'], apple_price_df['Close']], 
  title='Example candlestick',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with volumes",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  ohlcv=[apple_price_df['Open'], apple_price_df['High'], apple_price_df['Low'], apple_price_df['Close'], apple_price_df['Volume']], 
  title='Example candlestick',
  height=500
)
plot_example"""}]
def sparta_76f1053f28(type='line2'):A=_E;B={_F:_I,_G:_J,_H:_K};C=_M;return[{_A:f"{type.capitalize()}",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example {type}',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} two lines",_B:f"Example to plot multiple {type}s with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df[['Close', 'Open']], 
  title='Example {type}',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} two lines stacked",_B:f"Example to plot multiple {type}s with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df[['Close', 'Open']],
  stacked=True,
  title='Example {type}',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with time range",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""}]
def sparta_f2fbb54f18():return sparta_76f1053f28('line2')
def sparta_f8dbf805b8():return sparta_76f1053f28('bar2')
def sparta_79d2cdc75b():return sparta_76f1053f28('area2')
def sparta_69cb0e92a1():return sparta_76f1053f28('lollipop2')
def sparta_83932d8c8c():B='Example to plot a simple baseline chart with lightweight chart';A=_E;D={_F:_I,_G:_J,_H:_K};C='{\n    "baseline": [\n      \t{\n          "defaultBaselinePrice": 200,\n        },\n    ]\n    }';type='ts_baseline';return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example baseline',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom baseline",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example baseline',
  options={C},
  height=500
)
plot_example"""}]
def sparta_f5425df707():A=_E;C={_F:_I,_G:_J,_H:_K};B='{\n        "shadedBackground": {\n            "lowColor": "rgb(50, 50, 255)",\n            "highColor": "rgb(255, 50, 50)",\n            "opacity": 0.8,\n        },\n    }';type='ts_shaded';return[{_A:f"{type.capitalize()}",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  shaded_background=apple_price_df['Close'], 
  title='Example',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom colors",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  shaded_background=apple_price_df['Close'], 
  title='Example',
  options={B},
  height=500
)
plot_example"""}]
def sparta_3490a40462():A=_E;B={_F:_I,_G:_J,_H:_K};C=_M;type='performance';return[{_A:f"{type.capitalize()}",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example {type}',
  height=500
)
plot_example"""}]
def sparta_e69ad02972():A=_E;C={_F:_I,_G:_J,_H:_K};B='{\n        "areaBands": {\n            "fillColor": "#F5A623",\n            "color": "rgb(19, 40, 153)",\n            "lineColor": "rgb(208, 2, 27)",\n            "lineWidth": 3,\n            "custom_scale_axis": "Right",\n        },\n    }';type='ts_area_bands';return[{_A:f"{type.capitalize()}",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=[apple_price_df['Close'], apple_price_df['High'], apple_price_df['Low']], 
  title='Example',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom colors",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=[apple_price_df['Close'], apple_price_df['High'], apple_price_df['Low']], 
  options={B},
  height=500
)
plot_example"""}]