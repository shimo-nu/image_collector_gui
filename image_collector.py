import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from bing_image_downloader import downloader
from PIL import Image, ImageTk
import os
import shutil
import threading

# 画像を保存するフォルダのパス
save_dir = 'collected_images'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 画像収集関数
def collect_images(keyword, limit=10):
    downloader.download(keyword, limit=limit, output_dir='images', adult_filter_off=True, force_replace=False, timeout=60)
    image_paths = [os.path.join('images', keyword, img) for img in os.listdir(os.path.join('images', keyword))]
    return image_paths

# GUIクラス
class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector")
        self.root.geometry("800x600")
        self.image_paths = []
        self.current_image_index = 0
        self.selected_images = []
        self.loading_label = None
        self.loading_animation = None

        # キーワードと枚数の入力
        tk.Label(root, text="キーワード:").pack()
        self.keyword_entry = tk.Entry(root)
        self.keyword_entry.pack()

        tk.Label(root, text="収集する画像の枚数:").pack()
        self.limit_entry = tk.Entry(root)
        self.limit_entry.pack()

        self.start_button = tk.Button(root, text="画像収集を開始", command=self.start_collection_thread)
        self.start_button.pack()

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.keep_button = tk.Button(root, text="保存", command=self.keep_image)
        self.keep_button.pack(side=tk.LEFT)

        self.discard_button = tk.Button(root, text="削除", command=self.discard_image)
        self.discard_button.pack(side=tk.RIGHT)

    def start_collection_thread(self):
        thread = threading.Thread(target=self.start_collection)
        thread.start()

    def start_collection(self):
        self.show_loading()
        keyword = self.keyword_entry.get()
        limit = int(self.limit_entry.get())
        self.image_paths = collect_images(keyword, limit)
        self.hide_loading()
        self.current_image_index = 0
        self.show_image()

    def show_loading(self):
        self.loading_label = tk.Label(self.root, text="ローディング中...", font=("Helvetica", 16))
        self.loading_label.pack(pady=20)
        self.loading_animation = self.create_loading_animation()
        self.loading_animation.pack(pady=20)

    def hide_loading(self):
        if self.loading_label:
            self.loading_label.pack_forget()
        if self.loading_animation:
            self.loading_animation.pack_forget()

    def create_loading_animation(self):
        frames = [tk.PhotoImage(file="loading.gif", format="gif -index %i" % i) for i in range(10)]
        loading_label = tk.Label(self.root)
        
        def update_frame(index):
            frame = frames[index]
            index += 1
            if index >= len(frames):
                index = 0
            loading_label.configure(image=frame)
            self.root.after(100, update_frame, index)
        
        update_frame(0)
        return loading_label

    def show_image(self):
        if self.current_image_index < len(self.image_paths):
            img_path = self.image_paths[self.current_image_index]
            img = Image.open(img_path)
            img = img.resize((400, 400), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.image_label.config(image=img)
            self.image_label.image = img
        else:
            messagebox.showinfo("完了", "すべての画像を処理しました")
            self.root.quit()

    def keep_image(self):
        img_path = self.image_paths[self.current_image_index]
        self.selected_images.append(img_path)
        self.current_image_index += 1
        self.show_image()

    def discard_image(self):
        img_path = self.image_paths[self.current_image_index]
        os.remove(img_path)
        self.current_image_index += 1
        self.show_image()

    def save_selected_images(self):
        for img_path in self.selected_images:
            shutil.move(img_path, save_dir)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.save_selected_images)
    root.mainloop()

