# FlipHTML5 Downloader

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mehmetabak/FlipHTML5-Downloader/blob/main/fliphtml5_downloader_colab.ipynb)

## Purpose

The **FlipHTML5 Downloader** is a Python tool designed to download public pages from FlipHTML5 books and compile them into a single PDF file. It efficiently handles large books with hundreds of pages by downloading images, converting them if necessary, and creating a high-quality PDF document.

## Features

- **Download Pages**: Fetches pages from FlipHTML5 books in various formats.
- **Image Conversion**: Converts images from webp to jpg if needed.
- **Progress Tracking**: Provides progress updates during image downloads.
- **Chunked PDF Creation**: Breaks down large PDFs into smaller chunks to manage memory usage and combines them into a final PDF.
- **Flexible Page Range**: Allows specifying a range of pages or defaulting to the entire book.

## Open in Google Colab

You can also run this notebook on [Google Colab](https://colab.research.google.com/github/mehmetabak/FlipHTML5-Downloader/blob/main/fliphtml5_downloader_colab.ipynb).

## Installation

To use this tool, you need to install the required Python libraries. You can do this using `pip`. Open your terminal and run:

```sh
pip install requests pillow tqdm PyPDF2 fpdf
```

## Usage

1. **Download the Script**: Clone this repository or download the script file.

2. **Run the Script**: Execute the script using Python. You will be prompted to enter the following details:

    - **Book ID**: The ID of the FlipHTML5 book (e.g., `ousy/stby`).
    - **Start Page Number**: The page number where you want to start downloading (leave empty for default: 1).
    - **End Page Number**: The page number where you want to stop downloading (leave empty for default: last page).
    - **Folder Name**: The folder where images and PDFs will be saved (leave empty to use Book ID).
    - **PDF Filename**: The name of the final PDF file (leave empty for default).
    - **Skip Existing Files**: Whether to skip downloading images that already exist.

   Example command:

   ```sh
   python fliphtml5_downloader.py
   ```

   Follow the prompts to provide the necessary inputs.

3. **Final PDF**: Once the script finishes, the final PDF will be available in the specified folder.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions to this project are welcome! If you have any suggestions or improvements, please fork the repository and submit a pull request. 

## Potential Enhancements

- **User Authentication**: Add support for user authentication to access restricted books.
- **Error Handling**: Improve error handling and retry mechanisms for failed downloads.
- **GUI Interface**: Develop a graphical user interface (GUI) for ease of use.
- **Additional Formats**: Support additional image formats and conversion options.

## Acknowledgments

- [Requests](https://docs.python-requests.org/en/latest/): For handling HTTP requests.
- [Pillow](https://pillow.readthedocs.io/en/stable/): For image processing.
- [TQDM](https://tqdm.github.io/): For progress bars.
- [PyPDF2](https://pythonhosted.org/PyPDF2/): For PDF manipulation.
- [FPDF](http://www.fpdf.org/): For PDF creation.
