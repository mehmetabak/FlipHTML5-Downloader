import nest_asyncio
nest_asyncio.apply() # Colab'daki asyncio loop hatasını çözer

import os
import sys
import json
import random
import re
import concurrent.futures
import base64
import urllib.parse
import zlib
import asyncio

# 1. Bağımlılık Kontrolü
try:
    import requests
    from PIL import Image
    from tqdm import tqdm
    from fpdf import FPDF
    from PyPDF2 import PdfMerger
    from playwright.async_api import async_playwright
except ImportError as e:
    missing_module = str(e).split("'")[1]
    print(f"[-] Hata/Error: Eksik Kütüphane / Missing Library: '{missing_module}'")
    print(f"[-] Lütfen yükleyin / Please install: pip install {missing_module}")
    sys.exit(1)

# İsteğe bağlı lzstring kütüphanesi
try:
    import lzstring
except ImportError:
    lzstring = None

# --- ŞİFRE ÇÖZÜCÜ FONKSİYON ---
def de_string(s):
    if not isinstance(s, str) or not s.startswith("v01"):
        return None
    buffer = s[3:]
    length = len(buffer)
    h = length >> 1 
    decoded_parts = []
    for i in range(h):
        decoded_parts.append(buffer[i])
        decoded_parts.append(buffer[h + i])
    if length % 2 == 1:
        decoded_parts.append(buffer[length - 1])
    return "".join(decoded_parts)

# --- Sabitler ve Ayarlar ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
]
MAX_THREADS = 15
BOOK_BASE_URLS = [
    "https://fliphtml5.com",
    "https://online.fliphtml5.com"
]

