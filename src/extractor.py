#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo Extrator AgroCenter (OOP)
"""

import re
import csv
import json
from pathlib import Path
from bs4 import BeautifulSoup

class AgroCenterExtractor:
    def __init__(self, input_dir=None, output_dir=None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.input_dir = Path(input_dir) if input_dir else self.base_dir / 'data' / 'raw'
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / 'data' / 'processed'
        self.dados_consolidados = []

    def _extrair_arquivo(self, arquivo_html):
        """Método privado para processar um único arquivo HTML."""
        print(f"Lendo arquivo: {arquivo_html.name}")
        try:
            with open(arquivo_html, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
        except Exception as e:
            print(f"Erro ao ler arquivo {arquivo_html.name}: {e}")
            return []

        dict_produtores = {}

        # Estratégia 1: Tabela de Produtores
        self._processar_tabela_produtores(soup, dict_produtores, arquivo_html.name)
        
        # Estratégia 2: Tabela de Lotes em andamento
        self._processar_tabela_lotes(soup, dict_produtores, arquivo_html.name)

        # Finalizar lista para este arquivo
        lista_arquivo = []
        for nome, info in dict_produtores.items():
            info['aviarios'] = sorted(list(info['aviarios']))
            if not info['num_aviarios'] and info['aviarios']:
                info['num_aviarios'] = len(info['aviarios'])
            lista_arquivo.append(info)
        
        return lista_arquivo

    def _processar_tabela_produtores(self, soup, dict_produtores, filename):
        header = soup.find('h6', class_='MuiTypography-root', string='Produtores')
        if not header: return
        
        container = header.find_next_sibling('div')
        if not container: return

        for row in container.find_all('tr', class_='MuiTableRow-root'):
            link = row.find('a')
            if not link: continue

            nome = link.get_text(strip=True)
            if len(nome.split()) < 2: continue

            if nome not in dict_produtores:
                dict_produtores[nome] = {
                    'nome': nome,
                    'num_aviarios': 0,
                    'link': link.get('href', ''),
                    'aviarios': set(),
                    'arquivo_origem': filename
                }

            # Sub-tabela expandida
            collapse_row = row.find_next_sibling('tr')
            if collapse_row and 'MuiCollapse-root' in str(collapse_row):
                for cell in collapse_row.find_all('td', class_='MuiTableCell-sizeSmall'):
                    if not cell.find('button'):
                        av_nome = cell.get_text(strip=True)
                        if av_nome and re.search(r'AVIARIO\s+\d+', av_nome.upper()):
                            dict_produtores[nome]['aviarios'].add(av_nome)

    def _processar_tabela_lotes(self, soup, dict_produtores, filename):
        title = soup.find('span', class_='font-bold', string='Lotes em andamento')
        if not title: return

        container = title.find_parent('header').find_next_sibling('div')
        table = container.find('table', class_='MuiTable-root') if container else None
        if not table: return

        header_cells = table.find('thead').find_all('th')
        col_map = {
            'aviario': next((i for i, h in enumerate(header_cells) if 'Aviário' in h.get_text()), None),
            'produtor': next((i for i, h in enumerate(header_cells) if 'Produtor' in h.get_text()), None)
        }

        if col_map['aviario'] is not None and col_map['produtor'] is not None:
            body = table.find('tbody')
            for row in body.find_all('tr', class_='MuiTableRow-root'):
                cells = row.find_all('td', class_='MuiTableCell-root')
                if len(cells) > max(col_map.values()):
                    av = cells[col_map['aviario']].get_text(strip=True)
                    prod = cells[col_map['produtor']].get_text(strip=True)

                    if re.search(r'AVIARIO\s+\d+', av.upper()) and len(prod.split()) >= 2:
                        if prod not in dict_produtores:
                            dict_produtores[prod] = {
                                'nome': prod, 'num_aviarios': 0, 'link': '',
                                'aviarios': set(), 'arquivo_origem': filename
                            }
                        dict_produtores[prod]['aviarios'].add(av)

    def run(self):
        """Executa o processo completo de extração e salvamento."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        arquivos = list(self.input_dir.glob("*.html"))
        
        if not arquivos:
            print(f"⚠️  Nenhum HTML em {self.input_dir}")
            return

        for arquivo in arquivos:
            self.dados_consolidados.extend(self._extrair_arquivo(arquivo))

        if self.dados_consolidados:
            self.salvar()
            self._imprimir_resumo(len(arquivos))
        else:
            print("⚠️  Nenhum dado extraído.")

    def salvar(self):
        """Salva os dados nos formatos CSV e JSON."""
        # 1. Produtores CSV
        with open(self.output_dir / 'base_produtores.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['nome', 'num_aviarios', 'link', 'arquivo_origem'], extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.dados_consolidados)

        # 2. Aviários CSV (Flat)
        lista_flat = []
        for p in self.dados_consolidados:
            for av in p['aviarios']:
                lista_flat.append({'produtor': p['nome'], 'aviario': av, 'arquivo_origem': p['arquivo_origem']})

        with open(self.output_dir / 'base_aviarios.csv', 'w', newline='', encoding='utf-8') as f:
            if lista_flat:
                writer = csv.DictWriter(f, fieldnames=['produtor', 'aviario', 'arquivo_origem'])
                writer.writeheader()
                writer.writerows(lista_flat)

        # 3. JSON
        with open(self.output_dir / 'base_completa.json', 'w', encoding='utf-8') as f:
            json.dump(self.dados_consolidados, f, ensure_ascii=False, indent=2)

    def _imprimir_resumo(self, total_arquivos):
        num_produtores = len(self.dados_consolidados)
        num_aviarios = sum(len(p['aviarios']) for p in self.dados_consolidados)
        print("\n" + "=" * 80)
        print(f"PROCESSAMENTO CONCLUÍDO! ({total_arquivos} arquivos)")
        print(f"Produtores: {num_produtores} | Aviários: {num_aviarios}")
        print(f"Saída: {self.output_dir}")
        print("=" * 80)
