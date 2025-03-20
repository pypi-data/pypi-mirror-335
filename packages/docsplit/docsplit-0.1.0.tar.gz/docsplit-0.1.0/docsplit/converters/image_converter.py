import os
import base64
import io
from datetime import datetime
from typing import Dict, Any
from docsplit.config import Config
from PIL import Image
from pillow_heif import register_heif_opener

class HeicAndPngToJpg:
    def __init__(self, doc_info: Dict[str, Any], retain_splitted_documents: bool = False):
        self.doc_info = doc_info
        self.retain_splitted_documents = retain_splitted_documents
        register_heif_opener()

    def convert(self) -> Dict[str, Any]:
        """
        Convert HEIC or PNG images to JPG.

        Returns:
            Dict: Conversion result with base64-encoded JPG image.
        """
        try:
            image = self._get_image()
            converted_data = []

            # Generate the output path for the JPG image
            doc_uid = f"{self.doc_info['doc_id']}_page_1_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            temp_image_path = os.path.join(
                Config.get_temp_dir(),
                f"{doc_uid}.jpg"
            )

            # Convert the image to JPG format and save it
            image.convert("RGB").save(temp_image_path, "JPEG", quality=90)
            doc_size = os.path.getsize(temp_image_path)

            # Convert the image to base64
            with open(temp_image_path, "rb") as file:
                base64_data = base64.b64encode(file.read()).decode('utf-8')

            # Add the converted data to the result
            converted_data.append({
                'doc_uid': doc_uid,
                'doc_data': base64_data,
                'page': 1,
                'doc_size': doc_size,
                'doc_path': temp_image_path if self.retain_splitted_documents else None,
                'doc_id': self.doc_info['doc_id'],
                'parent_doc_uid': self.doc_info.get('parent_doc_uid'),
                'extension': 'jpg'
            })

            # Clean up if we don't need to retain the image
            if not self.retain_splitted_documents:
                os.remove(temp_image_path)

            return {'errCode': 0, 'datarec': converted_data}

        except Exception as e:
            print("Error:", str(e))
            return self._error_response(str(e))

    def _get_image(self) -> Image:
        """
        Get image content (either from a file or base64-encoded data).

        Returns:
            PIL.Image: The image object.
        """
        if self.doc_info.get('doc_path'):
            file_path = self.doc_info['doc_path']
            if file_path.lower().endswith('.heic'):
                # Handling HEIC file with pillow-heif (this is where we use pillow-heif)
                try:
                    image = Image.open(file_path)  # pillow-heif will be used here if it's a HEIC file
                    return image
                except Exception as e:
                    print(f"Error opening HEIC file: {e}")
            else:
                # For non-HEIC files, use Pillow directly
                return Image.open(file_path)
        elif self.doc_info.get('doc_data'):
            base64_data = self.doc_info['doc_data'].split('base64,')[-1]
            binary_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(binary_data))
            return image
        else:
            raise ValueError("No image data provided")

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

class HeicAndPngAndJpgAndJpegToPdf:
    def __init__(self, doc_info: Dict[str, Any], retain_splitted_documents: bool = False):
        self.doc_info = doc_info
        self.retain_splitted_documents = retain_splitted_documents
        register_heif_opener()

    def convert(self) -> Dict[str, Any]:
        """
        Convert HEIC, PNG, JPG, and JPEG images to PDF.

        Returns:
            Dict: Conversion result with base64-encoded PDF.
        """
        try:
            converted_data = []

            # Get the image (either from a file path or base64 data)
            image = self._get_image()

            # If the image is not in RGB mode, convert it
            if image.mode != 'RGB':
                image = image.convert("RGB")

            # Generate doc_uid and temporary file path for the resulting PDF
            doc_uid = f"{self.doc_info.get('doc_id')}_page_1_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            temp_pdf_path = os.path.join(Config.get_temp_dir(), f"{doc_uid}.pdf")

            # Save the image as a PDF
            image.save(temp_pdf_path, "PDF")
            doc_size = os.path.getsize(temp_pdf_path)

            # Convert the PDF to base64
            with open(temp_pdf_path, "rb") as file:
                base64_data = base64.b64encode(file.read()).decode('utf-8')

            # Prepare the converted data
            converted_data.append({
                'doc_uid': doc_uid,
                'doc_data': base64_data,
                'page': 1,
                'doc_size': doc_size,
                'doc_path': temp_pdf_path if self.retain_splitted_documents else None,
                'doc_id': self.doc_info.get('doc_id'),
                'parent_doc_uid': self.doc_info.get('parent_doc_uid'),
                'extension': 'pdf'
            })

            # Clean up the temporary file if not retaining
            if not self.retain_splitted_documents:
                os.remove(temp_pdf_path)

            return {'errCode': 0, 'datarec': converted_data, 'doc_id': self.doc_info.get('doc_id')}

        except Exception as e:
            datarec = {
                'doc_id': self.doc_info.get('doc_id'),
                'doc_data': self.doc_info.get('doc_data'),
                'doc_size': self.doc_info.get('doc_size')
            }
            return {'errCode': 1, 'msg': str(e), 'datarec': datarec}

    def _get_image(self) -> Image:
        """
        Get image content (either from a file or base64-encoded data).

        Returns:
            PIL.Image: The image object.
        """
        if self.doc_info.get('doc_path'):
            file_path = self.doc_info['doc_path']
            image = Image.open(file_path)
            return image
        elif self.doc_info.get('doc_data'):
            base64_data = self.doc_info['doc_data'].split('base64,')[-1]
            binary_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(binary_data))
            return image
        else:
            raise ValueError("No image data provided")


class FormatDoc:
    def __init__(self, doc_info: Dict[str, Any], retain_splitted_documents: bool = False):
        self.doc_info = doc_info
        self.retain_splitted_documents = retain_splitted_documents

    def convert(self) -> Dict[str, Any]:
        """
        Convert document data to base64-encoded format and return as part of the response.

        Returns:
            Dict: Conversion result with base64-encoded document data.
        """
        try:
            converted_data = []
            doc_name = f"{self.doc_info['doc_id']}_page_1_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            doc_data = None

            # Check if doc_data is provided and extract base64 data if necessary
            if self.doc_info.get('doc_data'):
                base64_data = self.doc_info['doc_data'].split('base64,')
                if len(base64_data) == 2:
                    doc_data = base64_data[1]
                else:
                    doc_data = base64_data[0]

            # If doc_path is provided, read the file and encode it as base64
            if self.doc_info.get('doc_path'):
                with open(self.doc_info['doc_path'], 'rb') as file:
                    binary_data = file.read()
                    doc_data = base64.b64encode(binary_data).decode('utf-8')

            # Prepare the result data
            converted_data.append({
                'doc_uid': doc_name,
                'doc_data': doc_data,
                'page': 1,
                'doc_size': self.doc_info.get('doc_size'),
                'doc_id': self.doc_info['doc_id'],
                'parent_doc_uid': self.doc_info.get('parent_doc_uid'),
                'extension': self.doc_info['split_format'],
                'doc_path': self.doc_info.get('doc_path'),
                'doc_link': self.doc_info.get('doc_link')
            })

            return {'errCode': 0, 'datarec': converted_data, 'doc_id': self.doc_info['doc_id']}

        except Exception as e:
            datarec = {
                'doc_id': self.doc_info['doc_id'],
                'doc_data': self.doc_info.get('doc_data'),
                'doc_size': self.doc_info.get('doc_size')
            }
            return {'errCode': 1, 'msg': str(e), 'datarec': datarec}
