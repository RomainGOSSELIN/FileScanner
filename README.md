# 🗂️ FileScanner v1.0

FileScanner is an intuitive desktop application to detect and manage duplicate files in your folders. Simplify your file organization in just a few clicks!

## ✨ Key Features

- **🔍 Duplicate Detection:** Quickly scan to identify duplicate files.
- **🗑️ Easy Deletion:** Easily delete selected duplicates.
- **📁 File Relocation:** Move duplicates to a dedicated folder for better organization.
- **🎨 Modern Interface:** A clean and user-friendly interface.

## 🚀 Installation

1. Clone the GitHub repository:
```
git clone https://github.com/<your-username>/FileScanner.git
cd FileScanner
``` 

2. (Optional) Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

4. Run the application:
```
python FileScanner.py
```

## 🛠️ Creating an Executable

If you want to distribute FileScanner as an executable, use PyInstaller:

1. Install PyInstaller:
```
pip install pyinstaller
```

2. Create the executable with an icon:
```
pyinstaller --onefile --windowed --icon=FileScanner.ico --add-data "FileScanner.ico;." FileScanner.py
```
The executable will be available in the dist/ folder.

## 🖥️ Usage

1. **Add Folders:** Click **"Add Folder"** to select folders to scan.
2. **Start Scanning:** Click **"Start Scan"** to detect duplicates.
3. Manage Duplicates:
  - 🗑️ Delete files by clicking **"Delete Selected"**.
  - 📁 Move files by clicking **"Move Selected"**.
  

## 🤝 Contributions

Have an idea or found a bug? Contributions are welcome! Open an issue or submit a pull request to participate in the project.

## 📜 License

This project is licensed under MIT.

## 👤 Author

Created by [Romain Gosselin](https://www.linkedin.com/in/romaingosselin/).
