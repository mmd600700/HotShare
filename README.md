# 🔥 HotShare

**Easily share and transfer files bidirectionally between your computer and any device (Android, iOS, laptop, etc.) over a hotspot or local network.**

---

## ✨ Features

- 🔄 **Two-Way Transfer:** Upload and download files seamlessly from both the desktop application and the web interface.
- 📊 **Progress Tracking:** Real-time progress bars for monitoring both upload and download transfers.
- 🌐 **Dynamic IP Detection:** The application automatically detects and displays your correct local network IP address (no hardcoded IPs).
- 📤 **Share Files from PC:** Host a simple web server to share files from your computer.
- 🔗 **QR Code Support:** Quickly scan a QR code to open the sharing address.
- 🔒 **Private & Offline:** Direct sharing over a hotspot or local network. No internet required.
- 📁 **Any File Type:** Share documents, images, videos, and more.
- 💻 **Ready-to-Use Binaries:** Download the executable file for your operating system.

## 🚀 Quick Start

### Prerequisites

- A computer (Windows, macOS, or Linux).
- A device with a web browser to send or receive files.
- A **hotspot** or **local network** connecting both devices (e.g., turn on your phone's hotspot and connect your computer to it, or connect both to the same Wi-Fi).

### Installation & Usage

1. **Download the Binary:**
   - Go to the [Releases](https://github.com/mmd600700/HotShare/releases) page.
   - Download the appropriate file for your operating system:
     - `HotShare-Windows.exe` for Windows
     - `HotShare-macOS` for macOS
     - `HotShare-Linux` for Linux

2. **Run the Application:**
   - **Windows:** Double-click the `.exe` file.
   - **macOS/Linux:** Open a terminal, navigate to the downloaded file, and run:
     ```bash
     chmod +x HotShare-macOS  # Make it executable (macOS/Linux)
     ./HotShare-macOS         # Run the file
     ```

3. **Share & Transfer Files:**
   - **On your computer:** Place the files you want to share in the same folder as the executable. The application will automatically detect your local network IP and start the server.
   - **On the other device (or vice versa):**
     1. Ensure both devices are connected to the **same hotspot or local network**.
     2. Open a web browser on the device.
     3. Enter the **exact dynamic address** shown in the application (e.g., `http://<Your-Local-IP>:8888`) or scan the displayed QR code. 
        > *Note: The IP address is dynamically detected based on your specific network configuration. Do not use generic examples like `192.168.43.1`; always use the address displayed by the app.*
     4. You can now **download** files shared from the computer, or **upload** files from your device directly to the computer. A real-time **progress bar** will display the transfer status on both the web page and the application.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.

---

**⭐️ If you find this project useful, please give it a star to help others discover it!**
