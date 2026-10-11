import sys
import os

# Ensure the root directory is on the path so modules can be imported reliably
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import tempfile
from PIL import Image, ImageEnhance, ImageFilter

# Import backend modules with safe fallback handling
try:
    from modules.image_compressor import compress_image_handler as compress_and_resize_image
except ImportError:
    compress_and_resize_image = None

# Robust import for image enhancer with built-in fallback
try:
    from modules.image_enhancer import enhance_image_quality 
except (ImportError, Exception):
    def enhance_image_quality(pil_img, sharpen_factor=1.0, contrast_factor=1.0, color_factor=1.0, upscale_factor=1):
        if pil_img is None:
            return None, "Please upload an image."
        res = pil_img.copy()
        orig_w, orig_h = res.size
        
        if sharpen_factor != 1.0:
            res = ImageEnhance.Sharpness(res).enhance(float(sharpen_factor))
        if contrast_factor != 1.0:
            res = ImageEnhance.Contrast(res).enhance(float(contrast_factor))
        if color_factor != 1.0:
            res = ImageEnhance.Color(res).enhance(float(color_factor))
            
        scale = int(upscale_factor) if upscale_factor else 1
        if scale > 1:
            res = res.resize((orig_w * scale, orig_h * scale), Image.Resampling.LANCZOS)
            res = res.filter(ImageFilter.DETAIL)
            
        new_w, new_h = res.size
        return res, f"Original: {orig_w}x{orig_h}px | Enhanced: {new_w}x{new_h}px ({scale}x Upscaled)"

try:
    from modules.background_remover import handle_background_removal as remove_background
except ImportError:
    remove_background = None

try:
    from modules.pdf_tool import remove_pdf_password as process_pdf
except ImportError:
    process_pdf = None

try:
    from modules.password_generator import generate_password
except ImportError:
    generate_password = None

try:
    from modules.unit_converter import convert_units
except ImportError:
    convert_units = None

try:
    from modules.password_saver import (
        add_entry,
        unlock_and_display,
        create_vault,
        is_vault_initialized,
    )
except ImportError:
    add_entry, unlock_and_display, create_vault, is_vault_initialized = (
        None,
        None,
        None,
        lambda: False,
    )

st.set_page_config(
    page_title="Human Utility AI Hub",
    page_icon="🛠️",
    layout="wide"
)

