
# FlipHTML5 Downloader

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mehmetabak/FlipHTML5-Downloader/blob/main/fliphtml5_downloader_colab.ipynb)

## Purpose

The **FlipHTML5 Downloader** is an advanced Python tool designed to download public pages from FlipHTML5 books and compile them into a single PDF file. It utilizes a **Hybrid Extraction Engine** to bypass modern protections (like WebAssembly/Wasm and LZString encryption) and efficiently handles large books with hundreds of pages.

## Features

- **Hybrid Extraction Engine**: Uses classic fast-fetching for standard books and automatically falls back to a Headless Browser (Playwright) bypass for heavily encrypted (Wasm) books.
- **Smart Path & Format Scanning**: Automatically searches through both `large` and `thumb` directories for multiple image formats (`.webp`, `.jpg`, `.png`).
- **Multi-Language Support**: Fully bilingual command-line interface supporting both English and Turkish.
- **Google Colab Ready**: Integrated `nest_asyncio` to work flawlessly inside Jupyter Notebooks and Google Colab environments.
- **Image Conversion**: Converts downloaded images into standard JPEG format for robust PDF creation.
- **Progress Tracking**: Provides real-time progress updates during image downloads.
- **Flexible Page Range**: Allows specifying a range of pages or defaulting to the entire book.

## Installation

To use this tool, you need to install the required Python libraries and the Playwright browser binaries. Open your terminal and run:

1. **Install Python Libraries:**
   ```sh
   pip install -r requirements.txt

```

2. **Install Playwright Browsers (Required for Wasm Bypass):**
```sh
playwright install chromium

```



## Usage

1. **Download the Script**: Clone this repository or download the script file.
2. **Run the Script**: Execute the script using Python. You will first be asked to select your language (English / Turkish). Then, you will be prompted to enter the following details:
* **Book ID**: The ID of the FlipHTML5 book (e.g., `ousy/stby`). Use the ID from the direct URL, not a bookcase link.
* **Start Page Number**: The page number where you want to start downloading (leave empty for default: 1).
* **End Page Number**: The page number where you want to stop downloading (leave empty for default: last page).
* **Folder Name**: The folder where images and PDFs will be saved (leave empty to use Book ID).
* **PDF Filename**: The name of the final PDF file (leave empty for default).
* **Skip Existing Files**: Whether to skip downloading images that already exist (y/n).


Example command:
```sh
python fliphtml5_downloader.py

```


3. **Final PDF**: Once the script finishes, the final PDF will be available in the specified folder.

## Open in Google Colab

You can easily run this tool without any local setup on [Google Colab](https://colab.research.google.com/github/mehmetabak/FlipHTML5-Downloader/blob/main/fliphtml5_downloader_colab.ipynb). The script is already optimized for Colab's asyncio event loops.

## Contributing

Contributions to this project are welcome! If you have any suggestions or improvements, please fork the repository and submit a pull request.

## 🚀 Upcoming Features & Enhancements

* **Performance Improvements**
* Enhanced multi-threading for even faster downloads.
* Memory-based chunk optimization for quicker PDF creation.
* Optional image compression for smaller PDF sizes.


* **Improved User Experience**
* Simplified CLI with presets for common settings.
* Detailed logging and progress bars for PDF generation.


* **Advanced Error Handling**
* Detection and exclusion of corrupt images during PDF creation.



## Acknowledgments

* [Playwright](https://playwright.dev/python/): For headless browser automation and Wasm decryption bypass.
* [Requests](https://docs.python-requests.org/en/latest/): For handling HTTP requests.
* [Pillow](https://pillow.readthedocs.io/en/stable/): For image processing.
* [TQDM](https://tqdm.github.io/): For progress bars.
* [PyPDF2](https://pythonhosted.org/PyPDF2/): For PDF manipulation.
* [lzstring](https://pypi.org/project/lzstring/): For handling LZString compressed configurations.

## License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

