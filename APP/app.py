import customtkinter as ctk
from tkinter import filedialog,PhotoImage,messagebox
from pathlib import Path
from modules.download import download_youtube_video,fetch_thumbnail,convert_mp4_to_mp3
from modules.errors import show_rate_limit_error,show_cookie_error
from modules.img_load import load_thumbnail_into_label
from modules.zip_files import zip_downloaded_files
import os
import threading
import shutil
import time
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def option_selected(value):
    if value == "Youtube Files":
        label_url.place(x=15, y=140)
        video_url.place(x=15, y=170)
    else:
        label_url.place_forget()
        video_url.place_forget()
        upload_label.place(x=15, y=140)
        save_entry2.place(x=15, y=170)
        upload_browse.place(x=15, y=210)

def check_url_content(event=None):
    urls = video_url.get("1.0", "end-1c").strip()
    url_jobs = [u.strip() for u in urls.split("\n") if u.strip()]
    if url_jobs:  
        mp4rad1.place(x=15, y=280)
        mp3rad2.place(x=15, y=310)
    else:
        mp4rad1.place_forget()
        mp3rad2.place_forget()
        res_label.place_forget()
        vid_res.place_forget()
    return url_jobs

def forget_all():
    aud_label.place_forget()
    aud_qut.place_forget()
    save_label.place_forget()
    save_entry.place_forget()
    browse_button.place_forget()
    res_label.place_forget()
    vid_res.place_forget()

def save_location_place_YT(event=None):
    save_label.place(x=15, y=420)
    save_entry.place(x=15, y=445)
    browse_button.place(x=15, y=485)

def save_location_place_YT_MP3(event=None):
    save_label.place(x=15, y=420)
    save_entry.place(x=15, y=445)
    browse_button.place(x=15, y=485)

def save_location_place():
    save_label.place(x=15,y=250)
    save_entry.place(x=15,y=280)
    browse_button2.place(x=15, y=320)

def format_selection():
    if output_format.get() == "MP4":
        forget_all()
        res_label.place(x=15, y=350)
        vid_res.place(x=15, y=380)
    elif output_format.get() == "MP3":
        forget_all()
        aud_label.place(x=15, y=350)
        aud_qut.place(x=15, y=380)
    else:
        forget_all()

def download_button(event=None):
    if event=='Yt':
        button_1.place(x=10, y=520)
    elif event=='vid':
        button_2.place(x=10, y=520)

def browse_folder(event=None):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        save_entry.delete(0, "end")
        save_entry.insert(0, folder_selected)
    download_button(event='Yt')

def browse_folder_vid(event=None):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        save_entry.delete(0, "end")
        save_entry.insert(0, folder_selected)
    download_button(event='vid')

def save_file(event=None):
    file_selected=filedialog.askopenfilename(filetypes=[('Video Files','*.mp4 *.mkv')])
    if file_selected:
        save_entry2.delete(0, "end")
        save_entry2.insert(0, file_selected)
    save_location_place()
    
def download_mp3_file():
    thread = threading.Thread(target=run_conversion)
    thread.start()

def run_conversion():
    try:
        convert_mp4_to_mp3(save_entry2.get(), save_entry.get())
        window.after(0,lambda:messagebox.showinfo(
            "Conversion Complete",
            "✅ The video has been converted to MP3 successfully!"
        ))
    except Exception as e:
        window.after(0,lambda:messagebox.showerror("Error", f"Conversion failed:\n{e}"))

def create_download_row(title,key='p'):
    row_frame = ctk.CTkFrame(downloads_frame, fg_color="#0B0C10")
    row_frame.pack(fill="x", pady=10, padx=1)

    thumb_label = ctk.CTkLabel(row_frame, text="", width=120)
    thumb_label.pack(side="left", padx=10)

    info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
    info_frame.pack(side="left", fill="x", expand=True)

    title_label = ctk.CTkLabel(
        info_frame,
        text=title,
        wraplength=400,
        anchor="w",
        justify="left"
    )
    title_label.pack(anchor="w")

    progress = ctk.CTkProgressBar(info_frame,progress_color="#1DFF83",fg_color="#D9D9D9")
    progress.pack(fill="x", pady=5)

    status = ctk.CTkLabel(info_frame, text="Preparing...")
    status.pack(anchor="w")

    return thumb_label, progress, status

