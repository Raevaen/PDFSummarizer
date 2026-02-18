import tkinter as tk
from tkinter import filedialog, scrolledtext
from rag import ChatLogic
import threading

class PDFGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Emanuele's PDF AI")
        self.logic = ChatLogic()

        # 1. Conversation Space
        self.chat_display = scrolledtext.ScrolledText(root, state='disabled', height=20, width=60)
        self.chat_display.pack(padx=10, pady=10)

        # 2. Input Field
        self.input_box = tk.Entry(root, width=50)
        self.input_box.pack(side=tk.LEFT, padx=10, pady=10)
        self.input_box.bind("<Return>", lambda e: self.send_query())

        # 3. Buttons
        tk.Button(root, text="Send", command=self.send_query).pack(side=tk.LEFT)
        tk.Button(root, text="Add PDF", command=self.upload_pdf).pack(side=tk.RIGHT, padx=10)

    def update_chat(self, sender, text):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {text}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            msg = self.logic.ingest_pdf(file_path)
            self.update_chat("System", msg)

    def send_query(self):
        user_text = self.input_box.get()
        if not user_text: return
        
        self.update_chat("You", user_text)
        self.input_box.delete(0, tk.END)
        
        # Run in thread so GUI doesn't freeze during Llama inference
        threading.Thread(target=self._process_ai, args=(user_text,)).start()

    def _process_ai(self, text):
        answer = self.logic.ask(text)
        self.root.after(0, lambda: self.update_chat("AI", answer))

if __name__ == "__main__":
    root = tk.Tk()
    PDFGui(root)
    root.mainloop()