from flask import *
from datetime import datetime
import pytz
import MetaTrader5 as mt5

app = Flask(__name__)
mt5.initialize()  # Initialize connection with MetaTrader 5


@app.route('/tradingview', methods=['GET', 'POST'])
def home():
    """Main endpoint to receive TradingView alerts via webhook.

    Processes buy/sell signals and manages orders in MetaTrader 5.
    Returns received data for confirmation.
    """
    json_data = request.json
    webhook = {
        'ticker': str(json_data["ticker"]),  # Financial asset (e.g., EURUSD)
        'price': str(json_data["price"]),  # Alert price
        'order': str(json_data["order"]),  # Order type (e.g., market)
        'order_type': str(json_data["order_type"])  # Specific signal (e.g., SarBUY)
    }

    print('-' * 40)
    print(f"Signal received: {webhook} || {time_now()}")  # Formatted log
    print('-' * 40)

    # Decision logic based on alert type
    if webhook['order_type'] in ['SarBUY', 'SarSELL']:
        sending_order(webhook)  # Execute new order

    elif 'Close entry' in webhook['order_type']:
        position = mt5.positions_get()  # Check open positions
        if position == ():  # Check if open orders tuple is empty
            print(f"ERROR: No open orders to close! || {time_now()}")
        else:
            close_position(webhook, position)  # Close existing position

    elif webhook['order_type'] in ['StopCompra', 'StopVenda']:
        print(f"ALERT: Stop Loss triggered for {webhook['ticker']} || {time_now()}")
        position = mt5.positions_get()
        if position == ():  # Check if open orders tuple is empty
            print(f"ERROR: No open orders to close! || {time_now()}")
        else:
            close_position(webhook, position)

    return webhook  # Confirm webhook reception


def sending_order(data):
    """Execute buy/sell orders in MetaTrader 5.

    Args:
        data (dict): Dictionary with webhook information (ticker, order_type, etc)
    """
    ticker = data['ticker']
    price = mt5.symbol_info_tick(ticker).ask if data['order_type'] == 'SarBUY' else mt5.symbol_info_tick(ticker).bid

    order = {
        'action': mt5.TRADE_ACTION_DEAL,  # Immediate market operation
        'symbol': ticker,
        'volume': 1.0,  # Standard lot (1 contract)
        'type': mt5.ORDER_TYPE_BUY if data['order_type'] == 'SarBUY' else mt5.ORDER_TYPE_SELL,
        'price': price,  # Current asset price
        'deviation': 30,  # Slippage tolerance (30 points)
        'magic': 1,  # Unique strategy identifier
        'comment': 'Entry Trade',  # Operation description
        'type_time': mt5.ORDER_TIME_GTC,  # Valid until canceled
        'type_filling': mt5.ORDER_FILLING_IOC  # Immediate execution or cancel
    }

    mt5.order_send(order)  # Send order to MT5


def close_position(data, position_close):
    """Close existing positions in MetaTrader 5.

    Args:
        data (dict): Webhook information
        position_close (list): List of open positions
    """
    for position in position_close:
        if data['ticker'] in position.symbol:  # Check matching asset
            tick = mt5.symbol_info_tick(position.symbol)

            # Define closing price based on position type
            closing_price = tick.ask if position.type == 1 else tick.bid

            close_order = {
                'action': mt5.TRADE_ACTION_DEAL,  # Action to execute immediate order
                'position': position.ticket,  # MT5 position ID
                'symbol': position.symbol,  # Asset symbol (e.g., "EURUSD")
                'volume': position.volume,  # Position volume (full closure)
                'type': mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
                # /\ Define inverse order type (buy to close sell and vice versa)
                'price': closing_price,  # Current price to close position
                'deviation': 20,  # Allowed slippage (20 points)
                'magic': 100,  # Closing operation identifier
                'comment': 'Close Trade',  # MT5 operation description
                'type_time': mt5.ORDER_TIME_GTC,  # Valid until manual cancellation
                'type_filling': mt5.ORDER_FILLING_IOC  # Immediate execution or cancel
            }

            mt5.order_send(close_order)
            print(f"Order closed: {data['ticker']} ({data['order_type']}) || {time_now()}")


def time_now():
    """Returns current time in Brazil/East timezone (forex market time).

    Returns:
        str: Formatted time (HH:MM:SS)
    """
    timezone = pytz.timezone('Brazil/East')
    return datetime.now(timezone).strftime('%H:%M:%S')


if __name__ == '__main__':
    app.run(debug=True)  # Run Flask server in development mode
