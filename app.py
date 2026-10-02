import gradio as gr
from PIL import Image
import os
import tempfile

# Import backend modules with safe fallback handling
try:
    from modules.image_compressor import compress_image_handler as compress_and_resize_image
except ImportError:
    compress_and_resize_image = None

try:
    from modules.image_enhancer import enhance_image_quality as enhance_image
except ImportError as e:
    print(f"DEBUG ENHANCER ERROR: {e}")  # <-- This will print the actual error to your console
    enhance_image = None

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


user_counter = 500


def get_user_count():
    global user_counter
    user_counter += 1
    return f"👥 **Active Users:** {user_counter:,}"


def load_input_image(img_input):
    if img_input is None:
        return None
    if isinstance(img_input, str):
        return Image.open(img_input)
    if isinstance(img_input, Image.Image):
        return img_input
    return Image.fromarray(img_input)


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


# --- SAFE WRAPPER FUNCTIONS ---


def safe_compress(img_input, quality, fmt, width, height):
    if img_input is None:
        return None, None, "⚠️ Please upload an image first."
    if not compress_and_resize_image:
        return None, None, "❌ Module 'modules.image_compressor' is missing."
    try:
        img_obj = load_input_image(img_input)
        res = compress_and_resize_image(img_obj, quality, fmt, width, height)

        out_img = res[0] if isinstance(res, tuple) else res
        stats_text = (
            res[1] if isinstance(res, tuple) else "Compression completed successfully."
        )

        download_file = convert_and_save_download(out_img, fmt)
        return out_img, download_file, stats_text
    except Exception as e:
        return None, None, f"❌ Compression Error: {str(e)}"


def safe_enhance(img_input, scale, output_format):
    if img_input is None:
        return None, None, "⚠️ Please upload an image first."
    if not enhance_image:
        return None, None, "❌ Module 'modules.image_enhancer' is missing."
    try:
        img_obj = load_input_image(img_input)

        # Parse scale string (e.g., "2x" -> 2)
        try:
            upscale_val = int(str(scale).replace("x", "").strip())
        except ValueError:
            upscale_val = 2

        res = enhance_image(
            img_obj,
            upscale_factor=upscale_val,
        )

        out_img = res[0] if isinstance(res, tuple) else res
        stats_text = res[1] if isinstance(res, tuple) else "Enhancement complete!"
        download_file = convert_and_save_download(out_img, output_format)
        return out_img, download_file, stats_text
    except Exception as e:
        return None, None, f"❌ Enhancement Error: {str(e)}"


def safe_remove_bg(img_input, out_fmt):
    if img_input is None:
        return None, None, "⚠️ Please upload an image first."
    if not remove_background:
        return None, None, "❌ Module 'modules.background_remover' is missing."
    try:
        img_obj = load_input_image(img_input)
        res = remove_background(img_obj)
        out_img = res[0] if isinstance(res, tuple) else res

        download_file = convert_and_save_download(out_img, out_fmt)
        return out_img, download_file, "✂️ Background successfully removed!"
    except Exception as e:
        return None, None, f"❌ Background Removal Error: {str(e)}"


def safe_process_pdf(files, action, password):
    if not files:
        return None, "⚠️ Please upload at least one PDF file."
    if not process_pdf:
        return None, "❌ Module 'modules.pdf_tool' is missing."
    try:
        res = process_pdf(files, action, password)
        if isinstance(res, tuple):
            return res[0], res[1]
        return res, "PDF processed successfully."
    except Exception as e:
        return None, f"❌ PDF Processing Error: {str(e)}"


def safe_generate_pwd(length, upper, digits, symbols, nature):
    if not generate_password:
        return "❌ Module 'modules.password_generator' is missing."
    try:
        return generate_password(length, upper, digits, symbols, nature)
    except Exception as e:
        return f"❌ Error: {str(e)}"


def safe_convert_units(val, cat, unit_from, unit_to):
    if not convert_units:
        return "❌ Module 'modules.unit_converter' is missing."
    try:
        return convert_units(val, cat, unit_from, unit_to)
    except Exception as e:
        return f"❌ Conversion Error: {str(e)}"


