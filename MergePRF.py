#!/usr/bin/env python3
import os
import subprocess
from PyPDF2 import PdfMerger

DOWNLOAD_DIR = "/home/node/files/consulta_prf"

def merge_and_compress(input_dir, output_name="requerimento.pdf"):
    # Encontra todos os PDFs (ignorando o próprio output)
    pdf_files = sorted(
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".pdf") and f.lower() != output_name.lower()
    )

    if not pdf_files:
        print(f"[!] Nenhum PDF encontrado em {input_dir}")
        return

    raw_path = os.path.join(input_dir, "merged_raw.pdf")
    final_path = os.path.join(input_dir, output_name)

    # 1) Merge dos PDFs
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open(raw_path, "wb") as fout:
        merger.write(fout)
    merger.close()

    # 2) Compressão com Ghostscript (modo ebook)
    gs_args = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dColorImageDownsampleType=/Bicubic",
        "-dColorImageResolution=150",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dGrayImageResolution=150",
        "-dMonoImageDownsampleType=/Subsample",
        "-dMonoImageResolution=150",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={final_path}",
        raw_path,
    ]
    try:
        subprocess.run(gs_args, check=True)
    except subprocess.CalledProcessError as e:
        print("[!] Erro ao executar Ghostscript:", e)
        return

    # 3) Remoção do arquivo intermediário
    os.remove(raw_path)
    print(f"[✔] PDF final salvo em: {final_path}")

if __name__ == "__main__":
    merge_and_compress(DOWNLOAD_DIR)
