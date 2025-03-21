import os
import base64
import io
from datetime import datetime

import pyvips
from typing import Dict, List, Any

from PyPDF2 import PdfWriter, PdfReader

from docsplit.config import Config

class PdfToJpg:
    def __init__(self, doc_info: Dict[str, Any], retain: bool = False):
        self.doc_info = doc_info
        self.retain = retain

    def convert(self) -> Dict[str, Any]:
        """
        Convert PDF to JPG images (one per page).

        Returns:
            Dict: Conversion result with base64-encoded images.
        """
        try:
            pdf_buffer = self._get_pdf_buffer()
            converted_pages = []

            with pyvips.Image.pdfload_buffer(pdf_buffer, n=-1) as pdf:
                for page_num in range(1, pdf.get("n-pages") + 1):
                    page_data = self._convert_page(pdf, page_num)
                    converted_pages.append(page_data)

            return {
                'errCode': 0,
                'datarec': converted_pages
            }
        except Exception as e:
            print("error", str(e))
            return self._error_response(str(e))

    def _get_pdf_buffer(self) -> bytes:
        """
        Get PDF content as bytes.

        Returns:
            bytes: PDF content.
        """
        if self.doc_info.get('doc_path'):
            with open(self.doc_info['doc_path'], 'rb') as f:
                return f.read()
        elif self.doc_info.get('doc_data'):
            # Remove 'base64,' part and any surrounding spaces/newlines
            base64_data = self.doc_info['doc_data'].split('base64,')[-1].strip()
            binary_data = base64.b64decode(base64_data)
            return io.BytesIO(binary_data).getvalue()
        raise ValueError("No PDF data provided")

    def _convert_page(self, pdf: 'pyvips.Image', page_num: int) -> Dict[str, Any]:
        """
        Convert a single PDF page to JPG.

        Args:
            pdf (pyvips.Image): PDF document.
            page_num (int): Page number to convert.

        Returns:
            Dict: Page details with base64-encoded image.
        """
        page = pyvips.Image.pdfload_buffer(self._get_pdf_buffer(), page=page_num - 1, dpi=150)  # 0-based indexing in pyvips
        temp_dir = Config.get_temp_dir()
        doc_uid = f"{self.doc_info['doc_id']}_page_{page_num}_{datetime.now().strftime('%Y%m%d%H%M%S') + str(datetime.now().microsecond)[:3]}"
        temp_image_path = os.path.join(
            temp_dir,
            f"{doc_uid}.jpg"
        )

        page.write_to_file(temp_image_path, Q=90)  # Q=90 for JPEG quality
        doc_size = os.path.getsize(temp_image_path)

        with open(temp_image_path, 'rb') as f:
            base64_data = base64.b64encode(f.read()).decode('utf-8')

        if not self.retain:
            os.remove(temp_image_path)

        return {
                'doc_uid': doc_uid,
                'doc_data': base64_data,
                'page': page_num,
                'doc_size': doc_size,
                'doc_path': temp_image_path if self.retain else None,
                'doc_id': self.doc_info['doc_id'],
                'parent_doc_uid': self.doc_info.get('parent_doc_uid'),
                'extension': 'jpg'
            }

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """
        Create error response for failed conversions.

        Args:
            error_msg (str): Error message.

        Returns:
            Dict: Error response.
        """
        return {
            'errCode': 1,
            'msg': error_msg,
            'datarec': {
                'doc_id': self.doc_info.get('doc_id'),
                'doc_data': self.doc_info.get('doc_data'),
                'doc_size': self.doc_info.get('doc_size')
            }
        }

class PdfToPdf:
    def __init__(self, doc_info: Dict[str, Any], retain: bool = False):
        self.doc_info = doc_info
        self.retain = retain

    def convert(self) -> Dict[str, Any]:
        """
               Convert PDF to individual PDF pages.

               Returns:
                   Dict: Conversion result with base64-encoded PDFs.
               """
        try:
            converted_pages = []

            reader = self._get_pdf_reader()

            for page_num, page in enumerate(reader.pages, start=1):
                page_data = self._convert_page(page, page_num)
                converted_pages.append(page_data)

            return {
                'errCode': 0,
                'datarec': converted_pages
            }

        except Exception as e:
            print("error", str(e))
            return self._error_response(str(e))


    def _get_pdf_reader(self) -> PdfReader:
        """
        Get the PDF reader object from the PDF buffer.

        Returns:
            PdfReader: The reader object to access pages in the PDF.
        """
        if self.doc_info.get('doc_path'):
            return PdfReader(self.doc_info['doc_path'])
        elif self.doc_info.get('doc_data'):
            base64_data = self.doc_info['doc_data'].split('base64,')[1]
            binary_data = base64.b64decode(base64_data)
            return PdfReader(io.BytesIO(binary_data))
        raise ValueError("Invalid PDF data provided")

    def _convert_page(self, page: 'PyPDF2.pdf.PageObject', page_num: int) -> Dict[str, Any]:
        """
        Convert a single PDF page to a separate PDF file.

        Args:
            page (PyPDF2.pdf.PageObject): PDF page to convert.
            page_num (int): Page number to convert.

        Returns:
            Dict: Page details with base64-encoded PDF.
        """
        doc_uid = f"{self.doc_info['doc_id']}_page_{page_num}_{datetime.now().strftime('%Y%m%d%H%M%S') + str(datetime.now().microsecond)[:3]}"
        temp_pdf_path = os.path.join(
            Config.get_temp_dir(),
            f"{doc_uid}.pdf"
        )

        writer = PdfWriter()
        writer.add_page(page)

        # Write the page to a temporary PDF file
        with open(temp_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)

        doc_size = os.path.getsize(temp_pdf_path)

        with open(temp_pdf_path, 'rb') as f:
            base64_data = base64.b64encode(f.read()).decode('utf-8')

        if not self.retain:
            os.remove(temp_pdf_path)

        return {
            'doc_uid': doc_uid,
            'doc_data': base64_data,
            'page': page_num,
            'doc_size': doc_size,
            'doc_path': temp_pdf_path if self.retain else None,
            'doc_id': self.doc_info['doc_id'],
            'parent_doc_uid': self.doc_info.get('parent_doc_uid'),
            'extension': 'pdf'
        }

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """
        Create error response for failed conversions.

        Args:
            error_msg (str): Error message.

        Returns:
            Dict: Error response.
        """
        return {
            'errCode': 1,
            'msg': error_msg,
            'datarec': {
                'doc_id': self.doc_info.get('doc_id'),
                'doc_data': self.doc_info.get('doc_data'),
                'doc_size': self.doc_info.get('doc_size')
            }
        }