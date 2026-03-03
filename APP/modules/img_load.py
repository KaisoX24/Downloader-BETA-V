from PIL import Image
import customtkinter as ctk

def load_thumbnail_into_label(path, label):
    img = Image.open(path)
    img = img.resize((120, 70))  

    ctk_img = ctk.CTkImage(light_image=img, size=(120, 70))

    label.configure(image=ctk_img)
    label.image = ctk_img

if __name__=='__main__':
    load_thumbnail_into_label('','') 