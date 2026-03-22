#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada principal para o Extrator de Aviários.
Inclui funcionalidade de envio de e-mail.
"""

from src.extractor import AgroCenterExtractor
from src.mailer import AgroCenterMailer

def main():
    # 1. Executa a Extração
    extractor = AgroCenterExtractor()
    extractor.run()

    # 2. Pergunta se deseja enviar por e-mail
    if extractor.dados_consolidados:
        print("\n" + "-" * 40)
        enviar = input("Deseja enviar os resultados por e-mail? (s/N): ").lower()
        
        if enviar == 's':
            mailer = AgroCenterMailer()
            mailer.configurar()
            mailer.enviar_arquivos()
        else:
            print("Operação de envio cancelada pelo usuário.")
    
    print("\nProcesso finalizado.")

if __name__ == "__main__":
    main()
