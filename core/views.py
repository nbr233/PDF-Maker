import os
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files import File
from django.http import HttpResponse
from .models import ProcessedFile
from .services import pdf_logic

def index(request):
    tools = [
        {'id': 'pdf-maker', 'name': 'PDF Maker & Editor', 'desc': 'Add, delete, reorder pages & insert images interactively.', 'icon': 'edit_document', 'featured': True},
        {'id': 'merge', 'name': 'Merge PDF', 'desc': 'Combine multiple PDFs into one.', 'icon': 'merge'},
        {'id': 'split', 'name': 'Split PDF', 'desc': 'Extract or delete pages from a PDF.', 'icon': 'split'},
        {'id': 'img-to-pdf', 'name': 'Image to PDF', 'desc': 'Convert images to a high-quality PDF.', 'icon': 'image'},
        {'id': 'word-to-pdf', 'name': 'Word to PDF', 'desc': 'Convert DOCX files to PDF format.', 'icon': 'description'},
        {'id': 'pdf-to-img', 'name': 'PDF to Image', 'desc': 'Extract PDF pages as images.', 'icon': 'photo_library'},
        {'id': 'pdf-to-word', 'name': 'PDF to Word', 'desc': 'Convert PDF documents to editable DOCX format.', 'icon': 'article'},
        {'id': 'protect', 'name': 'Protect PDF', 'desc': 'Add a password to your PDF files.', 'icon': 'lock'},
    ]
    return render(request, 'core/index.html', {'tools': tools})

