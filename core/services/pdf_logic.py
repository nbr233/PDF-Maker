import os
from pypdf import PdfReader, PdfWriter
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from pdf2image import convert_from_path

def pdf_to_word(pdf_path, output_path):
    """Convert PDF to DOCX using pdf2docx (preserves layout, tables, images)."""
    from pdf2docx import Converter
    cv = Converter(pdf_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()
    return output_path

def merge_pdfs(file_paths, output_path):
    writer = PdfWriter()
    for path in file_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def split_pdf(file_path, pages_to_keep, output_path):
    """
    pages_to_keep: list of 0-indexed page numbers
    """
    reader = PdfReader(file_path)
    writer = PdfWriter()
    
    for i in pages_to_keep:
        if 0 <= i < len(reader.pages):
            writer.add_page(reader.pages[i])
            
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def image_to_pdf(image_paths, output_path):
    images = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)
    
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:])
    return output_path

def word_to_pdf(word_path, output_path):
    """
    Simplified Word to PDF using reportlab and python-docx.
    Only extracts text and basic structure.
    """
    doc = Document(word_path)
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 40
    
    for para in doc.paragraphs:
        if y < 40:
            c.showPage()
            y = height - 40
        
        # Simple text wrapping could be added here, but for now:
        text = para.text
        c.drawString(40, y, text[:90]) # Rudimentary truncation/line handling
        y -= 20
        
    c.save()
    return output_path

def pdf_to_images(pdf_path, output_dir):
    """
    Converts PDF pages to images. 
    Note: Requires poppler on the system.
    """
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        path = os.path.join(output_dir, f"page_{i+1}.jpg")
        image.save(path, "JPEG")
        image_paths.append(path)
    return image_paths

def protect_pdf(pdf_path, password, output_path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
        
    writer.encrypt(password)
    
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path
