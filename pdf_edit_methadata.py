######################################################################
# This allows to edit PDF metadata (author, title, keywords) 
# for all PDFs in a given path with a very simple UI
#
# usage: python pdf_edit_methadata.py
#
######################################################################


# pip install PyMuPDF


import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import fitz
import shutil
import webbrowser

class PDFMetadataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Metadata Editor")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.path_label = tk.Label(root, width=20, text="Select a folder with PDF files:")
        self.path_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)

        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        self.root.columnconfigure(1, weight=1)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=0, column=2, sticky='w', padx=10, pady=5)

        self.tree = ttk.Treeview(root, columns=('filename', 'author', 'title', 'keywords'), show='headings')
        self.tree.heading('filename', text='Filename')
        self.tree.heading('author', text='Author')
        self.tree.heading('title', text='Title')
        self.tree.heading('keywords', text='Keywords')
        self.tree.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=5)
        self.root.rowconfigure(1, weight=1)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)

        self.metadata_frame = tk.Frame(root)
        self.metadata_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=10, pady=5)

        self.metadata_frame.columnconfigure(1, weight=1)


        self.author_label = tk.Label(self.metadata_frame, text="Author:")
        self.author_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.author_entry = tk.Entry(self.metadata_frame, width=50)
        self.author_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        self.title_label = tk.Label(self.metadata_frame, text="Title:")
        self.title_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.title_entry = tk.Entry(self.metadata_frame, width=50)
        self.title_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        self.keywords_label = tk.Label(self.metadata_frame, text="Keywords:")
        self.keywords_label.grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.keywords_entry = tk.Entry(self.metadata_frame, width=50)
        self.keywords_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        self.save_button = tk.Button(root, text="Save Metadata", command=self.save_metadata)
        self.save_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            self.list_pdf_files(directory)

    def list_pdf_files(self, path):
        self.tree.delete(*self.tree.get_children())
        for file in os.listdir(path):
            if file.endswith(".pdf"):
                self.load_metadata(file, path)

    def load_metadata(self, file, path):
        full_path = os.path.join(path, file)
        doc = fitz.open(full_path)
        metadata = doc.metadata
        title = metadata.get("title", "")
        author = metadata.get("author", "")
        keywords = metadata.get("keywords", "")
        self.tree.insert('', 'end', values=(file, author, title, keywords))

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            filename, author, title, keywords = item['values']
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, title)
            self.author_entry.delete(0, tk.END)
            self.author_entry.insert(0, author)
            self.keywords_entry.delete(0, tk.END)
            self.keywords_entry.insert(0, keywords)
            self.current_file = os.path.join(self.path_entry.get(), filename)

    def on_tree_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            filename = item['values'][0]
            full_path = os.path.join(self.path_entry.get(), filename)
            webbrowser.open(full_path)

    def save_metadata(self):
        if not hasattr(self, 'current_file'):
            messagebox.showerror("Error", "No file selected")
            return

        doc = fitz.open(self.current_file)
        metadata = doc.metadata
        metadata['title'] = self.title_entry.get()
        metadata['author'] = self.author_entry.get()
        metadata['keywords'] = self.keywords_entry.get()
        doc.set_metadata(metadata)

        temp_file = self.current_file + ".temp"
        doc.save(temp_file)
        doc.close()

        os.remove(self.current_file)
        shutil.move(temp_file, self.current_file)

        selected_item = self.tree.selection()[0]
        self.tree.item(selected_item, values=(
            os.path.basename(self.current_file),
            self.author_entry.get(),
            self.title_entry.get(),
            self.keywords_entry.get()
        ))

        messagebox.showinfo("Success", f"Metadata for {os.path.basename(self.current_file)} updated successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMetadataEditor(root)
    root.mainloop()