def start_download():
    url_jobs = check_url_content()

    if url_jobs:
        def worker():
            appdata = Path(os.getenv("LOCALAPPDATA")) / "DownloadBetaV"
            appdata.mkdir(parents=True, exist_ok=True)
            batch_folder = appdata / f"batch_{int(time.time()*1000)}"
            batch_folder.mkdir()
            try:
                for url in url_jobs:
                    try:
                        thum_temp_dir=None
                        thumb_path, vid_title,thum_temp_dir = fetch_thumbnail(url)
                    except Exception as e:
                        window.after(0, lambda: messagebox.showerror(
                            "COULDNT LOAD THUMBNAIL",
                            f"{type(e).__name__}:\n{str(e)}"
                        ))
                        continue
                    row_ready=threading.Event()
                    row_widgets = {}
                    def setup_row():
                        try:
                            thumb_label, row_progress_bar, row_status_label = create_download_row(vid_title,"pl")
                            load_thumbnail_into_label(thumb_path, thumb_label)
                            row_widgets["progress"] = row_progress_bar
                            row_widgets["status"] = row_status_label
                            row_ready.set()
                        except Exception as e:
                            messagebox.showerror("UI Error", str(e))
                        finally:
                            row_ready.set()

                    window.after(0, setup_row)
                    row_ready.wait()

                    def row_progress(value):
                        window.after(0, lambda: row_widgets["progress"].set(value))

                    def row_status(text):
                        window.after(0, lambda: row_widgets["status"].configure(text=text))
                    if len(url_jobs)==1:
                        download_youtube_video(
                            url,
                            res_var.get(),
                            aud_var.get(),
                            output_format.get().lower(),
                            save_entry.get(),
                            progress_callback=row_progress,
                            status_callback=row_status
                        )
                    else:
                        download_youtube_video(
                            url,
                            res_var.get(),
                            aud_var.get(),
                            output_format.get().lower(),
                            batch_folder,
                            progress_callback=row_progress,
                            status_callback=row_status
                        )
            except Exception as e:
                error_text=str(e)
                if "429" in error_text or "Too Many Requests" in error_text:
                    show_rate_limit_error()
                elif "Sign in" in error_text or "bot" in error_text or "cookie" in error_text:
                    show_cookie_error()
                else:
                    window.after(0, lambda: messagebox.showerror(
                            "Download Error",
                            f"{type(e).__name__}:\n{str(e)}"
                        ))
            finally:
                if len(url_jobs)>1:
                    zip_downloaded_files(save_entry.get(),batch_folder)
                if batch_folder.exists():
                    shutil.rmtree(batch_folder, ignore_errors=True)
                if thum_temp_dir and thum_temp_dir.exists():
                    shutil.rmtree(thum_temp_dir, ignore_errors=True)
                window.after(0, lambda: button_1.configure(state='normal'))
                window.after(0, lambda: messagebox.showinfo(
                    "Download Complete",
                    "✅ All downloads completed successfully!"
                ))
                window.after(2000,lambda: [w.destroy() for w in downloads_frame.winfo_children()])
        window.after(0, lambda: button_1.configure(state='disabled'))
        threading.Thread(target=worker, daemon=True).start()
        
# Main Window
window = ctk.CTk()
window.geometry("1100x700")
window.title("Download BETA V")
window.iconbitmap(resource_path(r'assets\\icon.ico'))
window.configure(fg_color="#0B0C10")
window.resizable(False, False)

# Sidebar Frame (Left panel)
sidebar = ctk.CTkFrame(
    window,
    width=240,
    height=700,
    fg_color="#12141B",
    corner_radius=0
)
sidebar.place(x=0, y=0)

# Main background frame
main_frame = ctk.CTkFrame(
    window,
    width=1100,
    height=700,
    fg_color="#0B0C10",
    corner_radius=0
)
main_frame.place(x=240, y=0)
main_frame.pack_propagate(False)

#Scroll section
downloads_frame = ctk.CTkScrollableFrame(
    main_frame,
    width=600,
    height=500,
    fg_color="#0B0C10",
    scrollbar_fg_color="#0B0C10",
    scrollbar_button_color="#0B0C10",
    scrollbar_button_hover_color="#0B0C10",
)
downloads_frame.place(relx=0.4, rely=0.55, anchor="center")


# Images
image_image_1 = PhotoImage(file=resource_path(r"assets\\frame0\\image_1.png"))
image_label_1 = ctk.CTkLabel(
    main_frame,
    image=image_image_1,
    text=""
)
image_label_1.place(x=250, y=63)

image_image_2 = PhotoImage(file=resource_path(r"assets\\frame0\\image_2.png"))
image_label_2 = ctk.CTkLabel(
    sidebar,
    image=image_image_2,
    text=""
)
image_label_2.place(x=26, y=43)

#Progress bar and status
progress_label = ctk.CTkLabel(main_frame, text="downloading", text_color="white")
progress_bar = ctk.CTkProgressBar(main_frame, width=300,fg_color="#D9D9D9", progress_color="#1DFF83")
progress_bar.set(0)

