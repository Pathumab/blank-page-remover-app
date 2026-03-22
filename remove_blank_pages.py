import os
try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF (fitz) is not installed. Please install it by running: pip install PyMuPDF")
    exit(1)

def is_page_blank(page, threshold=0.99):
    """
    Checks if a page is considered blank based on a white pixel threshold.
    Renders the page as a grayscale image and counts near-white pixels.
    """
    # Render the page to a grayscale pixmap
    # matrix=fitz.Matrix(0.5, 0.5) can be used to lower resolution for speed, 
    # but the default (72 DPI) is also very fast and accurate.
    pix = page.get_pixmap(colorspace=fitz.csGRAY, alpha=False)
    
    # In grayscale, pixel values range from 0 (black) to 255 (white).
    # We consider pixels >= 250 as "white" to account for minor invisible artifacts/noise.
    samples = pix.samples
    white_pixels = sum(samples.count(i) for i in range(250, 256))
    
    total_pixels = pix.width * pix.height
    
    if total_pixels == 0:
        return True # Edge case for extremely small/invalid pages
        
    white_ratio = white_pixels / total_pixels
    
    # If the ratio of white pixels is greater than or equal to the threshold, it is deemed blank
    return white_ratio >= threshold

def process_pdfs(source_dir="source", output_dir="output", threshold=0.99):
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        print(f"Source folder '{source_dir}' not found. Creating it ...")
        os.makedirs(source_dir)
        print("Please place your PDF files in the 'source' folder and run the script again.")
        return

    # Automatically create the output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{source_dir}'.")
        return

    for filename in pdf_files:
        source_path = os.path.join(source_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        print(f"Processing '{filename}'...")
        
        try:
            doc = fitz.open(source_path)
            original_length = len(doc)
            pages_to_keep = []
            
            # Check each page
            for page_num in range(original_length):
                page = doc[page_num]
                if not is_page_blank(page, threshold):
                    pages_to_keep.append(page_num)
            
            # If all pages are blank, we notify and skip saving
            if len(pages_to_keep) == 0:
                print(f"  -> Skipped '{filename}': All pages were detected as blank.")
                doc.close()
                continue
                
            # Use PyMuPDF's select function to keep only the specified pages in the document
            doc.select(pages_to_keep)
            
            # Save the modified document to the output folder
            # This ensures the original file in 'source' remains untouched
            doc.save(output_path)
            doc.close()
            
            removed_count = original_length - len(pages_to_keep)
            print(f"  -> Saved '{filename}'. Removed {removed_count} blank page(s), kept {len(pages_to_keep)} page(s).")
            
        except Exception as e:
            print(f"  -> Error processing '{filename}': {e}")

if __name__ == "__main__":
    SOURCE_FOLDER = "source"
    OUTPUT_FOLDER = "output"
    
    # 0.99 means 99% of the page pixels must be white or near-white to be considered blank.
    # Adjust this threshold if necessary depending on the artifacts in your PDFs.
    BLANK_THRESHOLD = 0.99 
    
    process_pdfs(SOURCE_FOLDER, OUTPUT_FOLDER, threshold=BLANK_THRESHOLD)
    print("Processing complete.")
