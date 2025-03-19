import requests
import os
import tqdm
import logging
from pydantic import BaseModel
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

def download_file(url: str, dest_path: str, show_progress_bars: bool = True):
    """downloads a file and shows a progress bar. allow resuming a download"""
    file_size = 0
    req = requests.get(url, stream=True, timeout=600)
    req.raise_for_status()

    total_size = int(req.headers.get('content-length', 0))
    temp_path = dest_path + ".temp"

    if os.path.exists(dest_path):
        logger.info(f" file already exists: {dest_path}")
        file_size = os.stat(dest_path).st_size
        if file_size == total_size:
            return dest_path

    if os.path.exists(temp_path):
        file_size = os.stat(temp_path).st_size

        if file_size < total_size:
            # Download incomplete
            logger.info("  resuming download")
            resume_header = {'Range': f'bytes={file_size}-'}
            req = requests.get(url, headers=resume_header, stream=True,
                               verify=False, allow_redirects=True, timeout=600)
        else:
            # Error, delete file and restart download
            logger.error(f" deleting file {dest_path} and restarting")
            os.remove(temp_path)
            file_size = 0
    else:
        # File does not exist, starting download
        logger.info("  starting download")

    # write dataset to file and show progress bar
    pbar = tqdm.tqdm(total=total_size, unit='B', unit_scale=True,
                     desc=dest_path, disable=not show_progress_bars)
    # Update progress bar to reflect how much of the file is already downloaded
    pbar.update(file_size)
    with open(temp_path, "ab") as dest_file:
        for chunk in req.iter_content(1024):
            dest_file.write(chunk)
            pbar.update(1024)
    # move temp file to target destination
    os.replace(temp_path, dest_path)
    return dest_path


class SingleModel(BaseModel):
    coin_id: int
    evaluations: List[Dict[str, Any]]
    created: str
    model_id: int
    name: str
    status: str
    target: str
    updated: str
    dev_id: str
    target_type: str
    class Config:
        protected_namespaces = ()
    
    
class AllModels(BaseModel):
    models: List[SingleModel]


class AccountInfo(BaseModel):
    api_key: bool
    models: List[SingleModel]
    user_id: str
    username: str
    updated: str
    created: str


class ModelEvaluation(BaseModel):
    benchmarks: Dict[str, Dict[str, Any]]
    metrics: Dict[str, Any]


class ApiKeyGeneration(BaseModel):
    api_key: str


class DataInfo(BaseModel):
    data: Dict[str, Dict[str, Dict[str, List[str]]]]
    coins: List[str]
    feature_sizes: List[str]
    targets: Dict[str, str]
    versions: Dict[str, float]