# Textbox
choice = ctk.CTkOptionMenu(
    sidebar,
    width=205,
    height=32,
    fg_color="#D9D9D9",
    text_color="#000716",
    corner_radius=6,
    values=['Youtube Files','Video Files'],
    command=option_selected
)
choice.place(x=15, y=100)
label_url = ctk.CTkLabel(
    sidebar,
    text="Enter the URL:",
    text_color="#1DFF83",
    font=ctk.CTkFont(size=12, weight="bold")
)
res_label=ctk.CTkLabel(
        sidebar,
        text="Select video resolution:",
        text_color="#1DFF83",
        font=ctk.CTkFont(size=12, weight="bold")
    )

aud_label=ctk.CTkLabel(
        sidebar,
        text="Select audio quality:",
        text_color="#1DFF83",
        font=ctk.CTkFont(size=12, weight="bold")
    )

video_url = ctk.CTkTextbox(
    sidebar,
    width=205,
    height=100,
    fg_color="#D9D9D9",
    text_color="#000716",
    corner_radius=6,
    wrap='word'
)

video_url.bind("<Control-Return>", check_url_content)
video_url.bind("<Command-Return>", check_url_content)

output_format = ctk.StringVar(value="MP4")
mp4rad1 = ctk.CTkRadioButton(
    sidebar,
    text="MP4",
    variable=output_format,
    value="MP4",
    command=format_selection
)
mp3rad2 = ctk.CTkRadioButton(
    sidebar,
    text="MP3",
    variable=output_format,
    value="MP3",
    command=format_selection
)

res_var=ctk.StringVar(value="Best")
vid_res=ctk.CTkOptionMenu(
        sidebar,
        width=205,
        height=32,
        fg_color="#D9D9D9",
        text_color="#000716",
        corner_radius=6,
        variable=res_var,
        values=['Best','480P','720P','1080P'],
        command=save_location_place_YT
    )
aud_var=ctk.StringVar(value="192k")
aud_qut=ctk.CTkOptionMenu(
    sidebar,
    width=205,
    height=32,
    fg_color="#D9D9D9",
    text_color="#000716",
    corner_radius=6,
    variable=aud_var,
    values=['128k','192k','256k','320k'],
    command=save_location_place_YT_MP3
)
save_label=ctk.CTkLabel(
    sidebar,
    text="Save Location:",
    text_color="#1DFF83",
    font=ctk.CTkFont(size=12, weight="bold")
)
save_label_idk_what_number=ctk.CTkLabel(
    sidebar,
    text="Save Location:",
    text_color="#1DFF83",
    font=ctk.CTkFont(size=12, weight="bold")
)
upload_label=ctk.CTkLabel(
    sidebar,
    text="Upload File:",
    text_color="#1DFF83",
    font=ctk.CTkFont(size=12, weight="bold")
)
save_entry = ctk.CTkEntry(
    sidebar,
    width=175,
    height=32,
    fg_color="#D9D9D9",
    text_color="#000716",
    corner_radius=6
)
save_entry2=ctk.CTkEntry(
    sidebar,
    width=175,
    height=32,
    fg_color="#D9D9D9",
    text_color="#000716",
    corner_radius=6
)
save_entry_idk=ctk.CTkEntry(
    sidebar,
    width=175,
    height=32,
    fg_color="#D9D9D9",
    text_color="#000716",
    corner_radius=6
)
upload_browse=ctk.CTkButton(
    sidebar,
    text="Browse",
    width=20,
    height=20,
    fg_color="#F8EC40",
    text_color="#15DB46",
    corner_radius=6,
    command=save_file)

browse_button = ctk.CTkButton(
    sidebar,
    text="Browse",
    width=20,
    height=20,
    fg_color="#F8EC40",
    text_color="#15DB46",
    corner_radius=6,
    command=browse_folder
)
browse_button2 = ctk.CTkButton(
    sidebar,
    text="Browse",
    width=20,
    height=20,
    fg_color="#F8EC40",
    text_color="#15DB46",
    corner_radius=6,
    command=browse_folder_vid
)

# Button images
button_image_1 = PhotoImage(file=resource_path(r"assets\\frame0\\button_1.png"))
button_image_hover_1 = PhotoImage(file=resource_path(r"assets\\frame0\\button_hover_1.png"))

# Button
button_1 = ctk.CTkButton(
    sidebar,
    image=button_image_1,
    text="",
    width=205,
    height=55,
    fg_color="transparent",
    hover=False,
    command=start_download
)
button_2 = ctk.CTkButton(
    sidebar,
    image=button_image_1,
    text="",
    width=205,
    height=55,
    fg_color="transparent",
    hover=False,
    command=download_mp3_file
)

# Hover effects
def button_1_hover(e):
    button_1.configure(image=button_image_hover_1)
    button_2.configure(image=button_image_hover_1)


def button_1_leave(e):
    button_1.configure(image=button_image_1)
    button_2.configure(image=button_image_1)

button_1.bind("<Enter>", button_1_hover)
button_1.bind("<Leave>", button_1_leave)
button_2.bind("<Enter>", button_1_hover)
button_2.bind("<Leave>", button_1_leave)

window.mainloop()