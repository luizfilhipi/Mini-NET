import socket
import threading
import time
import datetime
import json
import protocolo

MEU_VIP = "HOST_A"
MEU_MAC = "MAC_CLIENT"
DESTINO_VIP = "SERVIDOR PRIME"
DESTINO_MAC = "MAC_SERVER"
ENDERECO_LOCAL = ("127.0.0.1", 9001)
ROTEADOR = ("127.0.0.1", 8000)

TIMEOUT = 3.0 # Segundos antes de retransmitir

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(ENDERECO_LOCAL)

# Variáveis de controle de estado do Stop-and-Wait
ack_recebido = threading.Event()
seq_atual = 0

def thread_recebimento():
    global seq_atual
    while True:
        try:
            dados, _ = sock.recvfrom(4096)
            quadro_dict, valido = protocolo.Quadro.deserializar(dados)
            
            if not valido:
                continue # Descarta silenciosamente erros físicos
                
            pacote = quadro_dict.get("data", {})
            if pacote.get("dst_vip") != MEU_VIP:
                continue
                
            segmento = pacote.get("data", {})
            
            # Verifica se é um ACK para o número de sequência atual
            if segmento.get("is_ack") and segmento.get("seq_num") == seq_atual:
                print(f"\033[94m   [TRANSPORTE] ACK {seq_atual} recebido com sucesso!\033[0m")
                ack_recebido.set() # Libera a thread principal
                
        except Exception:
            pass

def enviar_mensagem(mensagem_texto):
    global seq_atual
    
    # Camada 7: Aplicação - Construção do JSON
    payload = {
        "type": "chat",
        "sender": "Usuario_A",
        "message": mensagem_texto,
        "timestamp": str(datetime.datetime.now())
    }
    
    # Encapsulamento
    segmento = protocolo.Segmento(seq_atual, False, payload)
    pacote = protocolo.Pacote(MEU_VIP, DESTINO_VIP, 10, segmento.to_dict())
    quadro = protocolo.Quadro(MEU_MAC, DESTINO_MAC, pacote.to_dict())
    
    bytes_para_enviar = quadro.serializar()
    
    ack_recebido.clear()
    
    # Stop-and-Wait com Timeouts
    while not ack_recebido.is_set():
        print(f"\n[TRANSPORTE] Enviando pacote seq={seq_atual}...")
        protocolo.enviar_pela_rede_ruidosa(sock, bytes_para_enviar, ROTEADOR)
        
        # Aguarda o ACK. Se não vier no tempo estipulado, o loop repete (Retransmissão)
        sucesso = ack_recebido.wait(TIMEOUT)
        if not sucesso:
            print(f"\033[93m[TRANSPORTE] Timeout! ACK {seq_atual} não chegou em {TIMEOUT}s. Retransmitindo...\033[0m")
            
    # Prepara o próximo bit de sequência (0 vira 1, 1 vira 0)
    seq_atual = 1 - seq_atual

if __name__ == "__main__":
    print(f"=== CLIENTE CHAT MINI-NET ({MEU_VIP}) ===")
    
    # Inicia a thread que fica escutando a rede
    t = threading.Thread(target=thread_recebimento, daemon=True)
    t.start()
    
    while True:
        msg = input("\nDigite sua mensagem: ")
        if msg.lower() == 'sair':
            break
        enviar_mensagem(msg)