def merge_tool(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        if not files:
            return redirect('index')
            
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_paths = []
            for f in files:
                path = os.path.join(tmp_dir, f.name)
                with open(path, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                temp_paths.append(path)
            
            output_path = os.path.join(tmp_dir, 'merged.pdf')
            pdf_logic.merge_pdfs(temp_paths, output_path)
            
            with open(output_path, 'rb') as f:
                processed = ProcessedFile.objects.create(
                    original_name="merged.pdf",
                    tool_used="Merge"
                )
                processed.file.save('merged.pdf', File(f))
                
            return render(request, 'core/result.html', {'file': processed})
            
    return render(request, 'core/tool.html', {'tool_name': 'Merge PDF', 'id': 'merge', 'multi': True})

def split_tool(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        pages_str = request.POST.get('pages', '')
        if not file: return redirect('index')
        
        # Convert "1,2,3-5" to [0,1,2,3,4]
        pages = []
        try:
            for part in pages_str.split(','):
                if '-' in part:
                    start, end = part.split('-')
                    pages.extend(range(int(start)-1, int(end)))
                else:
                    pages.append(int(part)-1)
        except:
            return render(request, 'core/tool.html', {'error': 'Invalid page range format.'})

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, file.name)
            with open(input_path, 'wb+') as f:
                for chunk in file.chunks(): f.write(chunk)
            
            output_path = os.path.join(tmp_dir, 'split.pdf')
            pdf_logic.split_pdf(input_path, pages, output_path)
            
            with open(output_path, 'rb') as f:
                processed = ProcessedFile.objects.create(
                    original_name="split.pdf",
                    tool_used="Split"
                )
                processed.file.save('split.pdf', File(f))
            return render(request, 'core/result.html', {'file': processed})
            
    return render(request, 'core/tool.html', {'tool_name': 'Split PDF', 'id': 'split', 'has_pages': True})

def img_to_pdf_tool(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        if not files: return redirect('index')
            
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_paths = []
            for f in files:
                path = os.path.join(tmp_dir, f.name)
                with open(path, 'wb+') as dest:
                    for chunk in f.chunks(): dest.write(chunk)
                temp_paths.append(path)
            
            output_path = os.path.join(tmp_dir, 'images.pdf')
            pdf_logic.image_to_pdf(temp_paths, output_path)
            
            with open(output_path, 'rb') as f:
                processed = ProcessedFile.objects.create(
                    original_name="images.pdf",
                    tool_used="Image to PDF"
                )
                processed.file.save('images.pdf', File(f))
            return render(request, 'core/result.html', {'file': processed})
            
    return render(request, 'core/tool.html', {'tool_name': 'Image to PDF', 'id': 'img-to-pdf', 'multi': True})

def word_to_pdf_tool(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file: return redirect('index')
            
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, file.name)
            with open(input_path, 'wb+') as f:
                for chunk in file.chunks(): f.write(chunk)
            
            output_path = os.path.join(tmp_dir, 'converted.pdf')
            pdf_logic.word_to_pdf(input_path, output_path)
            
            with open(output_path, 'rb') as f:
                processed = ProcessedFile.objects.create(
                    original_name=file.name.replace('.docx', '.pdf'),
                    tool_used="Word to PDF"
                )
                processed.file.save(processed.original_name, File(f))
            return render(request, 'core/result.html', {'file': processed})
            
    return render(request, 'core/tool.html', {'tool_name': 'Word to PDF', 'id': 'word-to-pdf'})

def protect_tool(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        password = request.POST.get('password')
        if not file or not password: return redirect('index')
            
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, file.name)
            with open(input_path, 'wb+') as f:
                for chunk in file.chunks(): f.write(chunk)
            
            output_path = os.path.join(tmp_dir, 'protected.pdf')
            pdf_logic.protect_pdf(input_path, password, output_path)
            
            with open(output_path, 'rb') as f:
                processed = ProcessedFile.objects.create(
                    original_name=file.name,
                    tool_used="Protect"
                )
                processed.file.save(f"protected_{file.name}", File(f))
            return render(request, 'core/result.html', {'file': processed})
            
    return render(request, 'core/tool.html', {'tool_name': 'Protect PDF', 'id': 'protect', 'has_password': True})

def pdf_to_img_tool(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file: return redirect('index')
            
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, file.name)
            with open(input_path, 'wb+') as f:
                for chunk in file.chunks(): f.write(chunk)
            
            try:
                images = pdf_logic.pdf_to_images(input_path, tmp_dir)
                if images:
                    with open(images[0], 'rb') as f:
                        processed = ProcessedFile.objects.create(
                            original_name=os.path.basename(images[0]),
                            tool_used="PDF to Image"
                        )
                        processed.file.save(os.path.basename(images[0]), File(f))
                    return render(request, 'core/result.html', {'file': processed})
            except Exception as e:
                return render(request, 'core/tool.html', {'error': f'Conversion failed: {str(e)}. Poppler might not be installed.'})
                
    return render(request, 'core/tool.html', {'tool_name': 'PDF to Image', 'id': 'pdf-to-img'})

import json
import base64
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from PIL import Image as PILImage
import io

def pdf_maker_tool(request):
    """Interactive PDF editor/maker page."""
    return render(request, 'core/pdf_maker.html')

def _hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def _apply_overlays(base_page, overlays, pw, ph):
    """Draw text/image overlays onto base_page in-place using reportlab."""
    if not overlays:
        return
    from reportlab.lib.utils import ImageReader
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(pw, ph))

    for ov in overlays:
        otype = ov.get('type')
        # positions are 0-1 fractions of page size, y from top (UI) → convert to pts from bottom
        x_pt  = float(ov.get('x', 0)) * pw
        y_top = float(ov.get('y', 0)) * ph
        ow_pt = float(ov.get('w', 0.3)) * pw
        oh_pt = float(ov.get('h', 0.1)) * ph
        y_pt  = ph - y_top - oh_pt   # reportlab y from bottom

        if otype == 'text':
            text      = ov.get('text', '')
            font_size = max(6, int(ov.get('fontSize', 14)))
            r, g, b   = _hex_to_rgb(ov.get('color', '#000000'))
            c.setFillColorRGB(r, g, b)
            c.setFont('Helvetica', font_size)
            # Simple word-wrap within element width
            line_h  = font_size * 1.35
            cur_y   = y_pt + oh_pt - font_size
            words   = text.split()
            line    = ''
            for word in words:
                test = (line + ' ' + word).strip()
                if c.stringWidth(test, 'Helvetica', font_size) <= ow_pt:
                    line = test
                else:
                    if line:
                        c.drawString(x_pt, cur_y, line)
                        cur_y -= line_h
                    line = word
                if cur_y < y_pt:
                    break
            if line and cur_y >= y_pt:
                c.drawString(x_pt, cur_y, line)

        elif otype == 'image':
            src = ov.get('src', '')
            if ',' in src:
                src = src.split(',', 1)[1]
            try:
                img_bytes = base64.b64decode(src)
                img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
                ibuf = io.BytesIO()
                img.save(ibuf, format='JPEG', quality=90)
                ibuf.seek(0)
                c.drawImage(ImageReader(ibuf), x_pt, y_pt, width=ow_pt, height=oh_pt,
                            preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

    c.save()
    buf.seek(0)
    overlay_page = PdfReader(buf).pages[0]
    base_page.merge_page(overlay_page)


@csrf_exempt
def pdf_maker_process(request):
    """
    Receives a JSON payload describing the document state and builds the final PDF.
    Payload:
    {
      "pages": [
        {"type": "pdf",   "src": "data:application/pdf;base64,...", "page_index": 0},
        {"type": "image", "src": "data:image/jpeg;base64,..."},
        {"type": "blank"}
      ]
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body  = request.body
        data  = json.loads(body)
        pages   = data.get('pages', [])
        sources = data.get('sources', {})  # key -> data URI string
    except Exception as e:
        return JsonResponse({'error': f'Parse error: {e}'}, status=400)

    def resolve(page_or_ov):
        """Replace src_key with the actual data URI src."""
        key = page_or_ov.get('src_key')
        if key and key in sources:
            page_or_ov['src'] = sources[key]
        return page_or_ov

    writer = PdfWriter()

    for page_def in pages:
        resolve(page_def)
        ptype    = page_def.get('type')
        overlays = [resolve(o) for o in page_def.get('overlays', [])]


        if ptype == 'blank':
            buf = io.BytesIO()
            c = rl_canvas.Canvas(buf, pagesize=A4)
            c.save()
            buf.seek(0)
            blank_reader = PdfReader(buf)
            writer.add_page(blank_reader.pages[0])

        elif ptype == 'image':
            src = page_def.get('src', '')
            if ',' in src:
                src = src.split(',', 1)[1]
            img_bytes = base64.b64decode(src)
            img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
            a4_w, a4_h = A4
            img_ratio = img.width / img.height
            a4_ratio  = a4_w / a4_h
            if img_ratio > a4_ratio:
                draw_w = a4_w;  draw_h = a4_w / img_ratio
            else:
                draw_h = a4_h;  draw_w = a4_h * img_ratio
            x_off = (a4_w - draw_w) / 2
            y_off = (a4_h - draw_h) / 2
            buf = io.BytesIO()
            c = rl_canvas.Canvas(buf, pagesize=A4)
            img_buf = io.BytesIO()
            img.save(img_buf, format='JPEG', quality=90)
            img_buf.seek(0)
            from reportlab.lib.utils import ImageReader
            c.drawImage(ImageReader(img_buf), x_off, y_off, width=draw_w, height=draw_h)
            c.save()
            buf.seek(0)
            writer.add_page(PdfReader(buf).pages[0])

        elif ptype == 'pdf':
            src = page_def.get('src', '')
            page_index = int(page_def.get('page_index', 0))
            if ',' in src:
                src = src.split(',', 1)[1]
            pdf_bytes = base64.b64decode(src)
            reader = PdfReader(io.BytesIO(pdf_bytes))
            if 0 <= page_index < len(reader.pages):
                writer.add_page(reader.pages[page_index])

        # Apply overlays onto the last added page
        if overlays and len(writer.pages) > 0:
            last_page = writer.pages[-1]
            pw = float(last_page.mediabox.width)
            ph = float(last_page.mediabox.height)
            _apply_overlays(last_page, overlays, pw, ph)

    # Write final PDF
    out_buf = io.BytesIO()
    writer.write(out_buf)
    out_buf.seek(0)

    processed = ProcessedFile.objects.create(
        original_name='edited_document.pdf',
        tool_used='PDF Maker'
    )
    processed.file.save('edited_document.pdf', File(out_buf))

    return JsonResponse({
        'success': True,
        'download_url': processed.file.url,
        'filename': processed.original_name
    })

def pdf_to_word_tool(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return redirect('index')

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, file.name)
            with open(input_path, 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            out_name = os.path.splitext(file.name)[0] + '.docx'
            output_path = os.path.join(tmp_dir, out_name)

            try:
                pdf_logic.pdf_to_word(input_path, output_path)
            except Exception as e:
                return render(request, 'core/tool.html', {
                    'tool_name': 'PDF to Word',
                    'id': 'pdf-to-word',
                    'error': f'Conversion failed: {str(e)}',
                })

            with open(output_path, 'rb') as f:
                processed = ProcessedFile.objects.create(
                    original_name=out_name,
                    tool_used='PDF to Word'
                )
                processed.file.save(out_name, File(f))

        return render(request, 'core/result.html', {'file': processed})

    return render(request, 'core/tool.html', {
        'tool_name': 'PDF to Word',
        'id': 'pdf-to-word',
    })
