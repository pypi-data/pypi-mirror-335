import os
from typing import Dict, List, Any
from docsplit.converters.pdf_converter import PdfToJpg, PdfToPdf
from docsplit.converters.image_converter import HeicAndPngToJpg, HeicAndPngAndJpgAndJpegToPdf, FormatDoc
from docsplit.converters.merge_converter import MergePdf  # Import the merge class

class DocumentHandler:
    def __init__(self):
        # Mapping for both split and merge conversions
        self.split_docs_mapping = {
            'pdf_to_jpg': PdfToJpg,
            'pdf_to_pdf': PdfToPdf,
            'heic_to_jpg': HeicAndPngToJpg,
            'png_to_jpg': HeicAndPngToJpg,
            'heic_to_pdf': HeicAndPngAndJpgAndJpegToPdf,
            'png_to_pdf': HeicAndPngAndJpgAndJpegToPdf,
            'jpg_to_pdf': HeicAndPngAndJpgAndJpegToPdf,
            'jpeg_to_pdf': HeicAndPngAndJpgAndJpegToPdf,
            'jpg_to_jpg': FormatDoc,
            'jpeg_to_jpg': FormatDoc,
            'jpeg_to_jpeg': FormatDoc,
            'png_to_png': FormatDoc
        }

        self.merge_docs_mapping = {
            'pdf': MergePdf  # Only handling PDF merge here, adjust if needed for other formats
        }

        self.supported_extensions = ['pdf', 'png', 'jpg', 'heic', 'jpeg']

    def process_documents(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process documents for either splitting or merging based on action type.

        Args:
            payload (Dict): Contains 'data' key with list of documents and 'action' key for split or merge.

        Returns:
            Dict: Response with status and processed documents.
        """
        action = payload.get('action', 'split')
        if action == 'split':
            return self.split_documents(payload)
        elif action == 'merge':
            return self.merge_documents(payload)
        else:
            return {'errCode': 1, 'msg': 'Invalid action. Supported actions are "split" or "merge".'}

    def split_documents(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a list of documents for splitting/conversion.

        Args:
            payload (Dict): Contains 'data' key with list of documents to process.

        Returns:
            Dict: Response with status and converted documents.
        """
        doc_list = payload.get('data', [])
        response = {'errCode': 0, 'data': []}

        for doc in doc_list:
            try:
                doc_response = self._process_document(doc, payload)
                response['data'].append(doc_response)
            except Exception as e:
                response['data'].append({
                    'errCode': 1,
                    'msg': str(e),
                    'datarec': self._error_datarec(doc)
                })

        return response

    def merge_documents(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge documents based on provided document paths.

        Args:
            payload (Dict): Contains 'data' key with list of documents to merge.

        Returns:
            Dict: Response with status and merged document.
        """
        doc_path_list = payload.get('doc_path_list', [])
        response = {'errCode': 0, 'data': []}

        try:
            # Initialize the MergePdf object
            merge_pdf_obj = MergePdf(doc_info={'doc_path_list':doc_path_list})
            merge_response = merge_pdf_obj.merge()

            if merge_response.get('errCode') == 0:
                response['data'].append(merge_response.get('datarec'))
            else:
                response['errCode'] = 1
                response['msg'] = merge_response.get('msg')

        except Exception as e:
            response['errCode'] = 1
            response['msg'] = str(e)

        return response

    def _process_document(self, doc: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single document for conversion.

        Args:
            doc (Dict): Document details.
            payload (Dict): Global payload with settings.

        Returns:
            Dict: Conversion result for the document.
        """
        file_extension = self._get_file_extension(doc)
        split_format = doc.get('split_format')

        if not self._validate_input(file_extension, split_format, doc):
            return {
                'errCode': 1,
                'msg': 'Invalid input: Unsupported file extension or missing split format',
                'datarec': self._error_datarec(doc)
            }

        converter_class = self.split_docs_mapping.get(f"{file_extension}_to_{split_format}")
        if not converter_class:
            return {
                'errCode': 1,
                'msg': f'Conversion from {file_extension} to {split_format} is not supported',
                'datarec': self._error_datarec(doc)
            }

        converter = converter_class(doc, payload.get('retain_splitted_documents', False))
        return converter.convert()

    def _get_file_extension(self, doc: Dict[str, Any]) -> str:
        """
        Extract file extension from document details.

        Args:
            doc (Dict): Document details.

        Returns:
            str: File extension in lowercase.
        """
        if doc.get('extension'):
            return doc['extension'].lower()
        return os.path.splitext(doc.get('doc_name', ''))[1].lstrip('.').lower()

    def _validate_input(self, file_extension: str, split_format: str, doc: Dict[str, Any]) -> bool:
        """
        Validate document input for conversion.

        Args:
            file_extension (str): Source file extension.
            split_format (str): Target format.
            doc (Dict): Document details.

        Returns:
            bool: True if input is valid, False otherwise.
        """
        if file_extension not in self.supported_extensions:
            return False
        if not split_format:
            return False
        return True

    def _error_datarec(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create error data record for failed conversions.

        Args:
            doc (Dict): Document details.

        Returns:
            Dict: Error data record.
        """
        return {
            'doc_id': doc.get('doc_id'),
            'doc_data': doc.get('doc_data'),
            'doc_size': doc.get('doc_size')
        }
