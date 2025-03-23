File Organizer CLI 📂

A simple command-line tool to organize files in a directory by extensions. Ideal for Download folders and keeping your workspace clean!

🚀 Features

✔ Categorizes files into folders based on extensions
✔ Supports all file types automatically
✔ Prevents overwriting existing files
✔ Lightweight and fast


---

📥 Installation

1️⃣ Install via pip (Recommended)

pip install dirorganizer

2️⃣ Install from Source

git clone https://github.com/SudoRV/dirorganizer.git
cd dirorganizer
pip install --editable .


---

🔧 Usage

Basic Command:

arrange /path/to/folder

Example:

📂 Before:

Downloads/
├── report.pdf
├── music.mp3
├── photo.jpg

📂 After arrange Downloads/

Downloads/
├── pdf/   → report.pdf
├── mp3/   → music.mp3
├── jpg/   → photo.jpg


---

🛠 Development

To modify the tool, follow these steps:

git clone https://github.com/SudoRV/dirorganizer.git
cd dirorganizer
pip install --editable .

Test your changes using:

arrange /path/to/folder


---

📄 License

This project is licensed under the MIT License.


---

🤝 Contributing

Got ideas or improvements? Feel free to open an issue or submit a pull request! 🚀


---

📌 Notes

Requires Python 3.6+

To uninstall, run:

pip uninstall dirorganizer