# --- Dil Metinleri ---
LANGUAGES = {
    "en": {
        "header": "--- FlipHTML5 Downloader - v11 (Hybrid & Multi-Path Edition) ---",
        "instructions_title": "\nIMPORTANT: Use the ID from the book's direct URL, not from a 'bookcase' link.",
        "instructions_line1": "Example: For 'https://fliphtml5.com/wrbmv/shsy/', the ID is 'wrbmv/shsy'",
        "instructions_line2": "Example: For 'https://fliphtml5.com/xovyu/bzlq/' or 'https://online.fliphtml5.com/xovyu/bzlq/', the ID is 'xovyu/bzlq'\n",
        "prompt_book_id": "[*] Enter the Book ID (e.g., xovyu/bzlq): ",
        "warn_id_format": "\n[!] WARNING: The Book ID format seems incorrect. It should be 'xxxx/yyyy'.\n",
        "fetching_config": "[*] Phase 1: Fetching book configuration...",
        "pw_fallback": "[!] Advanced protection (Wasm) detected. Phase 2: Starting Headless Browser bypass...",
        "pw_searching_memory": "[*] JS Hook returned empty, aggressive memory HTML scanning initiated...",
        "found_pages": "[+] Success! Found {total_pages} pages in the book.",
        "prompt_start_page": "[*] Enter the start page (Press Enter for 1): ",
        "prompt_end_page": "[*] Enter the end page (Press Enter for {total_pages}): ",
        "prompt_folder_name": "[*] Enter folder name (Press Enter for '{default_folder}'): ",
        "prompt_pdf_name": "[*] Enter PDF filename (Press Enter for '{folder_name}.pdf'): ",
        "prompt_skip_existing": "[*] Skip existing files? (y/n, default n): ",
        "skip_yes": "y",
        "processing_pages": "\n[*] A total of {count} pages ({start}-{end}) will be processed.",
        "progress_downloading": "Downloading Pages",
        "progress_downloaded": "Downloaded",
        "progress_skipped": "Skipped",
        "progress_failed": "Failed",
        "download_complete": "\n[+] Download process finished. Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}.",
        "first_fail_url": "[-] The first failed attempt was for URL: {url}",
        "converting_to_pdf": "\n[*] Converting images to PDF...",
        "creating_pdf_pages": "Creating PDF Pages",
        "merging_pdf_pages": "[*] Merging temporary PDF pages...",
        "pdf_success": "\n[+] PDF created successfully: {pdf_name}",
        "pdf_skipped_all_failed": "[-] PDF creation skipped because all downloads failed.",
        "pdf_skipped_no_new": "[*] PDF creation skipped as no new files were downloaded.",
        "all_complete": "\n--- All operations complete ---",
        "error_fetching_config": "[-] CRITICAL: Failed to fetch or parse configuration file.",
        "error_no_pages_in_config": "[-] No pages found. The book might be private, ID wrong, or structure changed.",
        "error_could_not_parse": "[-] Could not parse page data from configuration.",
        "error_invalid_range": "[-] Invalid page range! Please specify a range between 1 and {total_pages}.",
        "error_image_processing": "[-] Error: Could not process '{filename}': {error}",
        "error_no_images_to_process": "[-] No images found to process for PDF creation."
    },
    "tr": {
        "header": "--- FlipHTML5 İndirici - v11 (Hibrit & Çoklu-Yol Sürümü) ---",
        "instructions_title": "\nÖNEMLİ: 'bookcase' linki yerine doğrudan kitabın URL'sindeki ID'yi kullanın.",
        "instructions_line1": "Örnek: 'https://fliphtml5.com/wrbmv/shsy/' için ID: 'wrbmv/shsy'",
        "instructions_line2": "Örnek: 'https://fliphtml5.com/xovyu/bzlq/' veya 'https://online.fliphtml5.com/xovyu/bzlq/' için ID: 'xovyu/bzlq'\n",
        "prompt_book_id": "[*] Kitap ID'sini girin (ör: xovyu/bzlq): ",
        "warn_id_format": "\n[!] UYARI: Kitap ID formatı yanlış görünüyor. 'xxxx/yyyy' formatında olmalıdır.\n",
        "fetching_config": "[*] Aşama 1: Kitap yapılandırması çekiliyor...",
        "pw_fallback": "[!] Gelişmiş koruma (Wasm) tespit edildi. Aşama 2: Sanal Tarayıcı ile atlatılıyor, lütfen bekleyin...",
        "pw_searching_memory": "[*] JS Kancası boş döndü, bellek ve HTML agresif taranıyor...",
        "found_pages": "[+] Başarılı! Kitapta {total_pages} sayfa bulundu.",
        "prompt_start_page": "[*] Başlangıç sayfasını girin (boş bırakırsanız: 1): ",
        "prompt_end_page": "[*] Bitiş sayfasını girin (boş bırakırsanız: {total_pages}): ",
        "prompt_folder_name": "[*] Klasör adını girin (boş bırakırsanız: '{default_folder}'): ",
        "prompt_pdf_name": "[*] PDF dosya adını girin (boş bırakırsanız: '{folder_name}.pdf'): ",
        "prompt_skip_existing": "[*] Mevcut dosyalar atılsın mı? (e/h, varsayılan h): ",
        "skip_yes": "e",
        "processing_pages": "\n[*] Toplam {count} sayfa ({start}-{end}) işlenecek.",
        "progress_downloading": "Sayfalar İndiriliyor",
        "progress_downloaded": "İndi",
        "progress_skipped": "Atlandı",
        "progress_failed": "Hata",
        "download_complete": "\n[+] İndirme işlemi tamamlandı. İndi: {downloaded}, Atlandı: {skipped}, Hata: {failed}.",
        "first_fail_url": "[-] İlk başarısız deneme şu URL içindi: {url}",
        "converting_to_pdf": "\n[*] Resimler PDF'e dönüştürülüyor...",
        "creating_pdf_pages": "PDF Sayfaları Oluşturuluyor",
        "merging_pdf_pages": "[*] Geçici PDF sayfaları birleştiriliyor...",
        "pdf_success": "\n[+] PDF başarıyla oluşturuldu: {pdf_name}",
        "pdf_skipped_all_failed": "[-] Tüm indirmeler başarısız olduğu için PDF oluşturma işlemi atlandı.",
        "pdf_skipped_no_new": "[*] Yeni dosya indirilmediği için PDF oluşturma işlemi atlandı.",
        "all_complete": "\n--- Tüm işlemler tamamlandı ---",
        "error_fetching_config": "[-] KRİTİK: Yapılandırma dosyası çekilemedi veya işlenemedi.",
        "error_no_pages_in_config": "[-] Sayfa bulunamadı. Kitap gizli, ID hatalı veya site yapısı değişmiş olabilir.",
        "error_could_not_parse": "[-] Yapılandırmadan sayfa verileri okunamadı.",
        "error_invalid_range": "[-] Geçersiz sayfa aralığı! Lütfen 1 ile {total_pages} arasında bir aralık belirtin.",
        "error_image_processing": "[-] Hata: '{filename}' işlenemedi: {error}",
        "error_no_images_to_process": "[-] PDF oluşturmak için işlenecek resim bulunamadı."
    }
}