# --- CUSTOM THEME STYLING (Navy Blue Tabs & Light Grey Container) ---
st.markdown("""
<style>
    /* Main app background container -> Light Grey */
    .stApp {
        background-color: #f1f3f5;
        color: #212529;
    }
    
    /* Sidebar / Navigation panel -> Navy Blue */
    [data-testid="stSidebar"] {
        background-color: #1e3a8a;
        color: #ffffff;
    }
    
    /* Sidebar text, headers, and radio labels -> White */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    
    /* Sidebar Radio item hover / selection highlights */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        margin-bottom: 4px;
        padding: 4px 8px;
    }
    
    /* Primary Action Buttons (Deep Indigo / Slate) */
    .stButton>button {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2563eb !important;
    }
    
    /* Input and Selectbox styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 8px !important;
        border-color: #cbd5e1 !important;
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization for user tracking & modals
if "user_count" not in st.session_state:
    st.session_state.user_count = 505
if "show_privacy_modal" not in st.session_state:
    st.session_state.show_privacy_modal = True

# --- HELPER FUNCTIONS ---
def load_input_image(img_input):
    if img_input is None:
        return None
    if isinstance(img_input, str):
        return Image.open(img_input)
    if hasattr(img_input, "read"):
        return Image.open(img_input)
    return img_input

def convert_and_save_download(img, output_fmt):
    if img is None:
        return None
    if isinstance(img, str):
        img = Image.open(img)
        
    temp_dir = tempfile.gettempdir()
    fmt_lower = output_fmt.lower()
    ext = ".jpg" if fmt_lower in ["jpg", "jpeg"] else f".{fmt_lower}"
    out_path = os.path.join(temp_dir, f"processed_output{ext}")
    
    if fmt_lower in ["jpg", "jpeg"] and img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background
        
    save_fmt = "JPEG" if fmt_lower in ["jpg", "jpeg"] else fmt_lower.upper()
    img.save(out_path, format=save_fmt)
    return out_path

# --- HEADER & COUNTER ---
st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>Human Utility AI Hub</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #4b5563;'>👥 <b>Active Users:</b> {st.session_state.user_count:,}</p>", unsafe_allow_html=True)

if st.session_state.show_privacy_modal:
    with st.expander("🔒 Privacy First Notice (Click to Close/View)", expanded=True):
        st.markdown(
            "**Generated passwords are not saved automatically.**\n\n"
            "If you choose to save an entry in Local Password Vault, it is encrypted in `vault.enc` "
            "in the app's working directory and remains there until that file is deleted. "
            "Keep the vault file and its master password private."
        )
        if st.button("Understood & Continue"):
            st.session_state.show_privacy_modal = False
            st.rerun()

st.sidebar.title("🛠️ Available Services")
app_mode = st.sidebar.radio(
    "Select Service",
    [
        "Image Compression",
        "Image Enhancer",
        "Background Remover",
        "PDF Toolkit",
        "Password Generator",
        "Unit Converter",
        "Local Password Vault"
    ]
)

# --- TAB 1: Image Compression ---
if app_mode == "Image Compression":
    st.header("Image Compression & Resizer")
    st.markdown("Reduce file sizes and adjust image dimensions seamlessly.")
    
    col1, col2 = st.columns(2)
    with col1:
        img_input = st.file_uploader("Source Image", type=["jpg", "jpeg", "png", "webp"])
        quality_slider = st.slider("Quality Level", 10, 95, 60, step=5)
        out_format = st.selectbox("Output Format", ["JPEG", "PNG", "WEBP"])
        width_px = st.number_input("Width px (0 = Keep Original)", value=0, step=1)
        height_px = st.number_input("Height px (0 = Keep Original)", value=0, step=1)
        compress_btn = st.button("Compress & Resize", type="primary")

    with col2:
        if compress_btn:
            if img_input is None:
                st.info("ℹ️ Please upload an image first.")
            elif not compress_and_resize_image:
                st.error("❌ Module 'modules.image_compressor' is missing.")
            else:
                try:
                    img_obj = load_input_image(img_input)
                    res = compress_and_resize_image(img_obj, quality_slider, out_format, width_px, height_px)
                    out_img = res[0] if isinstance(res, tuple) else res
                    stats_text = res[1] if isinstance(res, tuple) else "Compression completed successfully."
                    
                    download_path = convert_and_save_download(out_img, out_format)
                    st.image(out_img, caption="Output Preview")
                    st.text_area("Compression & Resize Stats", value=stats_text, disabled=True)
                    with open(download_path, "rb") as file:
                        st.download_button("Download Processed File", data=file, file_name=f"compressed.{out_format.lower()}")
                except Exception as e:
                    st.error(f"❌ Compression Error: {str(e)}")

# --- TAB 2: Image Enhancer ---
elif app_mode == "Image Enhancer":
    st.header("Image Enhancer & Upscaler")
    st.markdown("Enhance photo clarity, sharpen fine details, and upscale resolution.")
    
    col1, col2 = st.columns(2)
    with col1:
        enh_input = st.file_uploader("Source Image for Enhancement", type=["jpg", "jpeg", "png", "webp"])
        scale_factor = st.radio("Upscale Factor", ["2x", "4x"], index=0)
        color_slider = st.slider("Color Factor / Enhancement", 0.5, 2.0, 1.2, 0.1)
        sharpen_check = st.checkbox("Apply Sharpening Filter", value=True)
        enh_out_format = st.selectbox("Download Format", ["PNG", "JPG", "JPEG"])
        enhance_btn = st.button("Enhance Image", type="primary")

    with col2:
        if enhance_btn:
            if enh_input is None:
                st.info("ℹ️ Please upload an image first.")
            elif not enhance_image_quality:
                st.error("❌ Module 'modules.image_enhancer' is missing.")
            else:
                try:
                    img_obj = load_input_image(enh_input)
                    upscale_val = int(str(scale_factor).replace("x", "").strip())
                    sharpen_factor = 2.0 if sharpen_check else 1.0
                    
                    res = enhance_image_quality(
                        img_obj,
                        sharpen_factor=sharpen_factor,
                        contrast_factor=1.0,
                        color_factor=color_slider,
                        upscale_factor=upscale_val
                    )
                    out_img = res[0] if isinstance(res, tuple) else res
                    stats_msg = res[1] if isinstance(res, tuple) else "✨ Image enhancement complete!"
                    
                    download_path = convert_and_save_download(out_img, enh_out_format)
                    st.image(out_img, caption="Enhanced Output")
                    st.text_area("Status", value=stats_msg, disabled=True)
                    with open(download_path, "rb") as file:
                        st.download_button("Download Enhanced Image", data=file, file_name=f"enhanced.{enh_out_format.lower()}")
                except Exception as e:
                    st.error(f"❌ Enhancement Error: {str(e)}")

# --- TAB 3: Background Remover ---
elif app_mode == "Background Remover":
    st.header("Background Remover")
    st.markdown("Isolate main subjects from image backgrounds automatically.")
    
    col1, col2 = st.columns(2)
    with col1:
        bg_input = st.file_uploader("Source Image (JPG, PNG, WEBP, etc.)", type=["jpg", "jpeg", "png", "webp"])
        bg_out_fmt = st.selectbox("Output Format for Download", ["PNG", "JPEG", "WEBP"])
        bg_btn = st.button("Remove Background", type="primary")

    with col2:
        if bg_btn:
            if bg_input is None:
                st.info("ℹ️ Please upload an image first.")
            elif not remove_background:
                st.error("❌ Module 'modules.background_remover' is missing.")
            else:
                try:
                    img_obj = load_input_image(bg_input)
                    res = remove_background(img_obj)
                    out_img = res[0] if isinstance(res, tuple) else res
                    
                    download_path = convert_and_save_download(out_img, bg_out_fmt)
                    st.image(out_img, caption="Result Preview")
                    st.text_area("Status", value="✂️ Background successfully removed!", disabled=True)
                    with open(download_path, "rb") as file:
                        st.download_button("Download Processed File", data=file, file_name=f"no_bg.{bg_out_fmt.lower()}")
                except Exception as e:
                    st.error(f"❌ Background Removal Error: {str(e)}")

# --- TAB 4: PDF Toolkit ---
elif app_mode == "PDF Toolkit":
    st.header("PDF Toolkit")
    st.markdown("Merge documents, extract text content, convert pages to images, or unlock files.")
    
    col1, col2 = st.columns(2)
    with col1:
        pdf_input = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)
        pdf_action = st.selectbox(
            "Action",
            ["Merge PDFs", "Extract Text", "Convert Pages to Images", "Remove PDF Password"]
        )
        pdf_password = st.text_input("PDF Password (If Encrypted)", type="password", placeholder="Enter password if required...")
        pdf_btn = st.button("Process PDF", type="primary")

    with col2:
        if pdf_btn:
            if not pdf_input:
                st.info("ℹ️ Please upload at least one PDF file.")
            elif not process_pdf:
                st.error("❌ Module 'modules.pdf_tool' is missing.")
            else:
                try:
                    res = process_pdf(pdf_input, pdf_action, pdf_password)
                    if isinstance(res, tuple):
                        output_file, status_text = res
                    else:
                        output_file, status_text = res, "PDF processed successfully."
                    
                    st.text_area("Extracted Content / Status", value=str(status_text), disabled=True)
                    if output_file and os.path.exists(str(output_file)):
                        with open(output_file, "rb") as file:
                            st.download_button("Download Processed File Output", data=file, file_name="processed_output.pdf")
                except Exception as e:
                    st.error(f"❌ PDF Processing Error: {str(e)}")

# --- TAB 5: Password Generator ---
elif app_mode == "Password Generator":
    st.header("Secure Password Generator")
    st.markdown("Create randomized, high-entropy passwords tailored to custom safety requirements.")    
    col1, col2 = st.columns(2)
    with col1:
        pwd_length = st.slider("Password Length", 8, 64, 16, step=1)
        use_upper = st.checkbox("Include Uppercase (A-Z)", value=True)
        use_digits = st.checkbox("Include Numbers (0-9)", value=True)
        use_symbols = st.checkbox("Include Symbols (!@#$)", value=True)
        use_nature = st.checkbox("Include Nature Element 🌱", value=True)
        gen_btn = st.button("Generate Password", type="primary")
        
        with st.expander("Storage & Recovery Information"):
            st.markdown(
                "Generated passwords are displayed in this app but **are not saved automatically**.\n\n"
                "To keep one, open **Local Password Vault**, initialize or unlock it with your master password, "
                "enter the service, username, and generated password, then choose **Save New Entry**. "
                "The vault is stored as `vault.enc` in the app's working directory. Its contents are encrypted "
                "using a key derived from your master password."
            )

    with col2:
        if gen_btn:
            if not generate_password:
                st.error("❌ Module 'modules.password_generator' is missing.")
            else:
                try:
                    pwd_result = generate_password(pwd_length, use_upper, use_digits, use_symbols, use_nature)
                    st.text_input("Generated Password", value=pwd_result, disabled=False)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- TAB 6: Unit Converter ---
elif app_mode == "Unit Converter":
    st.header("Unit Converter")
    st.markdown("Perform fast conversions across standard physical units.")
    
    col1, col2 = st.columns(2)
    with col1:
        unit_val = st.number_input("Value", value=1.0)
        category = st.selectbox("Category", ["Length", "Weight", "Temperature"])
        unit_from = st.text_input("From Unit", placeholder="e.g. km, kg, C")
        unit_to = st.text_input("To Unit", placeholder="e.g. miles, lbs, F")
        convert_btn = st.button("Convert", type="primary")

    with col2:
        if convert_btn:
            if not convert_units:
                st.error("❌ Module 'modules.unit_converter' is missing.")
            else:
                try:
                    conv_res = convert_units(unit_val, category, unit_from, unit_to)
                    st.text_area("Result", value=conv_res, disabled=True)
                except Exception as e:
                    st.error(f"❌ Conversion Error: {str(e)}")

# --- TAB 7: Password Vault ---
elif app_mode == "Local Password Vault":
    st.header("Encrypted Local Password Vault")
    vault_exists = is_vault_initialized() if is_vault_initialized else False

    if not vault_exists:
        st.markdown("#### Initial Setup: Set Master Password")
        new_master = st.text_input("Create Master Password", type="password")
        confirm_master = st.text_input("Confirm Master Password", type="password")
        create_btn = st.button("Initialize Vault", type="primary")
        
        if create_btn:
            if not create_vault:
                st.error("❌ Module 'modules.password_saver' missing.")
            else:
                msg, success = create_vault(new_master, confirm_master)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)
    else:
        master_pwd = st.text_input("Master Password", type="password", placeholder="Enter Master Password...")
        col_unl, _ = st.columns([1, 3])
        unlock_clicked = col_unl.button("Unlock Vault")

        if unlock_clicked:
            status_msg, rows = unlock_and_display(master_pwd)
            if rows is not None and len(rows) > 0:
                st.success(status_msg)
                st.table(rows)
            else:
                st.warning(status_msg)

        st.markdown("---")
        st.subheader("Save New Entry")
        svc_input = st.text_input("Service / Website", placeholder="e.g. Portal")
        usr_input = st.text_input("Username / Email", placeholder="e.g. user@domain.com")
        pwd_input = st.text_input("Password", type="password", placeholder="Stored password...")
        notes_input = st.text_input("Notes (Optional)", placeholder="e.g. PIN code")
        save_entry_btn = st.button("Save New Entry", type="primary")

        if save_entry_btn:
            if not add_entry:
                st.error("❌ Module missing.")
            else:
                msg, rows = add_entry(svc_input, usr_input, pwd_input, notes_input, master_pwd)
                if rows:
                    st.success(msg)
                    st.table(rows)
                else:
                    st.warning(msg)