import os
from gui import tk, PDFGui

if __name__ == "__main__":
    if not os.path.exists("./chroma_db"):
        os.makedirs("./chroma_db")

    print("--- Starting Local PDF AI System ---")
    root = tk.Tk()
    app = PDFGui(root)
    root.mainloop()