# --- YÖNTEM 1: KLASİK İNDİRME MANTIĞI ---
def fetch_config(session, book_id):
    for base_url in BOOK_BASE_URLS:
        config_url = f"{base_url}/{book_id}/javascript/config.js"
        try:
            response = session.get(config_url, timeout=20)
            response.raise_for_status()
            json_match = re.search(r'var\s+htmlConfig\s*=\s*({.*?});', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1)), response.text
        except Exception:
            continue
    return None, ""

# --- YÖNTEM 2: ASYNC PLAYWRIGHT (WASM BYPASS) ---
async def extract_via_playwright(book_id, STRINGS):
    print(STRINGS["pw_fallback"])
    pages = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()

        await page.add_init_script("""
            window.flipPagesData = [];
            const originalParse = JSON.parse;
            JSON.parse = function(text, reviver) {
                const result = originalParse(text, reviver);
                try {
                    if (Array.isArray(result) && result.length > 0) {
                        const first = result[0];
                        if (first && (first.n !== undefined || first.name !== undefined || typeof first === 'string')) {
                            const str = JSON.stringify(first);
                            if (str.includes('.jpg') || str.includes('.webp') || str.includes('.png')) {
                                window.flipPagesData = result;
                            }
                        }
                    } else if (result && result.list && Array.isArray(result.list)) {
                        const first = result.list[0];
                        if (first && (first.n !== undefined || first.name !== undefined)) {
                            window.flipPagesData = result.list;
                        }
                    }
                } catch(e) {}
                return result;
            };
        """)

        for base_url in BOOK_BASE_URLS:
            url = f"{base_url}/{book_id}/"
            try:
                await page.goto(url, timeout=45000, wait_until="networkidle")
                break
            except Exception:
                continue
            
        await page.wait_for_timeout(3000)

        intercepted = await page.evaluate("window.flipPagesData")

        if intercepted and len(intercepted) > 0:
            for item in intercepted:
                n_val = item.get('n', item.get('name')) if isinstance(item, dict) else item
                if isinstance(n_val, list) and len(n_val) > 0:
                    pages.append(os.path.splitext(os.path.basename(n_val[0]))[0])
                elif isinstance(n_val, str):
                    pages.append(os.path.splitext(os.path.basename(n_val))[0])
        else:
            print(STRINGS["pw_searching_memory"])
            hashes = await page.evaluate("""() => {
                let h = new Set();
                let regex = /([a-fA-F0-9]{32})\\.(webp|jpg|png)/g;
                let match = document.documentElement.innerHTML.match(regex);
                if(match) match.forEach(m => h.add(m.split('.')[0]));
                return Array.from(h);
            }""")
            if hashes:
                pages = hashes

        await browser.close()
    
    seen = set()
    return [x for x in pages if not (x in seen or seen.add(x))]

def run_playwright_sync(book_id, STRINGS):
    return asyncio.run(extract_via_playwright(book_id, STRINGS))

# --- DOSYA İNDİRME VE PDF ---
def download_image(args):
    session, page_id, book_id, folder_name, skip_existing = args
    image_path_jpg = os.path.join(folder_name, f"{page_id}.jpg")

    if skip_existing and os.path.exists(image_path_jpg):
        return "skipped", None

    # Hem yeni hem eski alan adında; 'large' ve 'thumb' klasörlerini, tüm uzantılarla deniyoruz
    for base_url in BOOK_BASE_URLS:
        headers = {'Referer': f"{base_url}/{book_id}/"}
        for folder in ['large', 'thumb']:
            for ext in ['webp', 'jpg', 'png']:
                url = f"{base_url}/{book_id}/files/{folder}/{page_id}.{ext}"
                try:
                    with session.get(url, headers=headers, timeout=20, stream=True) as response:
                        content_type = response.headers.get("Content-Type", "").lower()
                        if response.status_code == 200 and "text/html" not in content_type:
                            with Image.open(response.raw) as img:
                                img.convert("RGB").save(image_path_jpg, "JPEG")
                            return "downloaded", None
                except Exception:
                    continue
                
    # Hiçbirinden dönmediyse hata (Raporlamak için varsayılan bir URL yolluyoruz)
    failed_url = f"{BOOK_BASE_URLS[0]}/{book_id}/files/large/{page_id}.webp"
    return "failed", failed_url

