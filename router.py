import socket
import json
import protocolo

# Tabela de roteamento estática mapeando VIPs para (IP, Porta) reais
TABELA_ROTEAMENTO = {
    "HOST_A": ("127.0.0.1", 9001),
    "SERVIDOR PRIME": ("127.0.0.1", 9002)
}

ENDERECO_ROTEADOR = ("127.0.0.1", 8000)

def iniciar_roteador():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(ENDERECO_ROTEADOR)
    print(f"[ROTEADOR] Iniciado na porta {ENDERECO_ROTEADOR[1]}. Aguardando tráfego...")

    while True:
        dados_recebidos, addr = sock.recvfrom(4096)
        
        # Camada 2: Enlace - Verificar Integridade
        quadro_dict, valido = protocolo.Quadro.deserializar(dados_recebidos)
        
        if not valido:
            print("\033[91m[ROTEADOR] Erro de CRC detectado! Quadro descartado silenciosamente.\033[0m")
            continue
            
        pacote_dict = quadro_dict.get("data", {})
        dst_vip = pacote_dict.get("dst_vip")
        ttl = pacote_dict.get("ttl", 0)

        # Camada 3: Rede - TTL e Roteamento
        if ttl <= 1:
            print(f"\033[93m[ROTEADOR] Pacote para {dst_vip} descartado (TTL Expirado).\033[0m")
            continue
            
        pacote_dict["ttl"] = ttl - 1 # Decrementa TTL
        
        if dst_vip in TABELA_ROTEAMENTO:
            destino_real = TABELA_ROTEAMENTO[dst_vip]
            print(f"[ROTEADOR] Roteando pacote de {pacote_dict.get('src_vip')} para {dst_vip} {destino_real}")
            
            # Reencapsula o quadro atualizado
            novo_quadro = protocolo.Quadro(quadro_dict["src_mac"], quadro_dict["dst_mac"], pacote_dict)
            bytes_para_enviar = novo_quadro.serializar()
            
            # Envia pelo canal ruidoso
            protocolo.enviar_pela_rede_ruidosa(sock, bytes_para_enviar, destino_real)
        else:
            print(f"[ROTEADOR] Destino {dst_vip} desconhecido. Descartando.")

if __name__ == "__main__":
    iniciar_roteador()