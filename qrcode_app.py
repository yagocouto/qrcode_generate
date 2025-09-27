import streamlit as st
import qrcode
import zipfile
import os
import json
import socket
import subprocess
from io import BytesIO


# Descobre o IP local do Windows/Linux
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# Função para gerar o JSON (txt) local
def salvar_json(local, numeros_serie):
    json_path = os.path.abspath(f"{local}.txt")  # Caminho absoluto
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(numeros_serie, f, ensure_ascii=False, indent=4)
    return json_path


# Função para gerar QR Codes apontando para o arquivo via HTTP
def gerar_qrCodes_zip(local, ip, port):
    zip_buffer = BytesIO()
    json_url = f"http://{ip}:{port}/{local}.txt"

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(json_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        zipf.writestr(f"{local}.png", img_bytes.read())

    zip_buffer.seek(0)
    return zip_buffer, json_url


# Sobe o servidor HTTP na pasta atual (se não estiver rodando)
def start_http_server(port):
    try:
        subprocess.Popen(
            ["python", "-m", "http.server", str(port), "--bind", "0.0.0.0"],
            cwd=os.getcwd(),
        )
    except Exception as e:
        st.error(f"Erro ao iniciar servidor HTTP: {e}")


def app():
    st.title("Gerador de QR Codes apontando para TXT via HTTP")

    local = st.text_area("Local:")
    entrada = st.text_area("Insira os números de série (um por linha):")

    if st.button("Gerar QR Code"):
        numeros = [n.strip() for n in entrada.splitlines() if n.strip()]

        if numeros:
            ip = get_local_ip()
            port = 8502

            # Salva o TXT
            json_path = salvar_json(local, numeros)

            # Inicia o servidor HTTP
            start_http_server(port)

            # Gera o QR Code com o link HTTP
            zip_buffer, url = gerar_qrCodes_zip(local, ip, port)

            st.success("QR Code gerado com sucesso!")
            st.write(f"O arquivo pode ser acessado em: **{url}**")

            st.download_button(
                label="Baixar QR Code",
                data=zip_buffer,
                file_name="qrcodes.zip",
                mime="application/zip",
            )
        else:
            st.warning("Insira pelo menos um número de série.")