def convert_images_to_pdf(folder_name, pdf_name, page_order, STRINGS):
    print(STRINGS["converting_to_pdf"])
    temp_pdf_files, merger = [], PdfMerger()
    for i, page_id in enumerate(tqdm(page_order, desc=STRINGS["creating_pdf_pages"])):
        image_path = os.path.join(folder_name, f"{page_id}.jpg")
        if not os.path.exists(image_path): continue
        try:
            with Image.open(image_path) as img:
                w, h = img.size
                dpi = img.info.get('dpi', (72, 72))
                pdf = FPDF(unit="pt", format=(w * 72 / dpi[0], h * 72 / dpi[1]))
                pdf.add_page()
                pdf.image(image_path, 0, 0, w * 72 / dpi[0], h * 72 / dpi[1])
                temp_pdf_path = os.path.join(folder_name, f"~temp_{i}.pdf")
                pdf.output(temp_pdf_path)
                temp_pdf_files.append(temp_pdf_path)
        except Exception as e:
            print(STRINGS["error_image_processing"].format(filename=os.path.basename(image_path), error=e), file=sys.stderr)
            
    if not temp_pdf_files:
        print(STRINGS["error_no_images_to_process"], file=sys.stderr)
        return
        
    print(STRINGS["merging_pdf_pages"])
    for pdf_file in temp_pdf_files: merger.append(pdf_file)
    merger.write(pdf_name)
    merger.close()
    
    for pdf_file in temp_pdf_files:
        try: os.remove(pdf_file)
        except OSError: pass
    print(STRINGS["pdf_success"].format(pdf_name=pdf_name))

