import streamlit as st
import qrcode
import zipfile
import os
from io import BytesIO
import socket


# Descobre o IP local
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# Gera o arquivo TXT
def gerar_txt(local, numeros_serie):
    txt_path = os.path.abspath(f"qrcode_files/{local}.txt")
    pasta = os.path.dirname(txt_path)
    os.makedirs(pasta, exist_ok=True)

    with open(txt_path, "w", encoding="utf-8") as f:
        for numero in numeros_serie:
            f.write(f"{numero}\n")
    return txt_path


# Gera o QR apontando para o próprio app Streamlit
def gerar_qrCodes_zip(local, base_url):
    zip_buffer = BytesIO()
    internal_url = f"{base_url}/?file={local}"

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(internal_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        zipf.writestr(f"{os.path.basename(local)}.png", img_bytes.read())

    zip_buffer.seek(0)
    return zip_buffer, internal_url


def app():
    with open("assets/header.html", "r", encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)

    # Compatibilidade total (nova ou antiga API)
    try:
        query_params = st.query_params
    except AttributeError:
        query_params = st.experimental_get_query_params()

    # Exibe conteúdo do arquivo se acessar com ?file=
    if "file" in query_params:
        local_name = (
            query_params["file"]
            if isinstance(query_params["file"], str)
            else query_params["file"][0]
        )
        file_path = os.path.abspath(f"qrcode_files/{local_name}.txt")

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                conteudo = f.read()
            st.subheader(f"Números de série - {local_name}")
            st.text(conteudo)
            st.download_button(
                "Baixar arquivo TXT",
                data=conteudo,
                file_name=f"{local_name}.txt",
                mime="text/plain",
            )
        else:
            st.error("Arquivo não encontrado.")
        return  # interrompe o fluxo principal

    local = st.text_input("Local do Estoque:", placeholder="Ex.: PRIME/Disponível")
    entrada = st.text_area(
        "Insira os números de série:", placeholder="Digite um número de série por linha"
    )

    if st.button("Gerar QR Code"):
        numeros = [n.strip() for n in entrada.splitlines() if n.strip()]

        if numeros:
            gerar_txt(local, numeros)

            ip = get_local_ip()
            base_url = f"http://{ip}:8501"  # mesma porta do Streamlit

            zip_buffer, url = gerar_qrCodes_zip(local, base_url)

            st.success("QR Code gerado com sucesso!")
            st.write(f"Acesse os números de série pelo link: [Abrir arquivo]({url})")

            st.download_button(
                label="Baixar QR Code",
                data=zip_buffer,
                file_name="qrcodes.zip",
                mime="application/zip",
            )
        else:
            st.warning("Insira pelo menos um número de série.")

    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with open("assets/footer.html", encoding="utf-8") as f:
        st.markdown(
            f.read(),
            unsafe_allow_html=True,
        )
