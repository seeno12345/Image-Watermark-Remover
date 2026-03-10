import tkinter as tk
from tkinter import filedialog, messagebox
from remover import WatermarkRemover

w = WatermarkRemover()
win = tk.Tk()
win.title("去水印")
win.geometry("500x200")

path = ""

def select():
    global path
    path = filedialog.askopenfilename(filetypes=[("图片","*.jpg;*.png")])
    if path:
        lb.config(text=path)

def run():
    if not path:
        messagebox.showwarning("提示","先选图片")
        return
    if w.go(path, "result.png"):
        messagebox.showinfo("完成","已保存 result.png")

tk.Button(win, text="选择", command=select).pack(pady=10)
tk.Button(win, text="去水印", command=run).pack()
lb = tk.Label(win, text="未选择")
lb.pack()

win.mainloop()