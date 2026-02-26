import socket
import json
import protocolo

MEU_VIP = "SERVIDOR PRIME"
MEU_MAC = "MAC_SERVER"
ENDERECO_LOCAL = ("127.0.0.1", 9002)
ROTEADOR = ("127.0.0.1", 8000)

def iniciar_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(ENDERECO_LOCAL)
    print(f"[SERVIDOR] {MEU_VIP} operando na porta {ENDERECO_LOCAL[1]}...")

    seq_esperado = 0 # Espera o primeiro pacote com seq_num 0

    while True:
        dados, _ = sock.recvfrom(4096)
        
        # Desencapsulamento Camada 2 e verificação CRC
        quadro_dict, valido = protocolo.Quadro.deserializar(dados)
        if not valido:
            print("\033[91m[SERVIDOR] Erro físico detectado. Quadro descartado.\033[0m")
            continue
            
        pacote_dict = quadro_dict["data"]
        
        # Filtro da Camada 3
        if pacote_dict["dst_vip"] != MEU_VIP:
            continue
            
        segmento_dict = pacote_dict["data"]
        is_ack = segmento_dict["is_ack"]
        seq_num = segmento_dict["seq_num"]
        
        if not is_ack:
            # Camada 4: Lógica de Sequência (Descartar duplicatas)
            remetente_vip = pacote_dict["src_vip"]
            remetente_mac = quadro_dict["src_mac"]
            
            if seq_num == seq_esperado:
                payload = segmento_dict["payload"]
                print(f"\n\033[92m[APLICAÇÃO] Mensagem de {payload['sender']}: {payload['message']}\033[0m")
                # Alterna o bit de sequência (0 para 1, 1 para 0)
                seq_esperado = 1 - seq_esperado 
            else:
                print(f"\033[93m[TRANSPORTE] Duplicata recebida (seq {seq_num}). Reenviando ACK...\033[0m")

            # Enviar ACK de volta
            print(f"   [TRANSPORTE] Enviando ACK {seq_num} para {remetente_vip}...")
            seg_ack = protocolo.Segmento(seq_num, True, {})
            pac_ack = protocolo.Pacote(MEU_VIP, remetente_vip, 10, seg_ack.to_dict())
            quad_ack = protocolo.Quadro(MEU_MAC, remetente_mac, pac_ack.to_dict())
            
            protocolo.enviar_pela_rede_ruidosa(sock, quad_ack.serializar(), ROTEADOR)

if __name__ == "__main__":
    iniciar_servidor()