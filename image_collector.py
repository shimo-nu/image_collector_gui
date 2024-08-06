import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from bing_image_downloader import downloader
from PIL import Image, ImageTk
import os
import shutil
import threading

# 一時保存先ディレクトリ
temp_dir = 'images'

# 収集済み画像のURLを追跡するセット
collected_image_urls = set()

# 画像収集関数
def collect_images(keyword, limit=10):
    downloader.download(keyword, limit=limit, output_dir=temp_dir, adult_filter_off=True, force_replace=False, timeout=60)
    image_paths = [os.path.join(temp_dir, keyword, img) for img in os.listdir(os.path.join(temp_dir, keyword))]
    return image_paths

# 一時ディレクトリを削除する関数
def clean_temp_directory():
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# ユニークなファイル名を生成する関数
def generate_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    unique_filename = filename
    counter = 1
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}_{counter}{ext}"
        counter += 1
    return unique_filename

# GUIクラス
class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector")
        self.root.geometry("1200x800")  # ウィンドウサイズを1200x800に設定

         # 属性の初期化
        self.image_paths = []
        self.current_image_index = 0
        self.selected_images = []  # ここでselected_imagesを初期化


        # フレームの設定
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 左側の上部に配置
        self.input_frame = tk.Frame(self.left_frame)
        self.input_frame.pack(anchor=tk.NW, fill=tk.X)

        # キーワードと枚数の入力（リアルタイムで表示）
        self.keyword_var = tk.StringVar()
        self.keyword_var.trace("w", self.update_displayed_info)
        self.limit_var = tk.StringVar()
        self.limit_var.trace("w", self.update_displayed_info)
        self.save_dir_var = tk.StringVar()
        self.save_dir_var.trace("w", self.update_displayed_info)

        tk.Label(self.input_frame, text="キーワード:").pack(anchor=tk.W)
        self.keyword_entry = tk.Entry(self.input_frame, textvariable=self.keyword_var, width=30)
        self.keyword_entry.pack(anchor=tk.W)

        tk.Label(self.input_frame, text="収集する画像の枚数:").pack(anchor=tk.W)
        self.limit_entry = tk.Entry(self.input_frame, textvariable=self.limit_var, width=30)
        self.limit_entry.pack(anchor=tk.W)

        tk.Label(self.input_frame, text="保存先ディレクトリ名:").pack(anchor=tk.W)
        self.save_dir_entry = tk.Entry(self.input_frame, textvariable=self.save_dir_var, width=30)
        self.save_dir_entry.pack(anchor=tk.W)

        self.start_button = tk.Button(self.input_frame, text="画像収集を開始", command=self.start_collection_thread)
        self.start_button.pack(anchor=tk.W, pady=10)

        # 区切り線を追加
        self.separator = tk.Frame(self.left_frame, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, pady=20)

        # 左側の下部に配置
        self.info_frame = tk.Frame(self.left_frame)
        self.info_frame.pack(anchor=tk.SW, fill=tk.X)

        # 入力された情報の表示ラベル
        self.keyword_label = tk.Label(self.info_frame, text="キーワード:             ")
        self.keyword_label.pack(anchor=tk.W)

        self.limit_label = tk.Label(self.info_frame, text="収集する画像の枚数:     ")
        self.limit_label.pack(anchor=tk.W)

        self.save_dir_label = tk.Label(self.info_frame, text="保存先ディレクトリ名:   ")
        self.save_dir_label.pack(anchor=tk.W)

        # 右側の7:3に分割
        self.image_frame = tk.Frame(self.right_frame, height=500)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.right_frame, height=200)
        self.button_frame.pack(fill=tk.X)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(expand=True)

        self.keep_button = tk.Button(self.button_frame, text="保存", command=self.keep_image)
        self.keep_button.pack(side=tk.LEFT, padx=10, pady=10, expand=True)

        self.discard_button = tk.Button(self.button_frame, text="削除", command=self.discard_image)
        self.discard_button.pack(side=tk.RIGHT, padx=10, pady=10, expand=True)

    def start_collection_thread(self):
        thread = threading.Thread(target=self.start_collection)
        thread.start()

    def start_collection(self):
        self.show_loading()
        keyword = self.keyword_var.get()
        limit = int(self.limit_var.get())
        image_paths = collect_images(keyword, limit)

        # 新しい画像だけを残す
        new_image_paths = []
        for img_path in image_paths:
            img_url = os.path.basename(img_path)  # ファイル名をURLの代わりに使用
            if img_url not in collected_image_urls:
                collected_image_urls.add(img_url)
                new_image_paths.append(img_path)

        self.hide_loading()
        self.image_paths = new_image_paths
        self.current_image_index = 0
        self.displayed_images = self.prepare_images_for_display(self.image_paths)
        self.show_image()

    def update_displayed_info(self, *args):
        self.keyword_label.config(text=f"キーワード:\n {self.keyword_var.get()}")
        self.limit_label.config(text=f"収集する画像の枚数:\n {self.limit_var.get()}")
        self.save_dir_label.config(text=f"保存先ディレクトリ名:\n {self.save_dir_var.get()}")

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

    def prepare_images_for_display(self, image_paths):
        displayed_images = []
        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                img.thumbnail((600, 400), Image.LANCZOS)  # 表示用にリサイズ
                displayed_images.append(ImageTk.PhotoImage(img))
            except PermissionError:
                print(f"Permission denied for {img_path}")
                continue
        return displayed_images

    def show_image(self):
        if self.current_image_index < len(self.displayed_images):
            img = self.displayed_images[self.current_image_index]
            self.image_label.config(image=img)
            self.image_label.image = img
        else:
            self.save_selected_images()
            self.ask_next_action()

    def keep_image(self):
        if self.current_image_index < len(self.image_paths):
            img_path = self.image_paths[self.current_image_index]
            self.selected_images.append(img_path)
            self.current_image_index += 1
            self.show_image()

    def discard_image(self):
        if self.current_image_index < len(self.image_paths):
            img_path = self.image_paths[self.current_image_index]
            try:
                os.remove(img_path)
            except PermissionError:
                print(f"Permission denied for {img_path}")
            self.current_image_index += 1
            self.show_image()

    def save_selected_images(self):
        save_dir = os.path.join('collected_images', self.save_dir_var.get())
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        for img_path in self.selected_images:
            unique_filename = generate_unique_filename(save_dir, os.path.basename(img_path))
            shutil.move(img_path, os.path.join(save_dir, unique_filename))
        self.selected_images.clear()

    def ask_next_action(self):
        response = messagebox.askquestion(
            "次のアクション",
            "違うキーワードで収集しますか？\n同じキーワードで再度収集しますか？",
            icon="question",
            type="yesnocancel",
            default="cancel"
        )
        if response == "yes":
            self.reset_for_new_keyword()
        elif response == "no":
            self.reset_for_same_keyword()
        else:
            self.root.quit()
            clean_temp_directory()

    def reset_for_new_keyword(self):
        self.keyword_var.set("")  # キーワードをリセット
        self.limit_var.set("")    # 収集する画像の枚数をリセット
        self.save_dir_var.set("") # 保存先ディレクトリ名をリセット

    def reset_for_same_keyword(self):
        self.start_collection_thread()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.save_selected_images(), clean_temp_directory(), root.destroy()])
    root.mainloop()
