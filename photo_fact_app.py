import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter
import os
import shutil
from datetime import datetime


class PhotoFactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Fact Assignment App")
        self.root.geometry("900x600")
        self.center_window()

        self.photos = []
        self.fact_widgets = {}
        self.default_folder = self.setup_default_folder()

        # GUI Elements
        tk.Label(root, text="Species Name:").pack(pady=(10, 0))
        self.species_name_entry = tk.Entry(root, width=50)
        self.species_name_entry.pack(pady=5)

        tk.Label(root, text="Instagram Caption:").pack(pady=(10, 0))
        self.caption_text = tk.Text(root, height=5, width=60, wrap=tk.WORD)
        self.caption_text.pack(pady=5)

        self.upload_button = tk.Button(root, text="Upload Photos", command=self.upload_photos)
        self.upload_button.pack(pady=10)

        # Scrollable Frame
        self.scrollable_frame = tk.Frame(root)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.canvas = tk.Canvas(self.scrollable_frame)
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_content = tk.Frame(self.canvas)
        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Enter>", lambda e: self.bind_canvas_scroll())
        self.canvas.bind("<Leave>", lambda e: self.unbind_canvas_scroll())

        self.generate_button = tk.Button(root, text="Generate", command=self.generate_info_images)
        self.generate_button.pack(pady=10)

    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
        x = screen_width // 2 - size[0] // 2
        y = screen_height // 2 - size[1] // 2
        self.root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

    def setup_default_folder(self):
        """Set up the default folder for saving outputs."""
        documents_dir = os.path.expanduser("~/Documents")
        output_folder = os.path.join(documents_dir, "PhotoFactApp_Output")
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def bind_canvas_scroll(self):
        self.root.bind_all("<MouseWheel>", self.scroll_canvas)

    def unbind_canvas_scroll(self):
        self.root.unbind_all("<MouseWheel>")

    def scroll_canvas(self, event):
        direction = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(direction, "units")

    def upload_photos(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Photos",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if not filepaths:
            return

        self.photos = filepaths
        self.fact_widgets.clear()
        self.display_photos_and_facts()

    def display_photos_and_facts(self):
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()

        for idx, photo_path in enumerate(self.photos):
            img = Image.open(photo_path)
            img.thumbnail((150, 150))
            img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(self.scrollable_content, image=img_tk)
            img_label.image = img_tk
            img_label.grid(row=idx, column=0, padx=10, pady=10)

            text_frame = tk.Frame(self.scrollable_content)
            text_frame.grid(row=idx, column=1, padx=10, pady=10)

            fact_text = tk.Text(text_frame, height=5, width=50, wrap=tk.WORD)
            fact_scroll = tk.Scrollbar(text_frame, command=fact_text.yview)
            fact_text.configure(yscrollcommand=fact_scroll.set)

            fact_text.bind("<Enter>", lambda e: self.bind_text_scroll(fact_text))
            fact_text.bind("<Leave>", lambda e: self.bind_canvas_scroll())

            fact_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            fact_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            self.fact_widgets[photo_path] = fact_text

    def bind_text_scroll(self, text_widget):
        self.root.bind_all("<MouseWheel>", lambda event: self.scroll_text_widget(event, text_widget))

    def scroll_text_widget(self, event, text_widget):
        direction = -1 if event.delta > 0 else 1
        text_widget.yview_scroll(direction, "units")

    def generate_info_images(self):
        species_name = self.species_name_entry.get().strip()
        caption = self.caption_text.get("1.0", tk.END).strip()
        if not species_name or not caption or not self.photos:
            messagebox.showerror("Error", "Please fill all fields and upload photos.")
            return

        facts = {photo: widget.get("1.0", tk.END).strip() for photo, widget in self.fact_widgets.items()}
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        post_folder = os.path.join(self.default_folder, f"{species_name}_{timestamp}")

        os.makedirs(post_folder, exist_ok=True)

        for photo_path, fact in facts.items():
            output_path = os.path.join(post_folder, f"info_{os.path.basename(photo_path)}")
            self.create_info_image(photo_path, fact, output_path)
            shutil.copy(photo_path, post_folder)

        with open(os.path.join(post_folder, "caption.txt"), "w") as caption_file:
            caption_file.write(caption)

        messagebox.showinfo("Success", f"Images and caption saved in {post_folder}!")

    def create_info_image(self, photo_path, fact, output_path):
        """Create the information image."""
        try:
            image = Image.open(photo_path)
            image = image.resize((1080, 1080), Image.LANCZOS)
            blurred_background = image.filter(ImageFilter.GaussianBlur(radius=50))
            draw = ImageDraw.Draw(blurred_background)
            font_path = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
            max_width = 1080 * 0.8
            max_height = 1080 * 0.8
            font_size = 20
            max_font_size = 100

            while font_size <= max_font_size:
                font = ImageFont.truetype(font_path, font_size)
                lines = self.wrap_text(fact, font, max_width, draw)
                total_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + 20 for line in lines])
                if total_height > max_height:
                    font_size -= 1
                    break
                font_size += 1

            font = ImageFont.truetype(font_path, max(font_size, 20))
            wrapped_text = self.wrap_text(fact, font, max_width, draw)
            total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + 20 for line in wrapped_text])
            start_y = (1080 - total_text_height) / 2

            for line in wrapped_text:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                start_x = (1080 - text_width) / 2
                draw.text((start_x, start_y), line, font=font, fill="white")
                start_y += bbox[3] - bbox[1] + 20

            blurred_background.save(output_path)
        except Exception as e:
            print(f"Error processing image {photo_path}: {e}")

    def wrap_text(self, text, font, max_width, draw):
        """Wrap text into lines that fit within the max_width."""
        words = text.split()
        lines = []
        current_line = ''
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width and len(test_line.split()) > 1:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoFactApp(root)
    root.mainloop()
