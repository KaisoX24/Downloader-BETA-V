import zipfile
import os

def zip_downloaded_files(dest_path,temp_folder_path, zip_name="download.zip"):
    zip_path = os.path.join(dest_path, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(temp_folder_path):
            full_path = os.path.join(temp_folder_path, file)

            if file.endswith(".zip"):
                continue

            if os.path.isfile(full_path):
                zipf.write(full_path, arcname=file)

if __name__=='__main__':
    zip_downloaded_files('','')