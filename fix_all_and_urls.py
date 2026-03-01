import os
import unicodedata
import re
import urllib.parse

def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9\-]', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text

base_path = r'c:\Users\Tiago\Desktop\PROJETOS\01. BACKUP\albumsankofa'
folders = [
    'a-escolha-e-nossa',
    'baoba-ancestral',
    'batuque-de-malungo',
    'boia-fria',
    'ensaio-show',
    'pe-de coco'
]

# 1. Rename 'pe-de coco' folder to 'pe-de-coco' if it exists
old_coco_path = os.path.join(base_path, 'pe-de coco')
new_coco_path = os.path.join(base_path, 'pe-de-coco')

if os.path.exists(old_coco_path):
    print(f"Renaming folder: '{old_coco_path}' -> '{new_coco_path}'")
    # Terminate any process that might be using it? I'll just try.
    try:
        os.rename(old_coco_path, new_coco_path)
    except Exception as e:
        print(f"Error renaming folder: {e}")

# Update folders list
folders = [f if f != 'pe-de coco' else 'pe-de-coco' for f in folders]

# 2. Rename files in all folders to ensure they follow the taxonomy [folder-name]-instrument.mp3
for folder in folders:
    folder_path = os.path.join(base_path, folder)
    if not os.path.exists(folder_path):
        continue
    
    print(f"Checking files in: {folder}")
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):
            # If it already follows the pattern [folder]-instrument.mp3, skip
            # But wait, we want to be SURE.
            # Extract the 'instrument' part. 
            # If the filename starts with [folder]- then it might be okay.
            prefix = f"[{folder}]-"
            if filename.startswith(prefix):
                # Ensure the rest is slugified
                name_part = filename[len(prefix):-4]
                slug_part = slugify(name_part)
                new_filename = f"{prefix}{slug_part}.mp3"
            else:
                # Need to extract instrument name from old format
                # For 'pe-de coco', it was like '[pé de coco]agogo.mp3'
                # For others, it might be different.
                # Let's just slugify the whole name without extension and re-prefix.
                # But we should try to remove the old bracket part if it exists.
                name_without_ext = os.path.splitext(filename)[0]
                # Remove anything inside brackets at the start
                clean_name = re.sub(r'^\[.*?\]', '', name_without_ext)
                slug_part = slugify(clean_name)
                new_filename = f"[{folder}]-{slug_part}.mp3"
            
            if filename != new_filename:
                old_file_path = os.path.join(folder_path, filename)
                new_file_path = os.path.join(folder_path, new_filename)
                print(f"  Renaming file: '{filename}' -> '{new_filename}'")
                try:
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path) # Avoid conflict
                    os.rename(old_file_path, new_file_path)
                except Exception as e:
                    print(f"  Error renaming file: {e}")

# 3. Generate instrumentos_urls.txt
print("Generating instrumentos_urls.txt...")
header = ""
content_lines = []

ordered_folders = [
    'a-escolha-e-nossa',
    'baoba-ancestral',
    'batuque-de-malungo',
    'boia-fria',
    'pe-de-coco',
    'ensaio-show'
]

repo_name = "BesouroLAB/albumsankofa"
base_url = f"https://raw.githubusercontent.com/{repo_name}/main/"

for folder in ordered_folders:
    folder_path = os.path.join(base_path, folder)
    if not os.path.exists(folder_path):
        continue
    
    content_lines.append(folder)
    content_lines.append("")
    
    files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
    files.sort() # Ensure consistent order
    
    for f in files:
        # Properly encode filename for URL
        encoded_f = urllib.parse.quote(f)
        url = f"{base_url}{folder}/{encoded_f}"
        content_lines.append(url)
    
    content_lines.append("")

with open(os.path.join(base_path, 'instrumentos_urls.txt'), 'w', encoding='utf-8') as f:
    f.write("\n".join(content_lines))

print("Done!")