custom_css = """
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    background-color: #f7f5f9 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

.header-bar {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 24px 32px;
    background: transparent;
    border-radius: 16px;
    color: #000000;
    margin-bottom: 24px;
    box-shadow: none;
}
.header-title {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: #000000 !important;
    margin: 0 0 8px 0 !important;
    text-align: center !important;
    letter-spacing: 0.5px;
}
.header-title h1 {
    color: #000000 !important;
    font-weight: 800 !important;
}
.header-counter {
    font-size: 1.05rem !important;
    color: #000000 !important;
    background: transparent;
    padding: 6px 16px;
}
.header-counter * {
    color: #000000 !important;
}

.nav-sidebar {
    background: #ffffff !important;
    border: 1px solid #E1D5E7 !important;
    border-radius: 14px !important;
    padding: 20px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
}

.sidebar-title {
    color: #2D1537 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    margin-bottom: 12px !important;
}

.vertical-nav .gr-form {
    border: none !important;
    background: transparent !important;
}
.vertical-nav label {
    display: flex !important;
    align-items: center !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    border-radius: 10px !important;
    border: 1px solid #E8E0EC !important;
    background-color: #F3EDF7 !important;
    color: #2D1537 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
.vertical-nav label:hover {
    background-color: #E8DEF8 !important;
    border-color: #D0BCFF !important;
    transform: translateX(4px) !important;
}
.vertical-nav label.selected, .vertical-nav label:has(input:checked) {
    background-color: #1B5E20 !important;
    color: #ffffff !important;
    border-color: #144918 !important;
    box-shadow: 0 4px 12px rgba(27, 94, 32, 0.25) !important;
}

button.primary {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    transition: all 0.2s ease !important;
}
button.primary:hover {
    background: linear-gradient(135deg, #144918 0%, #1B5E20 100%) !important;
    box-shadow: 0 4px 14px rgba(27, 94, 32, 0.35) !important;
}

.card-box {
    background: #ffffff !important;
    border: 1px solid #E1D5E7 !important;
    border-radius: 14px !important;
    padding: 24px !important;
    min-height: 580px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
    color: #1C1B1F !important;
}

.card-box h2 {
    color: #2D1537 !important;
    font-weight: 700 !important;
}

.modal-overlay {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(29, 14, 38, 0.55);
    backdrop-filter: blur(6px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}
.modal-content {
    background: #ffffff;
    padding: 32px;
    border-radius: 18px;
    max-width: 480px;
    width: 90%;
    border: 2px solid #E1D5E7;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}
"""