def main():
    lang_choice = ""
    while lang_choice not in ['en', 'tr']:
        lang_choice = input("Select language / Dil seçin (en/tr): ").lower().strip()
    STRINGS = LANGUAGES[lang_choice]

    print(STRINGS["header"])
    print(STRINGS["instructions_title"])
    print(STRINGS["instructions_line1"])
    print(STRINGS["instructions_line2"])

    book_id = input(STRINGS["prompt_book_id"]).strip()
    if '/' not in book_id or len(book_id.split('/')) != 2: print(STRINGS["warn_id_format"])

    all_pages = []
    
    # AŞAMA 1: Klasik ve Hızlı Çekim Denemesi
    with requests.Session() as session:
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        print(STRINGS["fetching_config"])
        config, raw_text = fetch_config(session, book_id)
        
        if config:
            try:
                flip_data = config.get('fliphtml5_pages', [])
                decoded_text = ""

                if isinstance(flip_data, list) and len(flip_data) > 0:
                    for page in flip_data:
                        n_val = page.get('n', page.get('name'))
                        if isinstance(n_val, list) and len(n_val) > 0:
                            all_pages.append(os.path.splitext(os.path.basename(n_val[0]))[0])
                        elif isinstance(n_val, str):
                            all_pages.append(os.path.splitext(os.path.basename(n_val))[0])
                
                elif isinstance(flip_data, str) and flip_data.startswith("v01"):
                    decoded_str = de_string(flip_data)
                    
                    if lzstring:
                        try:
                            lz = lzstring.LZString()
                            temp_lz = lz.decompressFromBase64(decoded_str)
                            if temp_lz and ("{" in temp_lz or "[" in temp_lz):
                                decoded_text = temp_lz
                        except Exception:
                            pass
                    
                    if not decoded_text:
                        try:
                            b64_str = decoded_str + "=" * ((4 - len(decoded_str) % 4) % 4)
                            raw_bytes = base64.b64decode(b64_str)
                            try:
                                raw_bytes = zlib.decompress(raw_bytes, zlib.MAX_WBITS|32)
                            except Exception:
                                try: raw_bytes = zlib.decompress(raw_bytes)
                                except Exception: pass
                            decoded_text = raw_bytes.decode('utf-8', errors='ignore')
                            decoded_text = urllib.parse.unquote(decoded_text)
                        except Exception:
                            decoded_text = decoded_str
                    
                    if decoded_text:
                        try:
                            decoded_list = json.loads(decoded_text)
                            iterable = decoded_list if isinstance(decoded_list, list) else decoded_list.get('list', decoded_list.get('pages', []))
                            for page in iterable:
                                n_val = page.get('n', page.get('name'))
                                if isinstance(n_val, list) and len(n_val) > 0:
                                    all_pages.append(os.path.splitext(os.path.basename(n_val[0]))[0])
                                elif isinstance(n_val, str):
                                    all_pages.append(os.path.splitext(os.path.basename(n_val))[0])
                        except Exception:
                            hashes = re.findall(r'([a-fA-F0-9]{32})', decoded_text)
                            seen = set()
                            for h in hashes:
                                if h not in seen:
                                    seen.add(h)
                                    all_pages.append(h)
            except Exception:
                pass

    # AŞAMA 2: Aşama 1 Başarısız Olduysa (WASM) Playwright'ı Devreye Sok
    if not all_pages:
        all_pages = run_playwright_sync(book_id, STRINGS)

    # Son Kontrol
    if not all_pages:
        print(STRINGS["error_no_pages_in_config"], file=sys.stderr)
        return
        
    total_pages = len(all_pages)
    print(STRINGS["found_pages"].format(total_pages=total_pages))

    start_page_str = input(STRINGS["prompt_start_page"])
    end_page_str = input(STRINGS["prompt_end_page"].format(total_pages=total_pages))

    start_page = int(start_page_str) if start_page_str.isdigit() else 1
    end_page = int(end_page_str) if end_page_str.isdigit() else total_pages

    default_folder = book_id.replace('/', '-')
    folder_name = input(STRINGS["prompt_folder_name"].format(default_folder=default_folder)) or default_folder
    pdf_name = input(STRINGS["prompt_pdf_name"].format(folder_name=folder_name)) or f"{folder_name}.pdf"
    skip_existing = input(STRINGS["prompt_skip_existing"]).lower().startswith(STRINGS["skip_yes"])

    os.makedirs(folder_name, exist_ok=True)

    if not (1 <= start_page <= total_pages and start_page <= end_page <= total_pages):
        print(STRINGS["error_invalid_range"].format(total_pages=total_pages), file=sys.stderr)
        return

    pages_to_download = all_pages[start_page - 1:end_page]
    print(STRINGS["processing_pages"].format(count=len(pages_to_download), start=start_page, end=end_page))

    with requests.Session() as session:
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        tasks = [(session, page, book_id, folder_name, skip_existing) for page in pages_to_download]
        d, s, f, first_err_url = 0, 0, 0, None

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_page = {executor.submit(download_image, task): task[1] for task in tasks}
            p_bar = tqdm(concurrent.futures.as_completed(future_to_page), total=len(tasks), desc=STRINGS["progress_downloading"])
            for future in p_bar:
                try:
                    res, url = future.result()
                    if res == "downloaded": d += 1
                    elif res == "skipped": s += 1
                    else:
                        f += 1
                        if first_err_url is None: first_err_url = url
                    p_bar.set_postfix_str(f"{STRINGS['progress_downloaded']}: {d}, {STRINGS['progress_skipped']}: {s}, {STRINGS['progress_failed']}: {f}")
                except Exception:
                    f += 1

    print(STRINGS["download_complete"].format(downloaded=d, skipped=s, failed=f))
    if first_err_url: print(STRINGS["first_fail_url"].format(url=first_err_url))

    if d > 0 or (s > 0 and not os.path.exists(pdf_name)):
        convert_images_to_pdf(folder_name, pdf_name, pages_to_download, STRINGS)
    elif f == len(tasks):
        print(STRINGS["pdf_skipped_all_failed"])
    else:
        print(STRINGS["pdf_skipped_no_new"])

    print(STRINGS["all_complete"])

if __name__ == "__main__":
    main()
