import streamlit as st
import qrcode
import zipfile
import os
import json
from io import BytesIO


# Função para gerar o JSON local
def salvar_json(numeros_serie):
    json_path = os.path.abspath("series.txt")  # Caminho absoluto
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(numeros_serie, f, ensure_ascii=False, indent=4)
    return json_path


# Função para gerar QR Codes apontando para o JSON
def gerar_qrCodes_zip(numeros_serie, json_path):
    zip_buffer = BytesIO()

    # Transformando o caminho local em formato URI para o QR Code
    json_uri = f"file://{json_path.replace(os.sep, '/')}"

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for numero in numeros_serie:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            # Cada QR Code aponta para o mesmo JSON
            qr.add_data(json_uri)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img_bytes = BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            zipf.writestr(f"{numero}.png", img_bytes.read())

    zip_buffer.seek(0)
    return zip_buffer

def app():
    st.title("Gerador de QR Codes apontando para JSON local")

    entrada = st.text_area("Insira os números de série (um por linha):")

    if st.button("Gerar QR Codes"):
        numeros = [n.strip() for n in entrada.splitlines() if n.strip()]

        if numeros:
            json_path = salvar_json(numeros)
            zip_buffer = gerar_qrCodes_zip(numeros, json_path)

            st.success(f"{len(numeros)} QR Codes gerados com sucesso!")
            st.download_button(
                label="Baixar QR Codes em ZIP",
                data=zip_buffer,
                file_name="qrcodes.zip",
                mime="application/zip",
            )
            st.info(f"JSON salvo em: {json_path}")
        else:
            st.warning("Insira pelo menos um número de série.")