with gr.Blocks(css=custom_css, title="Human Utility AI Hub") as demo:

    with gr.Group(elem_classes="modal-overlay", visible=True) as privacy_modal:
        with gr.Column(elem_classes="modal-content"):
            gr.Markdown("### Privacy First")
            gr.Markdown(
                "**Generated passwords are not saved automatically.**\n\n"
                "If you choose to save an entry in Local Password Vault, it is encrypted in `vault.enc` "
                "in the app's working directory and remains there until that file is deleted. "
                "Keep the vault file and its master password private."
            )
            close_modal_btn = gr.Button("Understood & Continue", variant="primary")

    close_modal_btn.click(
        fn=lambda: gr.update(visible=False), inputs=None, outputs=privacy_modal
    )

    with gr.Group(
        elem_classes="modal-overlay", visible=False
    ) as password_storage_modal:
        with gr.Column(elem_classes="modal-content"):
            gr.Markdown("### Password Storage & Recovery")
            gr.Markdown(
                "Generated passwords are displayed in this app but **are not saved automatically**.\n\n"
                "To keep one, open **Local Password Vault**, initialize or unlock it with your master password, "
                "enter the service, username, and generated password, then choose **Save New Entry**. "
                "The vault is stored as `vault.enc` in the app's working directory. Its contents are encrypted "
                "using a key derived from your master password.\n\n"
                "To recover a saved password, open the vault from the same app directory and unlock it with "
                "the same master password. Back up `vault.enc` securely. **If you forget the master password, "
                "the vault cannot be decrypted or reset. If the vault file is lost and no backup exists, "
                "its saved entries cannot be recovered.**"
            )
            close_password_storage_btn = gr.Button("Close", variant="secondary")

    close_password_storage_btn.click(
        fn=lambda: gr.update(visible=False),
        inputs=None,
        outputs=password_storage_modal,
    )

    with gr.Column(elem_classes="header-bar"):
        gr.Markdown("# Human Utility AI Hub", elem_classes="header-title")
        counter_display = gr.Markdown(get_user_count(), elem_classes="header-counter")

    with gr.Row():
        with gr.Column(scale=1, min_width=280, elem_classes="nav-sidebar"):
            gr.Markdown("### Available Services", elem_classes="sidebar-title")
            nav_selector = gr.Radio(
                choices=[
                    "Image Compression",
                    "Image Enhancer",
                    "Background Remover",
                    "PDF Toolkit",
                    "Password Generator",
                    "Unit Converter",
                    "Local Password Vault",
                ],
                value="Image Compression",
                label="",
                elem_classes="vertical-nav",
            )

        with gr.Column(scale=4):

            # TAB 1: Image Compression
            with gr.Column(visible=True, elem_classes="card-box") as tab_compress:
                gr.Markdown("## Image Compression & Resizer")
                gr.Markdown(
                    "Reduce file sizes and adjust image dimensions seamlessly."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        img_input = gr.Image(label="Source Image", type="filepath")
                        quality_slider = gr.Slider(
                            minimum=10,
                            maximum=95,
                            value=60,
                            step=5,
                            label="Quality Level",
                        )
                        out_format = gr.Dropdown(
                            choices=["JPEG", "PNG", "WEBP"],
                            value="JPEG",
                            label="Output Format",
                        )
                        width_px = gr.Number(
                            label="Width px (0 = Keep Original)", value=0
                        )
                        height_px = gr.Number(
                            label="Height px (0 = Keep Original)", value=0
                        )
                        compress_btn = gr.Button(
                            "Compress & Resize", variant="primary"
                        )

                    with gr.Column(scale=1):
                        img_output = gr.Image(label="Output Preview")
                        download_output = gr.File(label="Download Processed File")
                        stats_output = gr.Textbox(
                            label="Compression & Resize Stats",
                            interactive=False,
                            lines=3,
                        )

                compress_btn.click(
                    fn=safe_compress,
                    inputs=[
                        img_input,
                        quality_slider,
                        out_format,
                        width_px,
                        height_px,
                    ],
                    outputs=[img_output, download_output, stats_output],
                )

            # TAB 2: Image Enhancer
            with gr.Column(visible=False, elem_classes="card-box") as tab_enhance:
                gr.Markdown("## Image Enhancer & Upscaler")
                gr.Markdown(
                    "Enhance photo clarity and upscale resolution using RealESRGAN."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        enh_input = gr.Image(label="Source Image", type="filepath")
                        scale_factor = gr.Radio(
                            choices=["2x", "4x"], value="2x", label="Upscale Factor"
                        )
                        enh_out_format = gr.Dropdown(
                            choices=["PNG", "JPG", "JPEG"],
                            value="PNG",
                            label="Download Format",
                        )
                        enhance_btn = gr.Button("Enhance Image", variant="primary")

                    with gr.Column(scale=1):
                        enh_output = gr.Image(label="Enhanced Output")
                        enh_file_output = gr.File(label="Download Enhanced Image")
                        enh_status = gr.Textbox(label="Status", interactive=False)

                enhance_btn.click(
                    fn=safe_enhance,
                    inputs=[enh_input, scale_factor, enh_out_format],
                    outputs=[enh_output, enh_file_output, enh_status],
                )

            # TAB 3: Background Remover
            with gr.Column(visible=False, elem_classes="card-box") as tab_bg_remove:
                gr.Markdown("## Background Remover")
                gr.Markdown(
                    "Isolate main subjects from image backgrounds automatically."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        bg_input = gr.Image(
                            label="Source Image (JPG, PNG, WEBP, etc.)",
                            type="filepath",
                        )
                        bg_out_fmt = gr.Dropdown(
                            choices=["PNG", "JPEG", "WEBP"],
                            value="PNG",
                            label="Output Format for Download",
                        )
                        bg_btn = gr.Button("Remove Background", variant="primary")

                    with gr.Column(scale=1):
                        bg_output = gr.Image(label="Result Preview")
                        bg_file_output = gr.File(label="Download Processed File")
                        bg_status = gr.Textbox(label="Status", interactive=False)

                bg_btn.click(
                    fn=safe_remove_bg,
                    inputs=[bg_input, bg_out_fmt],
                    outputs=[bg_output, bg_file_output, bg_status],
                )

            # TAB 4: PDF Toolkit
            with gr.Column(visible=False, elem_classes="card-box") as tab_pdf:
                gr.Markdown("## PDF Toolkit")
                gr.Markdown(
                    "Merge documents, extract text content, convert pages to images, or unlock files."
                )
                with gr.Row():
                    with gr.Column():
                        pdf_input = gr.File(
                            label="Upload PDF Files",
                            file_count="multiple",
                            file_types=[".pdf"],
                        )
                        pdf_action = gr.Dropdown(
                            choices=[
                                "Merge PDFs",
                                "Extract Text",
                                "Convert Pages to Images",
                                "Remove PDF Password",
                            ],
                            value="Merge PDFs",
                            label="Action",
                        )
                        pdf_password = gr.Textbox(
                            label="PDF Password (If Encrypted)",
                            type="password",
                            placeholder="Enter password if required...",
                        )
                        pdf_btn = gr.Button("Process PDF", variant="primary")

                    with gr.Column():
                        pdf_output_file = gr.File(label="Processed File Output")
                        pdf_output_text = gr.Textbox(
                            label="Extracted Content / Status", interactive=False
                        )

                pdf_btn.click(
                    fn=safe_process_pdf,
                    inputs=[pdf_input, pdf_action, pdf_password],
                    outputs=[pdf_output_file, pdf_output_text],
                )

            # TAB 5: Password Generator
            with gr.Column(visible=False, elem_classes="card-box") as tab_pwd_gen:
                gr.Markdown("## Secure Password Generator")
                gr.Markdown(
                    "Create randomized, high-entropy passwords tailored to custom safety requirements."
                )
                with gr.Row():
                    with gr.Column():
                        pwd_length = gr.Slider(
                            minimum=8,
                            maximum=64,
                            value=16,
                            step=1,
                            label="Password Length",
                        )
                        use_upper = gr.Checkbox(
                            value=True, label="Include Uppercase (A-Z)"
                        )
                        use_digits = gr.Checkbox(
                            value=True, label="Include Numbers (0-9)"
                        )
                        use_symbols = gr.Checkbox(
                            value=True, label="Include Symbols (!@#$)"
                        )
                        use_nature = gr.Checkbox(
                            value=True, label="Include Nature Element 🌱"
                        )
                        gen_btn = gr.Button("Generate Password", variant="primary")
                        storage_info_btn = gr.Button(
                            "Storage & Recovery", variant="secondary"
                        )

                        storage_info_btn.click(
                            fn=lambda: gr.update(visible=True),
                            inputs=None,
                            outputs=password_storage_modal,
                        )

                    with gr.Column():
                        generated_pwd = gr.Textbox(
                            label="Generated Password", interactive=False
                        )

                gen_btn.click(
                    fn=safe_generate_pwd,
                    inputs=[pwd_length, use_upper, use_digits, use_symbols, use_nature],
                    outputs=[generated_pwd],
                )

            # TAB 6: Unit Converter
            with gr.Column(visible=False, elem_classes="card-box") as tab_converter:
                gr.Markdown("## Unit Converter")
                gr.Markdown("Perform fast conversions across standard physical units.")
                with gr.Row():
                    with gr.Column():
                        unit_val = gr.Number(label="Value", value=1.0)
                        category = gr.Dropdown(
                            choices=["Length", "Weight", "Temperature"],
                            value="Length",
                            label="Category",
                        )
                        unit_from = gr.Textbox(
                            label="From Unit", placeholder="e.g. km, kg, C"
                        )
                        unit_to = gr.Textbox(
                            label="To Unit", placeholder="e.g. miles, lbs, F"
                        )
                        convert_btn = gr.Button("Convert", variant="primary")

                    with gr.Column():
                        conv_result = gr.Textbox(label="Result", interactive=False)

                convert_btn.click(
                    fn=safe_convert_units,
                    inputs=[unit_val, category, unit_from, unit_to],
                    outputs=[conv_result],
                )

            # TAB 7: Password Vault
            with gr.Column(visible=False, elem_classes="card-box") as tab_vault:
                gr.Markdown("## Encrypted Local Password Vault")
                vault_exists = is_vault_initialized() if is_vault_initialized else False

                with gr.Column(visible=not vault_exists) as setup_box:
                    gr.Markdown("#### Initial Setup: Set Master Password")
                    new_master = gr.Textbox(
                        label="Create Master Password", type="password"
                    )
                    confirm_master = gr.Textbox(
                        label="Confirm Master Password", type="password"
                    )
                    create_btn = gr.Button("Initialize Vault", variant="primary")
                    setup_status = gr.Textbox(label="Setup Status", interactive=False)

                with gr.Column(visible=vault_exists) as vault_box:
                    with gr.Row():
                        master_pwd = gr.Textbox(
                            label="Master Password",
                            type="password",
                            placeholder="Enter Master Password...",
                        )
                        unlock_btn = gr.Button("Unlock Vault", variant="secondary")

                status_msg = gr.Textbox(label="Status", interactive=False)

                with gr.Row():
                    svc_input = gr.Textbox(
                        label="Service / Website", placeholder="e.g. Portal"
                    )
                    usr_input = gr.Textbox(
                        label="Username / Email", placeholder="e.g. user@domain.com"
                    )
                    pwd_input = gr.Textbox(
                        label="Password", type="password", placeholder="Stored password..."
                    )
                    notes_input = gr.Textbox(
                        label="Notes (Optional)", placeholder="e.g. PIN code"
                    )

                save_entry_btn = gr.Button("Save New Entry", variant="primary")

                vault_table = gr.Dataframe(
                    headers=["Service", "Username / Email", "Password", "Notes"],
                    datatype=["str", "str", "str", "str"],
                    label="Saved Passwords",
                    interactive=False,
                )

                def safe_create_vault(pwd, confirm_pwd):
                    if not create_vault:
                        return (
                            "❌ Module 'modules.password_saver' missing.",
                            gr.update(visible=True),
                            gr.update(visible=False),
                        )
                    try:
                        msg, success = create_vault(pwd, confirm_pwd)
                        if success:
                            return (
                                msg,
                                gr.update(visible=False),
                                gr.update(visible=True),
                            )
                        return (
                            msg,
                            gr.update(visible=True),
                            gr.update(visible=False),
                        )
                    except Exception as e:
                        return (
                            f"❌ Setup Error: {str(e)}",
                            gr.update(visible=True),
                            gr.update(visible=False),
                        )

                def safe_unlock(master):
                    if not unlock_and_display:
                        return "❌ Module missing.", None
                    try:
                        return unlock_and_display(master)
                    except Exception as e:
                        return f"❌ Unlock Error: {str(e)}", None

                def safe_add_entry(svc, usr, pwd, notes, master):
                    if not add_entry:
                        return "❌ Module missing.", None
                    try:
                        return add_entry(svc, usr, pwd, notes, master)
                    except Exception as e:
                        return f"❌ Save Error: {str(e)}", None

                create_btn.click(
                    fn=safe_create_vault,
                    inputs=[new_master, confirm_master],
                    outputs=[setup_status, setup_box, vault_box],
                )

                unlock_btn.click(
                    fn=safe_unlock,
                    inputs=[master_pwd],
                    outputs=[status_msg, vault_table],
                )

                save_entry_btn.click(
                    fn=safe_add_entry,
                    inputs=[svc_input, usr_input, pwd_input, notes_input, master_pwd],
                    outputs=[status_msg, vault_table],
                )

    def switch_tab(selected_tab):
        return (
            gr.update(visible=(selected_tab == "Image Compression")),
            gr.update(visible=(selected_tab == "Image Enhancer")),
            gr.update(visible=(selected_tab == "Background Remover")),
            gr.update(visible=(selected_tab == "PDF Toolkit")),
            gr.update(visible=(selected_tab == "Password Generator")),
            gr.update(visible=(selected_tab == "Unit Converter")),
            gr.update(visible=(selected_tab == "Local Password Vault")),
        )

    nav_selector.change(
        fn=switch_tab,
        inputs=[nav_selector],
        outputs=[
            tab_compress,
            tab_enhance,
            tab_bg_remove,
            tab_pdf,
            tab_pwd_gen,
            tab_converter,
            tab_vault,
        ],
    )

    demo.load(fn=get_user_count, inputs=None, outputs=counter_display)

if __name__ == "__main__":
    # Render provides the public port through the PORT environment variable.
    # Do not open a local browser in a hosted, headless environment.
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        inbrowser=False,
    )
