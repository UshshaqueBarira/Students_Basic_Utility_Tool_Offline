# 🛠️ Human Utility AI Hub

An all-in-one desktop utility suite built with **Gradio** and **Python**. Designed for students and everyday users, this tool provides image optimization, document tools, conversion utilities, and a secure offline password vault—all through a modern tabbed interface.

---

## ✨ Features

### 🖼️ Image Utilities
* **Image Compression & Resizer:** Reduce image file size (JPEG, PNG, WEBP) and resize dimensions without sacrificing quality.
* **Image Enhancer & Upscaler:** Sharpen blurry images and upscale resolution (2x, 4x).
* **Background Remover:** Isolate subjects and export transparent PNG cutouts.

### 📄 PDF & Productivity Tools
* **PDF Toolkit:** Merge multiple PDFs, extract text, convert pages into images, and remove PDF passwords.
* **Password Generator:** Generate strong, customizable passwords with configurable length, special characters, and numbers.
* **Unit Converter:** Perform instant conversions across **Length** (m, km, miles, feet), **Weight** (kg, lbs, oz), and **Temperature** (°C, °F, K).

### 🔒 Offline Local Password Saver
* **AES-256 Encryption:** Encrypts vault contents locally using `PBKDF2HMAC` key derivation and `Fernet` symmetric encryption.
* **First-Time Setup Flow:** Prompts for initial Master Password creation and verification.
* **100% Offline Storage:** Writes encrypted data to `vault.enc` directly on your disk—no remote servers or cloud exposure.

---

## 🛠️ Tech Stack

* **UI Framework:** [Gradio](https://www.gradio.app/)
* **Cryptography:** `cryptography` (`PBKDF2HMAC`, `Fernet`)
* **Image Processing:** `Pillow`
* **PDF Processing:** `pypdf`
* **Language:** Python 3.9+

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.9+ installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/human-utility-ai-hub.git](https://github.com/your-username/human-utility-ai-hub.git)
   cd human-utility-ai-hub