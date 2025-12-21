import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import os
import re
from summarizer import summarize_pdf_folder

class SummarizerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Summarizer")
        self.root.geometry("800x600")

        # Folder selection
        self.folder_label = tk.Label(root, text="Selected Folder: None")
        self.folder_label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Folder", command=self.select_folder)
        self.select_button.pack(pady=5)

        # Run button
        self.run_button = tk.Button(root, text="Run Summarization", command=self.run_summarization, state=tk.DISABLED)
        self.run_button.pack(pady=5)

        # Output area
        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=30)
        self.output_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.output_text.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.output_text.tag_configure("header", font=("TkDefaultFont", 14, "bold"))

        self.folder_path = None
        self.summaries = []

    def insert_markdown(self, text):
        lines = text.split('\n')
        for line in lines:
            if line.startswith('## '):
                self.output_text.insert(tk.END, line[3:] + '\n', "header")
            else:
                # Parse bold
                parts = re.split(r'(\*\*.*?\*\*)', line)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        self.output_text.insert(tk.END, part[2:-2], "bold")
                    else:
                        self.output_text.insert(tk.END, part)
                self.output_text.insert(tk.END, '\n')

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.folder_label.config(text=f"Selected Folder: {folder}")
            self.run_button.config(state=tk.NORMAL)

    def run_summarization(self):
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        # Disable buttons during processing
        self.select_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.DISABLED)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing...\n")
        self.summaries = []

        # Run in thread to avoid freezing UI
        threading.Thread(target=self.process_summaries).start()

    def process_summaries(self):
        try:
            def update_ui(filename, summary):
                self.root.after(0, self.append_summary, filename, summary)
            
            summarize_pdf_folder(self.folder_path, callback=update_ui)
            self.root.after(0, self.finish_processing)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def append_summary(self, filename, summary):
        self.output_text.insert(tk.END, f"Summary for {filename}\n\n", "header")
        self.insert_markdown(summary)
        self.output_text.insert(tk.END, "\n---\n\n")

    def finish_processing(self):
        self.output_text.insert(tk.END, "All summaries completed.\n")
        # Re-enable buttons
        self.select_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)

    def show_error(self, error_msg):
        messagebox.showerror("Error", f"An error occurred: {error_msg}")
        self.select_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SummarizerUI(root)
    root.mainloop()