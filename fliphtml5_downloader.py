


import requests
import json
import os
import random
import threading
from PIL import Image
from io import BytesIO
from tqdm import tqdm
import re
from PyPDF2 import PdfMerger
from fpdf import FPDF

# Introduction message
print("FlipHTML5 Downloader - Enhanced Version/arasTiR")

# User inputs
bookID = input("Enter Book ID (e.g., 'ousy/stby'): ")
start = input("Enter the start page number (leave empty for default: 1): ")
end = input("Enter the end page number (leave empty for default: last page): ")
folderName = input("Enter folder name for saving (leave empty to use Book ID): ") or bookID.replace("/", "-")
pdfName = input("Enter PDF filename (leave empty for default): ") or f"{folderName}.pdf"
skipExisting = input("Skip existing files? (y/n): ").lower() == 'y'


# Set default values if start or end are empty
start = int(start) if start else 1
end = int(end) if end else None  # 'None' will be set to the last page later

# Create directory if it doesn't exist
os.makedirs(folderName, exist_ok=True)

# User-agent list to randomize requests
useragents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.17017',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
]

# Fetch configuration from a remote URL
def fetch_config():
    config_url = f"https://online.fliphtml5.com/{bookID}/javascript/config.js"
    headers = {'User-Agent': random.choice(useragents)}
    try:
        r = requests.get(config_url, headers=headers, timeout=50)
        r.raise_for_status()
        # Extract JSON part from JavaScript content
        json_str = re.search(r'var htmlConfig = ({.*?});', r.text, re.DOTALL)
        if json_str:
            config_data = json.loads(json_str.group(1))  # Parse JSON
            return config_data
        else:
            print("[-] JSON format not found in config content.")
            return None
    except Exception as e:
        print(f"[-] Error fetching config: {str(e)}")
        return None

# Function to clean taskID
def clean_taskID(taskID):
    if taskID.startswith('./files/large/'):
        taskID = taskID[len('./files/large/'):]  # Remove './files/large/' prefix
    taskID = re.sub(r'\.webp$|\.jpg$', '', taskID)  # Remove '.webp' or '.jpg' extension if present
    return taskID

# Function to download a single image
def download_image(taskID):
    taskID = clean_taskID(taskID)  # Clean the taskID
    for ext in ['jpg', 'webp' ]:  # Try webp first, then jpg
        filepath = f"{folderName}/{taskID}.{ext}"
        URL = f"https://online.fliphtml5.com/{bookID}/files/large/{taskID}.{ext}"
        headers = {'User-Agent': random.choice(useragents)}

        try:
            r = requests.get(URL, headers=headers, timeout=10)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content))

                # Convert webp to jpg if needed
                if ext == 'webp':
                    jpg_filepath = f"{folderName}/{taskID}.jpg"
                    img.convert("RGB").save(jpg_filepath, "JPEG")
                    print(f"[+] Page {taskID} downloaded as {ext} and converted to .jpg")
                else:
                    img.save(filepath)
                    print(f"[+] Page {taskID} downloaded as {ext}")
                return
            else:
                print(f"[-] Page {taskID} failed to download ({ext}, HTTP {r.status_code})")
        except Exception as e:
            print(f"[-] Page {taskID} failed to download: {str(e)}")

# Download images in range with a progress bar and optional threading for optimization
def download_images_concurrently(start, end, max_threads=5):
    config = fetch_config()
    if not config:
        print("[-] Configuration fetch failed. Exiting.")
        return

    # Extract page IDs from the configuration
    pages = [page['n'][0] for page in config.get('fliphtml5_pages', [])]

    # Ensure pages are in the correct order and total count
    total_pages = len(pages)

    # Ensure the start and end are within the correct range
    if start < 1 or (end is not None and end > total_pages) or start > (end if end is not None else total_pages):
        print("[-] Invalid page range specified.")
        return

    # Set end to the last page if it was not specified
    end = end if end is not None else total_pages

    # Get the correct page IDs based on user input
    filtered_pages = pages[start-1:end]

    # Save page order to a file for accurate sorting later
    with open(f"{folderName}/page_order.txt", "w") as f:
        for page in filtered_pages:
            f.write(f"{page}\n")

    threads = []
    with tqdm(total=len(filtered_pages)) as pbar:
        def worker(taskID):
            filepath_webp = f"{folderName}/{taskID}.webp"
            filepath_jpg = f"{folderName}/{taskID}.jpg"

            if skipExisting and (os.path.exists(filepath_webp) or os.path.exists(filepath_jpg)):
                print(f"[ ] Page {taskID} already exists, skipping.")
            else:
                download_image(taskID)
            pbar.update(1)

        for taskID in filtered_pages:
            while len(threads) >= max_threads:
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)

            t = threading.Thread(target=worker, args=(taskID,))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

# Function to convert images to PDF
def images_to_pdf(folder, pdf_filename="output.pdf"):
    pdf_files = []
    image_list = []

    # Extract pages from folder and sort by their original order
    with open(f"{folder}/page_order.txt") as f:
        page_order = [line.strip() for line in f]

    for taskID in page_order:
        image_path = os.path.join(folder, f"{clean_taskID(taskID)}.jpg")
        if os.path.exists(image_path):
            image_list.append(image_path)

    # Generate PDF files in chunks
    chunk_size = 50
    num_chunks = (len(image_list) // chunk_size) + 1

    image_path = image_list[0]
    width_pt, height_pt = 595, 842 #Default A4 dimensions in case of error with the first image

    with Image.open(image_path) as img:
            # Get image dimensions in points (1 inch = 72 points)
            width, height = img.size
            width_pt, height_pt = width * 72 / img.info.get("dpi", (72, 72))[0], height * 72 / img.info.get("dpi", (72, 72))[1]


    
    for i in range(num_chunks):
        chunk_filename = f"{folder}/chunk_{i+1}.pdf"
        pdf_files.append(chunk_filename)

       
        pdf = FPDF(unit="pt", format=(width_pt, height_pt))  # Use points as the unit for precise sizing
        start_index = i * chunk_size
        end_index = min((i + 1) * chunk_size, len(image_list))

        for image_path in image_list[start_index:end_index]:
                
                # Add a new page with the image's dimensions
                pdf.add_page() #Fails with format argument, otherwise get dimensions here
                pdf.image(image_path, 0,0) # 0,0 To place in top corner, dimensions are auto
                

        pdf.output(chunk_filename)
        print(f"[+] PDF chunk created: {chunk_filename}")

    # Combine PDF chunks into a single file
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(pdf_file)

    merger.write(pdf_filename)
    merger.close()

    # Cleanup temporary PDF chunks
    for pdf_file in pdf_files:
        os.remove(pdf_file)

    print(f"[+] Final PDF created: {pdf_filename}")


# Start downloading images
download_images_concurrently(start, end)

# Create PDF from downloaded images
images_to_pdf(folderName, pdfName)
