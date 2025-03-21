import os
import base64
import io
from datetime import datetime
from typing import Dict, Any
from PyPDF2 import PdfMerger

from docsplit.config import Config
from docsplit.converters.image_converter import HeicAndPngAndJpgAndJpegToPdf

class MergePdf:
    def __init__(self, doc_info: Dict[str, Any]):
        """
        Initialize with the list of document paths that need to be merged.

        Args:
            doc_info (Dict): Contains document paths to merge.
            retain_splitted_documents (bool): Flag to retain or delete intermediate files.
        """
        self.doc_info = doc_info

    def merge(self) -> Dict[str, Any]:
        """
        Merge PDF files (including images converted to PDFs) into a single PDF.

        Returns:
            Dict: Conversion result with base64-encoded merged PDF.
        """
        try:
            merged_data = []
            pdf_merger = PdfMerger()
            opened_files = []

            # Loop through each document path to handle different formats
            for doc_path in self.doc_info['doc_path_list']:
                _, ext = os.path.splitext(doc_path)
                ext = ext.lower().lstrip(".")

                if ext in ["jpg", "jpeg", "png", "heic"]:
                    # Convert image files (jpg, jpeg, png) to PDF
                    obj = HeicAndPngAndJpgAndJpegToPdf(
                        {'doc_path': doc_path, 'split_format': "pdf"},
                        retain_splitted_documents=True
                    )
                    pdf_data = obj.convert()
                    if pdf_data.get("errCode"):
                        return pdf_data
                    doc_path = pdf_data.get("datarec")[0]['doc_path']

                elif ext != "pdf":
                    return {"errCode": 0, "msg": f"Unsupported file format: {ext}"}

                # Append PDF files to the merger
                pdf = open(doc_path, 'rb')
                pdf_merger.append(pdf)
                opened_files.append(pdf)

            print("opened_files", opened_files)

            # Write the merged PDF to a BytesIO object
            merged_pdf_binary = io.BytesIO()
            pdf_merger.write(merged_pdf_binary)
            pdf_merger.close()
            merged_pdf_binary.seek(0)

            # Close all opened PDFs
            for pdf in opened_files:
                pdf.close()

            # Calculate the size of the merged PDF
            merged_pdf_size = len(merged_pdf_binary.getvalue())
            binary_data = base64.b64encode(merged_pdf_binary.read()).decode('utf-8')

            temp_pdf_path = os.path.join(Config.get_temp_dir(), f"merged_document_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")

            with open(temp_pdf_path, 'wb') as temp_pdf_file:
                temp_pdf_file.write(merged_pdf_binary.getvalue())

            # Prepare the result data
            merged_data.append({
                'binary_data': binary_data,
                'size': merged_pdf_size,
                'extension': 'pdf'
            })

            return {'errCode': 0, 'datarec': merged_data}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'errCode': 1, 'msg': str(e)}
