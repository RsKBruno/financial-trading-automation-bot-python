from flask import *
from datetime import datetime
import pytz
import MetaTrader5 as mt5

app = Flask(__name__)
mt5.initialize()  # Inicializa a conexão com o MetaTrader 5


@app.route('/tradingview', methods=['GET', 'POST'])
def home():
    """Endpoint principal para receber alertas do TradingView via webhook.

    Processa sinais de compra/venda e gerencia ordens no MetaTrader 5.
    Retorna os dados recebidos para confirmação.
    """
    json_data = request.json
    webhook = {
        'ticker': str(json_data["ticker"]),  # Ativo financeiro (ex: EURUSD)
        'price': str(json_data["price"]),  # Preço do alerta
        'order': str(json_data["order"]),  # Tipo de ordem (ex: market)
        'order_type': str(json_data["order_type"])  # Sinal específico (ex: SarBUY)
    }

    print('-' * 40)
    print(f"Sinal recebido: {webhook} || {time_now()}")  # Log formatado
    print('-' * 40)

    # Lógica de decisão baseada no tipo de alerta
    if webhook['order_type'] in ['SarBUY', 'SarSELL']:
        sending_order(webhook)  # Executa nova ordem

    elif 'Close entry' in webhook['order_type']:
        position = mt5.positions_get()  # Verifica posições abertas
        if position == ():  # Verifica se a tupla de ordens abertas está vazia
            print(f"ERRO: Nenhuma ordem aberta para fechar! || {time_now()}")
        else:
            close_position(webhook, position)  # Fecha posição existente

    elif webhook['order_type'] in ['StopCompra', 'StopVenda']:
        print(f"ALERTA: Stop Loss atingido para {webhook['ticker']} || {time_now()}")
        position = mt5.positions_get()
        if position == ():  # Verifica se a tupla de ordens abertas está vazia
            print(f"ERRO: Nenhuma ordem aberta para fechar! || {time_now()}")
        else:
            close_position(webhook, position)

    return webhook  # Confirma recebimento do webhook


def sending_order(dados):
    """Executa ordens de compra/venda no MetaTrader 5.

    Args:
        dados (dict): Dicionário com informações do webhook (ticker, order_type, etc)
    """
    ticker = dados['ticker']
    preco = mt5.symbol_info_tick(ticker).ask if dados['order_type'] == 'SarBUY' else mt5.symbol_info_tick(ticker).bid

    ordem = {
        'action': mt5.TRADE_ACTION_DEAL,  # Operação imediata no mercado
        'symbol': ticker,
        'volume': 1.0,  # Lote padrão (1 contrato)
        'type': mt5.ORDER_TYPE_BUY if dados['order_type'] == 'SarBUY' else mt5.ORDER_TYPE_SELL,
        'price': preco,  # Preço atual do ativo
        'deviation': 30,  # Tolerância de deslizamento (30 pontos)
        'magic': 1,  # Identificador único da estratégia
        'comment': 'Entry Trade',  # Descrição da operação
        'type_time': mt5.ORDER_TIME_GTC,  # Válida até cancelamento
        'type_filling': mt5.ORDER_FILLING_IOC  # Execução imediata ou cancela
    }

    mt5.order_send(ordem)  # Envia ordem ao MT5


def close_position(dados, position_close):
    """Fecha posições existentes no MetaTrader 5.

    Args:
        dados (dict): Informações do webhook
        position_close (list): Lista de posições abertas
    """
    for posicao in position_close:
        if dados['ticker'] in posicao.symbol:  # Verifica ativo correspondente
            tick = mt5.symbol_info_tick(posicao.symbol)

            # Define preço de fechamento baseado no tipo da posição
            preco_fechamento = tick.ask if posicao.type == 1 else tick.bid

            fechar_ordem = {
                'action': mt5.TRADE_ACTION_DEAL,  # Ação para executar ordem imediata no mercado
                'position': posicao.ticket,  # ID único da posição a ser fechada (identificador do MT5)
                'symbol': posicao.symbol,  # Símbolo do ativo (ex: "EURUSD") [[7]]
                'volume': posicao.volume,  # Volume da posição (mesmo da ordem original para fechar totalmente)
                'type': mt5.ORDER_TYPE_BUY if posicao.type == 1 else mt5.ORDER_TYPE_SELL,
                # /\ Define tipo de ordem inversa (compra para fechar venda e vice-versa)
                'price': preco_fechamento,  # Preço atual para fechar a posição (ask para compra, bid para venda)
                'deviation': 20,  # Tolerância de deslizamento permitida (20 pontos)
                'magic': 100,  # Número para identificar operações de fechamento
                'comment': 'Close Trade',  # Descrição da operação no MT5
                'type_time': mt5.ORDER_TIME_GTC,  # Ordem válida até cancelamento manual
                'type_filling': mt5.ORDER_FILLING_IOC  # Executa imediatamente ou cancela (sem fila de espera)
            }

            mt5.order_send(fechar_ordem)
            print(f"Ordem fechada: {dados['ticker']} ({dados['order_type']}) || {time_now()}")


def time_now():
    """Retorna horário atual no Brasil(Brasília) (fuso horário do mercado forex).

    Returns:
        str: Hora formatada (HH:MM:SS)
    """
    fuso = pytz.timezone('Brazil/East')
    return datetime.now(fuso).strftime('%H:%M:%S')


if __name__ == '__main__':
    app.run(debug=True)  # Executa servidor Flask em modo de desenvolvimento