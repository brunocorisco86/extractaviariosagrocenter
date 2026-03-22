# Extract Aviários - AgroCenter

Este projeto é uma ferramenta de extração de dados de produtores e aviários a partir de arquivos HTML exportados do sistema AgroCenter.

## Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação.
- `src/extractor.py`: Lógica principal encapsulada em classe (OOP).
- `data/raw/`: Pasta para os arquivos HTML de entrada.
- `data/processed/`: Pasta para os arquivos CSV e JSON gerados.
- `requirements.txt`: Dependências do projeto.
- `.gitignore`: Arquivos ignorados pelo Git.

## Instalação

1. Clone o repositório.
2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # ou
   .venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Coloque os arquivos HTML do AgroCenter na pasta `data/raw/`.
2. Execute o script:
   ```bash
   python main.py
   ```
3. Os resultados serão salvos em `data/processed/` nos formatos CSV e JSON.

## Autor

- Script Gerado (2026)
