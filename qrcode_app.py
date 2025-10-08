import streamlit as st
import qrcode
import zipfile
import os
import socket
from io import BytesIO
import urllib.parse


# Descobre o IP local Windows/Linux
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def gerar_txt(local, numeros_serie):
    # Cria a pasta da subpasta caso não exista
    pasta = os.path.join("qrcode_files", os.path.dirname(local))
    os.makedirs(pasta, exist_ok=True)

    txt_path = os.path.abspath(f"qrcode_files/{local}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for numero in numeros_serie:
            f.write(f"{numero}\n")
    return txt_path


def gerar_qrCodes_zip(local, ip, port):
    zip_buffer = BytesIO()
    # Codifica todo o caminho relativo para o QR Code
    encoded_file = urllib.parse.quote(local)
    json_url = f"http://{ip}:{port}/?file={encoded_file}"

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


def app():
    # Header
    if os.path.exists("assets/header.html"):
        with open("assets/header.html", "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)

    # Lê query param para exibir arquivo TXT
    query_params = st.query_params
    if "file" in query_params:
        file_name = urllib.parse.unquote(query_params["file"][0])
        file_path = os.path.abspath(os.path.join("qrcode_files", file_name + ".txt"))
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                conteudo = f.read()
            st.subheader(f"Conteúdo do arquivo: {file_name}.txt")
            st.text_area("TXT", conteudo, height=300)
            st.download_button(
                label="Baixar arquivo TXT",
                data=conteudo,
                file_name=f"{file_name}.txt",
                mime="text/plain",
            )
        else:
            st.error(f"Arquivo não encontrado: {file_path}")
        return

    # Entrada de dados
    local = st.text_input("Local do Estoque:", placeholder="Ex.: Prime/Disponivel2")
    entrada = st.text_area(
        "Insira os números de série:", placeholder="Digite um número de série por linha"
    )

    if st.button("Gerar QR Code"):
        numeros = [n.strip() for n in entrada.splitlines() if n.strip()]

        if numeros:
            ip = get_local_ip()
            port = 8501

            # Salva o TXT na pasta correta
            gerar_txt(local, numeros)

            # Gera o QR Code com link para a própria aplicação
            zip_buffer, url = gerar_qrCodes_zip(local, ip, port)

            st.success("QR Code gerado com sucesso!")
            st.write(f"O QR Code aponta para: **{url}**")
            st.download_button(
                label="Baixar QR Code",
                data=zip_buffer,
                file_name="qrcodes.zip",
                mime="application/zip",
            )
        else:
            st.warning("Insira pelo menos um número de série.")

    # Footer
    if os.path.exists("assets/style.css"):
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    if os.path.exists("assets/footer.html"):
        with open("assets/footer.html", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
