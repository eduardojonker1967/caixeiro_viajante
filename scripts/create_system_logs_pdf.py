#!/usr/bin/env python3
"""Coleta vários logs do sistema e gera um PDF com o conteúdo.

Comportamento:
- coleta outputs de comandos (uname, lsb_release, docker ps, docker logs, journalctl, dmesg, python/pip)
- grava um arquivo de texto em `logs/system_logs_<timestamp>.txt`
- tenta usar `reportlab` para converter o texto em PDF e salva em `logs/system_logs_<timestamp>.pdf`
- se `reportlab` não estiver instalado, tenta instalar via pip; se falhar, mantém apenas o .txt e retorna com código 0

Uso: python create_system_logs_pdf.py
"""
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(__file__)
LOGS_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)


def run_cmd(cmd, timeout=30):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out = res.stdout.strip()
        err = res.stderr.strip()
        return out, err, res.returncode
    except Exception as e:
        return '', f'ERROR running "{cmd}": {e}', 1


def collect():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    basename = f'system_logs_{ts}'
    txt_path = os.path.join(LOGS_DIR, basename + '.txt')
    pdf_path = os.path.join(LOGS_DIR, basename + '.pdf')

    commands = [
        ("Date/time", "date --utc || date"),
        ("User", "whoami"),
        ("Working dir", "pwd"),
        ("Uname", "uname -a"),
        ("LSB Release", "lsb_release -a 2>/dev/null || echo 'lsb_release not available'"),
        ("Python version", "python --version 2>&1 || python3 --version 2>&1"),
        ("Pip freeze", "pip freeze 2>/dev/null || echo 'pip not available'"),
        ("Docker PS", "docker ps -a --no-trunc || echo 'docker not available or permission denied'"),
        ("Docker - mongodb container logs (caixeiroviajante-mongodb-1)", "docker logs caixeiroviajante-mongodb-1 --tail 500 2>&1 || echo 'no logs for caixeiroviajante-mongodb-1'"),
        ("Docker - mongodb container logs (mongodb)", "docker logs mongodb --tail 500 2>&1 || echo 'no logs for mongodb'"),
        ("Journalctl (current boot, tail 1000)", "journalctl -b --no-pager -n 1000 2>&1 || echo 'journalctl not available or permission denied'"),
        ("Dmesg (tail 200)", "dmesg | tail -n 200 2>&1 || echo 'dmesg not available or permission denied'"),
    ]

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"System logs collected at {datetime.now().isoformat()}\n")
        f.write('=' * 80 + '\n')
        for title, cmd in commands:
            f.write(f"--- {title} ---\n")
            out, err, code = run_cmd(cmd)
            if out:
                f.write(out + '\n')
            if err:
                f.write('\n[stderr]\n')
                f.write(err + '\n')
            f.write('\n')

    # Tentar gerar PDF usando reportlab
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm

        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        margin = 15 * mm
        max_width = width - 2 * margin
        y = height - margin
        lines = text.split('\n')
        # use monospace font
        try:
            c.setFont('Courier', 9)
        except Exception:
            c.setFont('Helvetica', 9)

        line_height = 10
        for line in lines:
            # wrap long lines
            while c.stringWidth(line) > max_width:
                # find approx split
                for i in range(len(line)-1, 0, -1):
                    if c.stringWidth(line[:i]) <= max_width:
                        part = line[:i]
                        rest = line[i:]
                        break
                c.drawString(margin, y, part)
                y -= line_height
                line = rest
                if y < margin:
                    c.showPage()
                    try:
                        c.setFont('Courier', 9)
                    except Exception:
                        c.setFont('Helvetica', 9)
                    y = height - margin
            c.drawString(margin, y, line)
            y -= line_height
            if y < margin:
                c.showPage()
                try:
                    c.setFont('Courier', 9)
                except Exception:
                    c.setFont('Helvetica', 9)
                y = height - margin

        c.save()
        print(f'PDF criado em: {pdf_path}')
        return txt_path, pdf_path

    except ImportError:
        print('reportlab não está instalado. Tentando instalar via pip...')
        # tenta instalar reportlab localmente
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'reportlab'])
            # re-executa a si mesmo para gerar o PDF
            print('reportlab instalado. Gerando o PDF...')
            return collect()
        except Exception as e:
            print('Falha ao instalar reportlab ou gerar PDF:', e)
            print(f'O arquivo de texto com logs está em: {txt_path}')
            return txt_path, None


if __name__ == '__main__':
    txt, pdf = collect()
    if pdf:
        print('Operação concluída: logs salvos em texto e PDF.')
    else:
        print('Operação concluída: apenas o TXT foi salvo.')
