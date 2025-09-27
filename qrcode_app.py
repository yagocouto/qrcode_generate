import streamlit as st
import qrcode
import zipfile
import os
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


def gerar_txt(local, numeros_serie):
    txt_path = os.path.abspath(f"qrcode_files/{local}.txt")
    pasta = os.path.dirname(txt_path)  # pega só o diretório do caminho
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    with open(txt_path, "w", encoding="utf-8") as f:
        for numero in numeros_serie:
            f.write(f"{numero}\n")
    return txt_path


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

        nome_arquivo = f"{os.path.basename(local)}.png"
        zipf.writestr(nome_arquivo, img_bytes.read())

    zip_buffer.seek(0)
    return zip_buffer, json_url


def start_http_server(port):
    pasta_arquivos = os.path.abspath("qrcode_files")
    os.makedirs(pasta_arquivos, exist_ok=True)

    try:
        subprocess.Popen(
            ["python", "-m", "http.server", str(port), "--bind", "0.0.0.0"],
            cwd=pasta_arquivos,
        )
    except Exception as e:
        st.error(f"Erro ao iniciar servidor HTTP: {e}")


def app():
    with open("assets/header.html", "r", encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)

    local = st.text_input("Local do Estoque:", placeholder="Ex.: PRIME/Disponível")
    entrada = st.text_area(
        "Insira os números de série:", placeholder="Digite um número de série por linha"
    )

    if st.button("Gerar QR Code"):
        numeros = [n.strip() for n in entrada.splitlines() if n.strip()]

        if numeros:
            ip = get_local_ip()
            port = 8502

            # Salva o TXT
            json_path = gerar_txt(local, numeros)

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

    # HTML Rodapé
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with open("assets/footer.html", encoding="utf-8") as f:
        st.markdown(
            f.read(),
            unsafe_allow_html=True,
        )
