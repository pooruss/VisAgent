import os
import kaggle
from zipfile import ZipFile
import re
import requests
import time

def sanitize_filename(filename):
    return re.sub(r'[\/:*?"<>|]', '-', filename)

def download_file_with_timeout(url, dest_path, timeout=10):
    start_time = time.time()
    response = requests.get(url, stream=True)
    chunk_size = 1024
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size):
            if time.time() - start_time > timeout:
                print(f"Download time exceeded {timeout} seconds, skipping.")
                return False
            if chunk:
                f.write(chunk)
    return True

def get_all_datasets(keyword, max_datasets):
    page = 1
    datasets = []
    
    while len(datasets) < max_datasets:
        results = kaggle.api.dataset_list(search=keyword, page=page)
        if not results:
            break
        datasets.extend(results)
        page += 1
    
    return datasets[:max_datasets]

def download_and_extract_kaggle_datasets(keyword, max_datasets=5, timeout=10):
    datasets_to_download = get_all_datasets(keyword, max_datasets)
    
    for dataset in datasets_to_download:
        dataset_ref = dataset.ref
        dataset_url = f'https://www.kaggle.com/{dataset_ref}'
        dataset_name = sanitize_filename(dataset_url)
        dataset_dir = os.path.join('datasets', dataset_name)

        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)

        # Kaggle 下载链接
        download_url = f'https://www.kaggle.com/api/v1/datasets/download/{dataset_ref}'

        zip_path = os.path.join(dataset_dir, dataset_ref.split('/')[-1] + '.zip')

        print(f"Downloading {dataset_ref}...")
        
        if not download_file_with_timeout(download_url, zip_path, timeout):
            continue
        
        # 解压文件
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dataset_dir)
        
        # 删除zip文件
        os.remove(zip_path)
        
        print(f'Dataset {dataset_ref} downloaded and extracted to {dataset_dir}')

if __name__ == "__main__":
    keyword = 'financial'
    max_datasets = 100  # 指定要下载的数据集数量
    download_and_extract_kaggle_datasets(keyword, max_datasets=max_datasets)
