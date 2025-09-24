import streamlit as st
import qrcode
import zipfile
from io import BytesIO

def gerar_qrCodes_zip(numeros_serie):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for numero in numeros_serie:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(numero)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img_bytes = BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            zipf.writestr(f"{numero}.png", img_bytes.read())

    zip_buffer.seek(0)
    return zip_buffer

# Interface Streamlit
st.title("Gerador de QR Codes em Memória")

entrada = st.text_area("Insira os números de série (um por linha):")

if st.button("Gerar QR Codes"):
    numeros = [n.strip() for n in entrada.splitlines() if n.strip()]
    
    if numeros:
        zip_buffer = gerar_qrCodes_zip(numeros)

        st.success(f"{len(numeros)} QR Codes gerados com sucesso!")
        st.download_button(
            label="Baixar QR Codes em ZIP",
            data=zip_buffer,
            file_name="qrcodes.zip",
            mime="application/zip"
        )
    else:
        st.warning("Insira pelo menos um número de série.")
