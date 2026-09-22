import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path
import json
from src.organizer import InvoiceOrganizer


class InvoiceOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Organizer - Property Taxation")
        self.root.geometry("600x500")
        
        self.organizer = InvoiceOrganizer()
        
        self.create_widgets()
        self.load_config()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Invoice Organizer", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        ttk.Label(main_frame, text="Accounts Team Member:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.person_var = tk.StringVar()
        self.person_combo = ttk.Combobox(main_frame, textvariable=self.person_var, values=self.organizer.accounts_team)
        self.person_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Contractor:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.contractor_var = tk.StringVar()
        self.contractor_combo = ttk.Combobox(main_frame, textvariable=self.contractor_var, values=list(self.organizer.contractors.keys()))
        self.contractor_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Purchased From:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.purchased_from_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.purchased_from_var).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Invoice Date:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.date_var).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Source File/Folder:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar()
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(source_frame, textvariable=self.source_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(source_frame, text="Browse", command=self.browse_source).pack(side=tk.LEFT, padx=5)
        
        self.move_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Move files (uncheck to copy)", variable=self.move_var).grid(
            row=6, column=0, columnspan=2, pady=10
        )
        
        ttk.Button(main_frame, text="Organize Invoice", command=self.organize, style="Accent.TButton").grid(
            row=7, column=0, columnspan=2, pady=20
        )
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(main_frame, text="Batch Processing", font=("Arial", 12, "bold")).grid(
            row=9, column=0, columnspan=2, pady=5
        )
        
        ttk.Button(main_frame, text="Create Folder Structure for All", command=self.create_structure).grid(
            row=10, column=0, columnspan=2, pady=5
        )
        
        self.log_text = tk.Text(main_frame, height=10, width=60)
        self.log_text.grid(row=11, column=0, columnspan=2, pady=10)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=11, column=2, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        main_frame.columnconfigure(1, weight=1)
    
    def load_config(self):
        pass
    
    def browse_source(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if not path:
            path = filedialog.askdirectory()
        if path:
            self.source_var.set(path)
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
    
    def organize(self):
        person = self.person_var.get()
        contractor = self.contractor_var.get()
        purchased_from = self.purchased_from_var.get()
        date_str = self.date_var.get()
        source = self.source_var.get()
        move = self.move_var.get()
        
        if not all([person, contractor, purchased_from, date_str, source]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            invoice_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        source_path = Path(source)
        if not source_path.exists():
            messagebox.showerror("Error", "Source path does not exist")
            return
        
        if source_path.is_file():
            try:
                result = self.organizer.organize_file(
                    source_path=str(source_path),
                    person=person,
                    contractor=contractor,
                    purchased_from=purchased_from,
                    invoice_date=invoice_date,
                    move=move
                )
                self.log(f"Organized: {result}")
                messagebox.showinfo("Success", f"File organized:\n{result}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            files = list(source_path.glob("*.jpg")) + list(source_path.glob("*.jpeg")) + list(source_path.glob("*.png"))
            self.log(f"Found {len(files)} files to process")
            
            for file_path in files:
                try:
                    result = self.organizer.organize_file(
                        source_path=str(file_path),
                        person=person,
                        contractor=contractor,
                        purchased_from=purchased_from,
                        invoice_date=invoice_date,
                        move=move
                    )
                    self.log(f"  Organized: {result}")
                except Exception as e:
                    self.log(f"  Failed: {file_path} - {e}")
            
            messagebox.showinfo("Complete", f"Processed {len(files)} files")
    
    def create_structure(self):
        for person in self.organizer.accounts_team:
            self.organizer.create_folder_structure(person)
            self.log(f"Created structure for {person}")
        messagebox.showinfo("Complete", "Folder structure created for all team members")


def main():
    root = tk.Tk()
    app = InvoiceOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()