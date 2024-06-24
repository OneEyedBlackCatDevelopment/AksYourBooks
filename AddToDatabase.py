# pip install PyMuPDF marqo

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import fitz
import webbrowser
import marqo
import pdf_add_to_index

class AddToDatabaseUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Index your eBooks")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # First Row
        self.db_url_label = tk.Label(root, text="Database-URL:")
        self.db_url_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.db_url_entry = tk.Entry(root, width=50)
        self.db_url_entry.insert(0, "http://localhost:8882/")
        self.db_url_entry.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        self.db_name_label = tk.Label(root, text="Database Index name:")
        self.db_name_label.grid(row=0, column=2, sticky='w', padx=10, pady=5)
        self.db_name_entry = tk.Entry(root, width=20)
        self.db_name_entry.insert(0, "eBooks")
        self.db_name_entry.grid(row=0, column=3, sticky='ew', padx=10, pady=5)

        # Delete DB Index Button
        self.delete_index_button = tk.Button(root, text="Delete DB Index", command=self.delete_index)
        self.delete_index_button.grid(row=0, column=4, sticky='w', padx=10, pady=5)

        # Second Row
        self.path_label = tk.Label(root, text="Select a folder with PDF files:")
        self.path_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=1, column=2, sticky='w', padx=10, pady=5)
        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_check = tk.Checkbutton(root, text="Recursive search", variable=self.recursive_var, command=self.on_recursive_check_change)
        self.recursive_check.grid(row=1, column=3, sticky='w', padx=10, pady=5)

        # Treeview
        self.tree = ttk.Treeview(root, columns=('filename', 'author', 'title', 'keywords', 'path'), show='headings')
        self.tree.heading('filename', text='Filename')
        self.tree.heading('author', text='Author')
        self.tree.heading('title', text='Title')
        self.tree.heading('keywords', text='Keywords')
        self.tree.heading('path', text='Path')
        self.tree.grid(row=2, column=0, columnspan=5, sticky='nsew', padx=10, pady=5)
        self.root.rowconfigure(2, weight=1)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)

        # Select All Button
        self.select_all_button = tk.Button(root, text="Select All", command=self.select_all_files)
        self.select_all_button.grid(row=3, column=0, columnspan=5, padx=10, pady=5)

        # Add to Database Button
        self.add_button = tk.Button(root, text="Add to database", command=self.add_to_database)
        self.add_button.grid(row=4, column=0, columnspan=5, padx=10, pady=5)

        # Status Label
        self.status_label = tk.Label(root, text="", anchor='w')
        self.status_label.grid(row=5, column=0, columnspan=5, sticky='ew', padx=10, pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            self.list_pdf_files(directory)

    def list_pdf_files(self, path):
        self.tree.delete(*self.tree.get_children())
        script_dir = os.path.abspath(os.path.dirname(__file__))

        if self.recursive_var.get():
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".pdf"):
                        self.load_metadata(file, root, script_dir)
        else:
            for file in os.listdir(path):
                if file.endswith(".pdf"):
                    self.load_metadata(file, path, script_dir)

    def load_metadata(self, file, path, script_dir):
        full_path = os.path.join(path, file)

        # Get the relative path from the script_dir
        relative_path = os.path.relpath(full_path, script_dir)

        # If the relative path starts with "..", it means it's outside the script_dir
        if relative_path.startswith(".."):
            display_path = full_path
        else:
            display_path = relative_path

        doc = fitz.open(full_path)
        metadata = doc.metadata
        title = metadata.get("title", "")
        author = metadata.get("author", "")
        keywords = metadata.get("keywords", "")
    
        self.tree.insert('', 'end', values=(file, author, title, keywords, display_path))

    def on_tree_select(self, event):
        pass  # No action needed for now

    def on_tree_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            full_path = item['values'][4]
            webbrowser.open(full_path)

    def on_recursive_check_change(self):
        current_path = self.path_entry.get()
        if current_path:
            self.list_pdf_files(current_path)

    def select_all_files(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def add_single_entry_to_index(self, entry):
        self.mq.index(self.index_name).add_documents([entry], tensor_fields=["Details"])

    def add_to_database(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No files selected")
            return

        self.root.config(cursor="wait")
        self.root.update()
        self.add_button.config(state=tk.DISABLED)

        # Get the database URL and index name from the UI inputs
        self.db_url = self.db_url_entry.get()
        self.index_name = self.db_name_entry.get()
        self.index_settings = {
            "model": "flax-sentence-embeddings/all_datasets_v4_MiniLM-L6",
            "normalizeEmbeddings": True,
            "textPreprocessing": {
                "splitLength": 4,
                "splitOverlap": 1,
                "splitMethod": "sentence"
            },
        }


        self.mq = marqo.Client(self.db_url)

        # Create index if not exist
        try:
            self.mq.create_index(self.index_name, settings_dict=self.index_settings)
        except Exception as e:
            print(f"Index creation skipped: {e}")

        try:
            for item in selected_items:
                file_path = self.tree.item(item)['values'][4]
                file_name = self.tree.item(item)['values'][0]
                self.status_label.config(text=f"Processing {file_name}...")
                self.root.update()

                pdf_add_to_index.read_pdf(self.add_single_entry_to_index, file_path, source_type="book")

            messagebox.showinfo("Success", "All selected files have been added to the database.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.root.config(cursor="")
            self.add_button.config(state=tk.NORMAL)
            self.status_label.config(text="")

    def delete_index(self):
        db_url = self.db_url_entry.get()
        index_name = self.db_name_entry.get()

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{index_name}' from '{db_url}'?"):
            mq = marqo.Client(db_url)
            try:
                mq.index(index_name).delete()
                messagebox.showinfo("Success", f"Index '{index_name}' has been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AddToDatabaseUI(root)
    root.mainloop()
