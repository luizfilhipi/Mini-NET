## Visão Geral

Este projeto implementa uma aplicação de chat em Python com uma pilha de protocolos de rede customizada, construída com uma abordagem Top-Down. O objetivo é demonstrar o funcionamento das camadas de rede, garantindo a entrega, ordenação e integridade das mensagens através de UDP (`SOCK_DGRAM`), sem utilizar as garantias nativas do protocolo TCP. O sistema está preparado para funcionar de forma fiável sobre um canal de comunicação simulado que introduz perda de pacotes e corrupção de dados.

## Arquitetura e Encapsulamento

Os dados seguem o encapsulamento estrito (estrutura de "Bonecas Russas"):
`Quadro (Enlace) → Pacote (Rede) → Segmento (Transporte) → JSON (Aplicação)`.

**Camada de Aplicação:** Formatação das mensagens em JSON.
 
**Camada de Transporte:** Implementação de confiabilidade com temporizadores (Timeouts), números de sequência e ACKs (algoritmo Stop-and-Wait).

**Camada de Rede:** Endereçamento virtual (VIP), TTL (Time to Live) e encaminhamento através de um Roteador central.

**Camada de Enlace:** Verificação de integridade utilizando cálculo de Checksum/CRC32 (FCS) e endereçamento MAC fictício.

## Pré-requisitos

**Linguagem:** Python 3.8 ou superior.

**Dependências:** Apenas bibliotecas padrão do Python (socket, threading, json, zlib, time, random, etc.). Nenhuma biblioteca externa é necessária.

## Como Executar o Projeto

O sistema é composto por três entidades principais que devem ser executadas em terminais separados. Siga a ordem abaixo para iniciar a rede de forma correta:

1. **Iniciar o Roteador:**
Abra o primeiro terminal e execute o ficheiro do roteador. Este atuará como o nó intermediário da rede.


```bash
python router.py

```


2. **Iniciar o Servidor:**
Abra o segundo terminal e inicie o servidor, que ficará à escuta de mensagens direcionadas ao seu VIP.


```bash
python server.py

```


3. **Iniciar o Cliente:**
Abra o terceiro terminal e execute o cliente. A partir daqui, poderá introduzir as mensagens de texto.


```bash
python client.py

```


4. **Utilização:**
No terminal do Cliente, digite a sua mensagem e prima `Enter`. Poderá acompanhar os registos coloridos nos terminais para visualizar o tráfego nas diferentes camadas ("Enviando ACK", "Erro físico detetado", retransmissões por Timeout).



## Simulação de Falhas e Testes de Stress

O ficheiro `protocolo.py` fornecido contém o simulador do canal físico. Para a demonstração de resiliência , pode alterar as seguintes variáveis no topo do ficheiro `protocolo.py` para testar a recuperação de erros:
 
`PROBABILIDADE_PERDA`: Define a taxa de perda de pacotes.

`PROBABILIDADE_CORRUPCAO`: Define a probabilidade de um erro de bit (invalidação do CRC).



## Autor

Luiz Felipe Belisário Macedo

202200538