import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import cv2  # OpenCV for AVIF reading
import numpy as np
import requests
from io import BytesIO
import cloudinary
import cloudinary.uploader
import time

# Cloudinary configuration
cloudinary.config(
    cloud_name='doihflfyz',  # Replace with your Cloudinary cloud name
    api_key='144885736697597',  # Replace with your Cloudinary API key
    api_secret='eoprw93aSKaEK0MFMRmGDiinkTo'  # Replace with your Cloudinary API secret
)

timestamp = time.time()

# Initialize the main window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Image Converter")
app.geometry("500x500")

app.selected_file = None  # Store selected file
app.image_url = ""  # Store image URL


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[
        ("All Image Files", "*.png;*.jpg;*.jpeg;*.avif;*.webp;*.bmp;*.gif"),
        ("All Files", "*.*")
    ])
    if file_path:
        app.selected_file = file_path
        file_label.configure(text=f"Selected: {os.path.basename(file_path)}")
        convert_button.configure(state="normal")


def select_url():
    url = url_entry.get().strip()
    if url:
        app.image_url = url
        app.selected_file = None  # Reset local file selection
        file_label.configure(text="Using image from URL")
        convert_button.configure(state="normal")


def avif_to_format(input_file, output_file, format_choice):
    try:
        response = cloudinary.uploader.upload(input_file, format=format_choice)
        converted_url = response.get("secure_url")
        if converted_url:
            img_data = requests.get(converted_url).content
            with open(output_file, 'wb') as f:
                f.write(img_data)
            return output_file
    except Exception as e:
        raise Exception(f"Cloudinary conversion failed: {e}")


def convert_image():
    if not app.selected_file and not app.image_url:
        messagebox.showwarning("No File Selected", "Please select an image or enter a URL!")
        return

    format_choice = format_var.get().lower()
    if format_choice not in ["png", "jpg", "jpeg"]:
        messagebox.showwarning("Invalid Format", "Please select a valid output format!")
        return

    save_dir = filedialog.askdirectory()
    if not save_dir:
        status_label.configure(text="No save directory selected!", text_color="red")
        return

    try:
        if app.image_url:
            response = requests.get(app.image_url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                file_name = str(timestamp)
            else:
                raise Exception("Failed to fetch image from URL")
        else:
            file_name = os.path.splitext(os.path.basename(app.selected_file))[0]

            if app.selected_file.lower().endswith(".avif"):
                output_file = os.path.join(save_dir, f"{file_name}.{format_choice}")
                converted_file = avif_to_format(app.selected_file, output_file, format_choice)
                status_label.configure(text="Conversion Successful!", text_color="green")
                messagebox.showinfo("Success", f"Image saved at:\n{converted_file}")
                return
            else:
                img = Image.open(app.selected_file)

        save_path = os.path.join(save_dir, f"{file_name}.{format_choice}")

        if format_choice in ["jpg", "jpeg"]:
            img = img.convert("RGB")
            img.save(save_path, format="JPEG", quality=95)
        else:
            img.save(save_path, format=format_choice.upper())

        status_label.configure(text="Conversion Successful!", text_color="green")
        messagebox.showinfo("Success", f"Image saved at:\n{save_path}")

    except Exception as e:
        status_label.configure(text=f"Error: {e}", text_color="red")
        messagebox.showerror("Error", f"Failed to convert image:\n{e}")


# UI Elements
file_label = ctk.CTkLabel(app, text="Select an image file or enter a URL", font=("Arial", 14))
file_label.pack(pady=10)

select_button = ctk.CTkButton(app, text="Browse", command=select_file)
select_button.pack(pady=5)

url_entry = ctk.CTkEntry(app, placeholder_text="Enter image URL here", width=400)
url_entry.pack(pady=5)

url_button = ctk.CTkButton(app, text="Use URL", command=select_url)
url_button.pack(pady=5)

format_var = ctk.StringVar(value="png")
format_label = ctk.CTkLabel(app, text="Select Output Format:", font=("Arial", 12))
format_label.pack(pady=5)
format_dropdown = ctk.CTkComboBox(app, values=["PNG", "JPG", "JPEG"], variable=format_var)
format_dropdown.pack(pady=5)

convert_button = ctk.CTkButton(app, text="Convert", command=convert_image, state="disabled")
convert_button.pack(pady=10)

status_label = ctk.CTkLabel(app, text="", font=("Arial", 12))
status_label.pack(pady=10)

app.mainloop()