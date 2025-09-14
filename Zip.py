import zipfile
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import multiprocessing

lock = Lock()

def find_first_zip_in_cwd():
    cwd = os.getcwd()
    for file in os.listdir(cwd):
        if file.lower().endswith('.zip') and os.path.isfile(os.path.join(cwd, file)):
            return os.path.join(cwd, file)
    return None

def extract_single_file(zip_path, file_info, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extract(file_info, extract_to)
    return file_info.filename

def extract_zip_fast(zip_path, extract_to, max_workers=8):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        files = zip_ref.infolist()
        total_files = len(files)

    print(f"\n📦 Found {total_files} files in the archive.")
    print(f"⚡ Extracting with {max_workers} threads...\n")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_single_file, zip_path, file_info, extract_to): file_info for file_info in files}

        for i, future in enumerate(as_completed(futures), start=1):
            with lock:
                percent = (i / total_files) * 100
                sys.stdout.write(f"\r✅ Extracted: {i}/{total_files} files ({percent:.2f}%)")
                sys.stdout.flush()

    print(f"\n\n🎉 Extraction complete! Files extracted to: {extract_to}")

def main():
    print("==== Auto ZIP Extractor ====")
    zip_path = find_first_zip_in_cwd()

    if not zip_path:
        print("❌ No .zip file found in current folder.")
        return

    extract_to = os.path.dirname(zip_path)  # same folder

    print(f"📁 Found ZIP file: {os.path.basename(zip_path)}")
    print(f"📂 Extracting files to: {extract_to}")

    max_workers = multiprocessing.cpu_count() or 4

    try:
        extract_zip_fast(zip_path, extract_to, max_workers=max_workers)
    except zipfile.BadZipFile:
        print("❌ Error: The file is not a valid ZIP archive.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
