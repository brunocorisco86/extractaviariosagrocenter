#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de envio de e-mails para o Extrator AgroCenter.
"""

import os
import smtplib
from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv, set_key

class AgroCenterMailer:
    def __init__(self, processed_dir=None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.env_path = self.base_dir / '.env'
        self.processed_dir = Path(processed_dir) if processed_dir else self.base_dir / 'data' / 'processed'
        
        # Garante que o .env existe
        if not self.env_path.exists():
            self.env_path.touch()
            
        load_dotenv(self.env_path)

    def _get_config(self, key, prompt, sensitive=False):
        """Busca valor no .env ou pede ao usuário se estiver vazio."""
        value = os.getenv(key)
        if not value:
            print(f"\n[CONFIGURAÇÃO] {key} não encontrada.")
            value = input(f"{prompt}: ").strip()
            set_key(str(self.env_path), key, value)
            # Recarrega o env após salvar
            load_dotenv(self.env_path, override=True)
        return value

    def configurar(self):
        """Verifica e configura as variáveis de ambiente interativamente."""
        self.user_email = self._get_config("SENDER_EMAIL", "Digite seu e-mail do Gmail")
        self.app_password = self._get_config("APP_PASSWORD", "Digite sua Senha de App do Google (16 caracteres)", sensitive=True)
        self.recipient_email = self._get_config("RECIPIENT_EMAIL", "Digite o e-mail do destinatário padrão")

        # Confirmar ou alterar o destinatário
        print(f"\nDestinatário atual: {self.recipient_email}")
        change = input("Deseja alterar o destinatário para este envio? (s/N): ").lower()
        if change == 's':
            new_recipient = input("Digite o novo e-mail: ").strip()
            save = input("Deseja salvar este novo e-mail como padrão? (s/N): ").lower()
            if save == 's':
                set_key(str(self.env_path), "RECIPIENT_EMAIL", new_recipient)
                self.recipient_email = new_recipient
                load_dotenv(self.env_path, override=True)
            else:
                self.recipient_email = new_recipient

    def enviar_arquivos(self):
        """Envia os arquivos da pasta processed como anexo."""
        print(f"\nPreparando e-mail para {self.recipient_email}...")
        
        msg = EmailMessage()
        msg['Subject'] = 'Extração de Aviários - AgroCenter'
        msg['From'] = self.user_email
        msg['To'] = self.recipient_email
        msg.set_content("Olá,\n\nSegue em anexo os dados extraídos do AgroCenter.\n\nAtenciosamente,\nExtrator Automático.")

        # Anexar arquivos
        arquivos = list(self.processed_dir.glob("*.*"))
        if not arquivos:
            print("⚠️ Nenhum arquivo encontrado para enviar.")
            return False

        for path in arquivos:
            with open(path, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(
                    file_data,
                    maintype='application',
                    subtype='octet-stream',
                    filename=path.name
                )
            print(f"📎 Anexado: {path.name}")

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.user_email, self.app_password)
                smtp.send_message(msg)
            print("✅ E-mail enviado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar e-mail: {e}")
            return False
