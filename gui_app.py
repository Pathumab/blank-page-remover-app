import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import fitz  # PyMuPDF
except ImportError:
    messagebox.showerror("Error", "PyMuPDF is not installed!")
    exit(1)

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    pass

try:
    import customtkinter as ctk
except ImportError:
    pass

# Make sure CustomTkinter looks modern
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# To combine CustomTkinter (CTk) with Drag and Drop (TkinterDnD2)
class TkinterDnDApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

def is_page_blank(page, threshold=0.99):
    pix = page.get_pixmap(colorspace=fitz.csGRAY, alpha=False)
    samples = pix.samples
    white_pixels = sum(samples.count(i) for i in range(250, 256))
    total_pixels = pix.width * pix.height
    if total_pixels == 0:
        return True
    return (white_pixels / total_pixels) >= threshold

class PDFRemoverApp(TkinterDnDApp):
    def __init__(self):
        super().__init__()
        self.title("✨ PDF Blank Page Remover ✨")
        self.geometry("650x650")
        
        # Configure grid layout for expanding
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        self.pdf_list = []  # Store absolute paths

        # ---------------- Title Frame ----------------
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        title_lbl = ctk.CTkLabel(title_frame, text="Blank Page Remover", font=ctk.CTkFont(size=24, weight="bold"))
        title_lbl.pack()
        subtitle_lbl = ctk.CTkLabel(title_frame, text="Drag & Drop PDFs to clean them up automatically!", font=ctk.CTkFont(size=14), text_color="gray")
        subtitle_lbl.pack()

        # ---------------- Settings Frame ----------------
        set_frame = ctk.CTkFrame(self)
        set_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Output Folder
        self.output_var = tk.StringVar(value=r"D:\EMPTY PAGE REMOVER\output")
        ctk.CTkLabel(set_frame, text="Output Folder:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.out_entry = ctk.CTkEntry(set_frame, textvariable=self.output_var)
        self.out_entry.grid(row=0, column=1, padx=10, pady=(15, 5), sticky="ew")
        set_frame.grid_columnconfigure(1, weight=1)
        
        btn_out = ctk.CTkButton(set_frame, text="Browse", fg_color="#F39C12", hover_color="#D68910", width=80, command=self.browse_output)
        btn_out.grid(row=0, column=2, padx=15, pady=(15, 5))
        
        # Threshold
        self.thresh_var = tk.StringVar(value="0.99")
        ctk.CTkLabel(set_frame, text="Blank Threshold:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=15, pady=(5, 15), sticky="w")
        self.thresh_entry = ctk.CTkEntry(set_frame, textvariable=self.thresh_var, width=80)
        self.thresh_entry.grid(row=1, column=1, padx=10, pady=(5, 15), sticky="w")

        # ---------------- Listbox Frame (Drag and Drop) ----------------
        dnd_frame = ctk.CTkFrame(self)
        dnd_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        
        top_dnd = ctk.CTkFrame(dnd_frame, fg_color="transparent")
        top_dnd.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(top_dnd, text="Drop Area", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(top_dnd, text="Clear List", fg_color="#E74C3C", hover_color="#C0392B", width=80, height=24, command=self.clear_list).pack(side="right")
        
        # We use a standard tk.Listbox styled to match CTk Dark Theme because CTk doesn't have a native ListBox
        self.listbox = tk.Listbox(dnd_frame, selectmode="extended", 
                                  bg="#2A2D2E", fg="#FFFFFF", highlightthickness=0, borderwidth=0,
                                  font=("Segoe UI", 11), selectbackground="#1E90FF")
        self.listbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.listbox.insert("end", "   ☁️ Drag and Drop your PDF files anywhere here... ☁️")
        
        # Enable Drag and drop
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.drop_files)
        
        # ---------------- Log and Process Area ----------------
        log_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.log = ctk.CTkTextbox(log_frame, height=100, state="disabled")
        self.log.pack(fill="both", expand=True)

        self.start_btn = ctk.CTkButton(self, text="▶ START PROCESSING", font=ctk.CTkFont(size=15, weight="bold"), 
                                       fg_color="#2ECC71", hover_color="#27AE60", height=45, command=self.start_thread)
        self.start_btn.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        
    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder: self.output_var.set(folder)
        
    def drop_files(self, event):
        if "☁️ Drag and Drop your PDF" in self.listbox.get(0):
            self.listbox.delete(0)
            
        files = self.tk.splitlist(event.data)
        for f in files:
            if f.lower().endswith('.pdf'):
                if f not in self.pdf_list:
                    self.pdf_list.append(f)
                    self.listbox.insert("end", f" 📄 {os.path.basename(f)}")
                    
    def clear_list(self):
        self.listbox.delete(0, "end")
        self.pdf_list.clear()
        self.listbox.insert("end", "   ☁️ Drag and Drop your PDF files anywhere here... ☁️")
        
    def log_msg(self, msg):
        self.log.configure(state='normal')
        self.log.insert('end', msg + "\n")
        self.log.see('end')
        self.log.configure(state='disabled')
        self.update_idletasks()

    def start_thread(self):
        if not self.pdf_list:
            messagebox.showwarning("No Files", "Please drag and drop some PDFs first!")
            return
            
        self.start_btn.configure(state="disabled", text="⏳ PROCESSING...")
        self.log.configure(state='normal')
        self.log.delete(1.0, 'end')
        self.log.configure(state='disabled')
        threading.Thread(target=self.process_pdfs, daemon=True).start()

    def process_pdfs(self):
        output_dir = self.output_var.get()
        try:
            threshold = float(self.thresh_var.get())
        except ValueError:
            threshold = 0.99
            
        os.makedirs(output_dir, exist_ok=True)
        self.log_msg("=== Starting Check ===")
        
        success_count = 0
        
        # Iterate over a copy of the list
        for source_path in list(self.pdf_list):
            filename = os.path.basename(source_path)
            output_path = os.path.join(output_dir, filename)
            self.log_msg(f"\nScanning: '{filename}'")
            
            try:
                doc = fitz.open(source_path)
                original_len = len(doc)
                keep_pages = []
                for num in range(original_len):
                    if not is_page_blank(doc[num], threshold):
                        keep_pages.append(num)
                
                if not keep_pages:
                    self.log_msg(" -> All pages blank! Processed correctly.")
                    doc.close()
                    # We no longer delete the original file per user request!
                    # os.remove(source_path)
                    
                    if source_path in self.pdf_list:
                        idx = self.pdf_list.index(source_path)
                        self.listbox.delete(idx)
                        self.pdf_list.pop(idx)
                    
                    success_count += 1
                    continue
                    
                doc.select(keep_pages)
                doc.save(output_path)
                doc.close()
                # We no longer delete the original file per user request!
                # os.remove(source_path)
                
                if source_path in self.pdf_list:
                    idx = self.pdf_list.index(source_path)
                    self.listbox.delete(idx)
                    self.pdf_list.pop(idx)
                
                removed = original_len - len(keep_pages)
                self.log_msg(f" -> Removed {removed} blanks. Original perfectly kept.")
                success_count += 1
            except Exception as e:
                self.log_msg(f" -> Error: {e}")
                
        self.log_msg(f"\n=== Processed {success_count} files successfully! ===")
        self.log_msg("Original files were left untouched in your source directory.")
        self.start_btn.configure(state="normal", text="▶ START PROCESSING")
        
        if not self.pdf_list:
            self.listbox.insert("end", "   ☁️ Drag and Drop your PDF files anywhere here... ☁️")

if __name__ == "__main__":
    try:
        app = PDFRemoverApp()
        app.mainloop()
    except Exception as e:
        print(f"\nError launching UI: {e}\nEnsure `customtkinter` and `tkinterdnd2` are installed.")
