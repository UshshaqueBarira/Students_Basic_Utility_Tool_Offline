import os
import tempfile
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter


def remove_pdf_password(files, action="Merge PDFs", password=""):
    """Handles PDF operations: Merging, Extracting Text, Converting Pages to Images,

    and Removing Passwords.
    """
    if not files:
        return None, "⚠️ Please upload at least one PDF file."

    temp_dir = tempfile.gettempdir()

    # --- ACTION 1: REMOVE PDF PASSWORD ---
    if action == "Remove PDF Password":
        file_path = files[0].name if hasattr(files[0], "name") else files[0]
        reader = PdfReader(file_path)

        if reader.is_encrypted:
            if not password:
                return None, "⚠️ Password is required for encrypted PDF."
            unlocked = reader.decrypt(password)
            if not unlocked:
                return None, "❌ Incorrect password provided."

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        output_path = os.path.join(temp_dir, "unlocked_document.pdf")
        with open(output_path, "wb") as f_out:
            writer.write(f_out)

        return output_path, "🔓 Password removed successfully!"

    # --- ACTION 2: MERGE PDFs ---
    elif action == "Merge PDFs":
        writer = PdfWriter()

        for file in files:
            f_path = file.name if hasattr(file, "name") else file
            reader = PdfReader(f_path)

            if reader.is_encrypted:
                if password and not reader.decrypt(password):
                    return (
                        None,
                        f"❌ Incorrect password for {os.path.basename(f_path)}",
                    )

            for page in reader.pages:
                writer.add_page(page)

        output_path = os.path.join(temp_dir, "merged_output.pdf")
        with open(output_path, "wb") as f_out:
            writer.write(f_out)

        return output_path, f"✅ Successfully merged {len(files)} PDF(s)."

    # --- ACTION 3: EXTRACT TEXT ---
    elif action == "Extract Text":
        f_path = files[0].name if hasattr(files[0], "name") else files[0]
        reader = PdfReader(f_path)

        if reader.is_encrypted:
            if not password or not reader.decrypt(password):
                return None, "❌ Password required or incorrect password."

        extracted_text = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            extracted_text.append(f"--- Page {idx + 1} ---\n{text}")

        full_text = "\n\n".join(extracted_text)
        return None, full_text if full_text.strip() else "No readable text found."

    # --- ACTION 4: CONVERT PAGES TO IMAGES ---
    elif action == "Convert Pages to Images":
        f_path = files[0].name if hasattr(files[0], "name") else files[0]
        doc = fitz.open(f_path)

        if doc.is_encrypted:
            if not password or not doc.authenticate(password):
                return None, "❌ Password required or incorrect password."

        page = doc.load_page(0)  # Convert first page
        pix = page.get_pixmap()
        output_path = os.path.join(temp_dir, "pdf_page_1.png")
        pix.save(output_path)

        return output_path, "🖼️ First page converted to image successfully!"

    return None, "❌ Invalid Action Selected."