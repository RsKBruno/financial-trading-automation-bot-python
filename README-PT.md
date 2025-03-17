**README.md**  

---

# Robô de Automação para Trading Financeiro 🤖💸  

![Python](https://img.shields.io/badge/Python-3.8+-blue)  
![MetaTrader5](https://img.shields.io/badge/MetaTrader5-ativo-brightgreen)  

### Este projeto automatiza operações no mercado financeiro **integrando duas ferramentas líderes**:  
- **TradingView**: Plataforma global para análise de ativos, gráficos em tempo real e geração de alertas técnicos (ex: sinais baseados em indicadores como SAR ou MACD).  
- **MetaTrader 5 (MT5)**: Plataforma profissional para execução de ordens em mercados como forex, ações e commodities, com recursos avançados de gerenciamento de posições.  

O robô atua como uma **ponte inteligente** entre essas tecnologias:  
1. **Recebe alertas do TradingView** via webhooks (notificações em formato JSON).  
2. **Processa sinais em tempo real** (ex: `SarBUY` para compra ou `SarSELL` para venda).  
3. **Executa ordens no MT5** automaticamente, reduzindo erros manuais e garantindo velocidade de resposta.  
4. **Gerencia riscos**: Fecha posições via stop loss ou reversões de tendência.  

---

## 🛠️ Pré-requisitos  
1. **MetaTrader 5**: Instalado e configurado.  
2. **Python 3.8+**: Com bibliotecas:  
   ```bash  
   pip install flask MetaTrader5 pytz  
   ```  
3. **Ngrok**: Para expor o servidor local à internet (tutorial [aqui](https://ngrok.com/docs)).  

---
## 🚀 Configuração +  Passo a passo para iniciar testes.  
1. **TradingView**:  
- Salve as estratégias fornecidas em Pine Script (linguagem de programação do TradingView para criação de estratégias) diretamente na plataforma, garantindo compatibilidade com o projeto.
- Fique atento às instruções de uso do Ngrok , detalhadas no tópico 3 abaixo. Elas são essenciais para garantir que tudo funcione corretamente.
  - Será fornecido um link específico (gerado pelo Ngrok) para você copiar e colar nos alertas criados no TradingView.
  - Para mais detalhes sobre a configuração, consulte as explicações completas na seção dedicada ao Ngrok.

---
2. **MetaTrader 5**:  
- Crie uma conta demo em uma corretora de sua preferência. As estratégias disponibilizadas para o projeto são voltadas para pares de moedas do mercado Forex.
- Habilite a API no MT5 para permitir a integração com Python. Para isso, abra o MT5 e siga o caminho: (`Ferramentas > Opções > API`).  

---
3. **Ngrok**:   
     Ferramenta que expõe seu servidor Flask local à internet, permitindo que o TradingView envie alertas para sua máquina.  
   - **Passo a passo**:  
     1. **Instale o Ngrok**:  
        Baixe em [https://ngrok.com](https://ngrok.com) e siga as instruções de instalação.  
     2. **Execute o comando**:  
        ```bash  
        ngrok http 5000  # Cria um túnel para o Flask (porta 5000)  
        ```  
        - Copie o endereço público gerado (ex: `https://abcd1234.ngrok.io`).  
     3. **Configure o TradingView**:  
        - Cole o endereço no campo de webhook do alerta:  
          ```  
          https://abcd1234.ngrok.io/tradingview  
          ```  
        - Note que no final do link público fornecido pelo ngrok, precisamos adicionar o texto `tradingview`
        pois no nosso script em python especificamos isso no Flask 
        `@app.route('/tradingview', methods=['GET', 'POST'])`

     4. **Teste**:  
        - Dispare um alerta no TradingView e verifique se o Flask responde (use os logs do terminal).  

   - **Dica**:  
     - O link do Ngrok muda a cada reinício. Atualize o webhook no TradingView se necessário.  
     - Use a versão gratuita para testes, mas teste também alternativas (ex: Cloudflare Tunnel) em produção. 

---
4. **Servidor Flask/Script em Python**:
    - Execute o script em Python e confira se logs estão sendo gerados no terminal após alertas enviarem o sinal.

---
5. **Observação**:
    - Em breve, disponibilizarei um vídeo autoexplicativo com todos os detalhes e o passo a passo da integração das tecnologias utilizadas. 

---
### 🎯 **Parâmetros Editáveis**  
---
#### **1. Personalização de Sinais**  
- **Nomes dos alertas**:  
  - Modifique os valores `SarBUY`, `SarSELL`, `Close entry`, etc., **diretamente no TradingView** para criar estratégias únicas.  
  - Exemplo de alerta customizado:  
    ```python
    # No TradingView:
    alertcondition(condition, title="Meu_Sinal_Customizado", message="Compra_MACD")
    ```  
    No código, basta atualizar as condições em `home()` para refletir o novo nome e nova lógica que desejar.  

#### **2. Configurações Técnicas**  
- **Volume**:  
  ```python
  # Na função sending_order e close_position
  'volume': 1.0  # Ajuste para microcontas (ex: 0.1) ou contas padrão (ex: 10.0)
  ```  
- **Tolerância (deslizamento)**:  
  ```python
  # Na função sending_order e close_position
  'deviation': 30  # Reduza em mercados voláteis (ex: 10 pontos)
  ```  

#### **3. Base para Estratégias Próprias**  
- **Expanda a lógica**:  
  - Adicione novos `elif` em `home()` para processar sinais como `MACD_Buy` ou `RSI_Sell`.  
  - Exemplo de extensão:  
    ```python
    elif webhook['order_type'] == 'MACD_Buy':
        sending_order_macd(webhook)  # Nova função para MACD 
    ```  
- **Gerenciamento de risco**:  
  - Integre `stop loss` dinâmico usando `mt5.symbol_info_tick().ask` ou `bid`


---

## 📚 Documentação Técnica  
### Fluxo de Dados:  
1. **Recepção de Sinais**:  
   ```python  
   @app.route('/tradingview', methods=['POST'])  
   def home():  
       # Processa JSON do TradingView e decide ações  
   ```  
2. **Abertura de Ordem**:  
   ```python  
   def sending_order(dados):  
       # Define parâmetros como preço (ask/bid), magic (identificador) e tolerância de deslizamento do preço da ordem 
   ```  
3. **Fechamento de Posição**:  
   ```python  
   def close_position(dados, position_close):  
       # Fecha ordens específicas usando o ticket da posição e magic=100  
   ```  

---

## ⚠️ Limitações  
- **Posições Simultâneas**: Não gerencia múltiplas ordens no mesmo ativo.  
- **Testes**: Recomenda-se usar contas demo.  

---

## 📄 Licença  
MIT License – Veja o arquivo `LICENSE` para detalhes.  

---

## 📞 Suporte  
- Reporte bugs ou dúvidas para melhorias do projeto.  
- **Aviso Legal**:  
  - Este projeto e os scripts disponibilizados **são exclusivamente para fins educacionais**.  
  - Operações no mercado financeiro envolvem **riscos financeiros significativos**, incluindo a possibilidade de perdas superiores ao capital investido.  
  - **Recomenda-se o uso de uma conta demonstrativa** para testes, conforme práticas de segurança recomendadas por regulamentações do setor.  
  - O autor **não se responsabiliza por decisões de investimento** baseadas neste projeto.    

---

**Autor**: Bruno Alves  
**Última Atualização**: 16/03/2025  

---

