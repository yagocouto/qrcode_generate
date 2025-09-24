import streamlit as st
import qrcode
import os
import zipfile
from io import BytesIO

def gerar_qrCodes(numeros_serie, output_dir = "qrcodes"):
  os.makedirs(output_dir, exist_ok=True)

  for numero in numeros_serie:
    qr = qrcode.QRCode(
      version=1,
      error_correction=qrcode.constants.ERROR_CORRECT_H,
      box_size=10,
      border=4,
    )
    qr.add_data(numero)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", black_color="white")
    
    filename = os.path.join(output_dir, f"{numero}.png")
    img.save(filename)
    
    print(f"QR Code gerado: {filename}")
    
entrada = st.text_area("Insira os números de série (um por linha):")

if st.button("Gerar QR Codes"):
  numeros = entrada.splitlines()
  arquivos = gerar_qrCodes(numeros)
  
  zip_buffer = BytesIO()
  with zipfile.ZipFile(zip_buffer, "w") as zipf:
    for file in arquivos:
      zipf.write(file,os.path.basename(file))
  zip_buffer.seek(0)
  
  st.success(f"{len(arquivos)} QR Codes gerados com sucesso!")
  st.download_button(
    label="Baixar QR Codes em ZIP",
    data=zip_buffer,
    file_name="qrcodes.zip",
    mime="application/zip"
  )