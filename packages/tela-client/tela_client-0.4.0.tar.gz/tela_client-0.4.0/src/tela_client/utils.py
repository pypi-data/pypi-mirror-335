from PyPDF2 import PdfReader, PdfWriter
import tempfile
import os

def split_pdf(input_path, output_dir, pages_per_split=10):
    input_pdf = PdfReader(input_path)
    output_pdfs = []
    num_pages = len(input_pdf.pages)
    original_filename = os.path.splitext(os.path.basename(input_path))[0]
    
    for i in range(0, num_pages, pages_per_split):
        output_pdf = PdfWriter()
        start_page = i + 1
        end_page = min(i + pages_per_split, num_pages)
        
        for j in range(i, end_page):
            output_pdf.add_page(input_pdf.pages[j])
        
        # Create a file with original name and page range
        output_filename = f"{original_filename}_pages_{start_page}-{end_page}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as output_file:
            output_pdf.write(output_file)

        output_pdfs.append(output_path)
    
    return output_pdfs


def get_all_files_in_folder(folder_path):
    files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files

def count_pdf_pages(pdf_path):
    """
    Count the number of pages in a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        int: Number of pages in the PDF.
    """
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        return len(pdf_reader.pages)
