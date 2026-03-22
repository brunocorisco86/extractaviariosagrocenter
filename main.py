#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada principal para o Extrator de Aviários.
"""

from src.extractor import AgroCenterExtractor

def main():
    # Instancia o extrator com os diretórios padrão
    extractor = AgroCenterExtractor()
    
    # Executa o processamento
    extractor.run()

if __name__ == "__main__":
    main()
