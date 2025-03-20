import os
import requests
from tqdm import tqdm
import zipfile
import tarfile

def gitclone(url: str, output_filename: str = "repo.zip", dest_dir: str = "."):
    if url.endswith('.git'):
        base_url = url[:-4]
    else:
        base_url = url
    download_url = base_url + "/archive/refs/heads/main.zip"
    response = requests.get(download_url, stream=True)
    if response.status_code != 200:
        download_url = base_url + "/archive/refs/heads/master.zip"
        response = requests.get(download_url, stream=True)
        if response.status_code != 200:
            response.raise_for_status()
    os.makedirs(dest_dir, exist_ok=True)
    file_path = os.path.join(dest_dir, output_filename)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    with open(file_path, 'wb') as file, tqdm(
        desc="Downloading repository",
        total=total_size,
        unit='B',
        unit_scale=True,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {unit}"
    ) as bar:
        for data in response.iter_content(block_size):
            file.write(data)
            bar.update(len(data))
    return file_path

def extract_archive(archive_path: str, extract_to: str = None):
    if extract_to is None:
        extract_to = os.path.dirname(archive_path)
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, 'r') as archive:
            members = archive.infolist()
            with tqdm(total=len(members), desc="Extracting (ZIP)", unit="file", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {unit}") as bar:
                for member in members:
                    archive.extract(member, path=extract_to)
                    bar.update(1)
    elif tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, 'r:*') as archive:
            members = archive.getmembers()
            with tqdm(total=len(members), desc="Extracting (TAR)", unit="file", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {unit}") as bar:
                for member in members:
                    archive.extract(member, path=extract_to)
                    bar.update(1)
    else:
        raise ValueError("Unsupported archive format")
