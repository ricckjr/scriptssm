#!/usr/bin/env python3
import os
import subprocess
from PyPDF2 import PdfMerger

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

    # 1) Merge
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open(raw_path, "wb") as fout:
        merger.write(fout)
    merger.close()

    # 2) Compress via Ghostscript (modo /ebook para ~150 dpi)
    gs_args = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",          # qualidade intermediária (~150 dpi)
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

    # 3) Limpeza do arquivo temporário
    os.remove(raw_path)
    print(f"[✔] PDF final salvo em: {final_path}")

if __name__ == "__main__":
    DOWNLOAD_DIR = "/home/node/files/consulta_goias"
    merge_and_compress(DOWNLOAD_DIR)
