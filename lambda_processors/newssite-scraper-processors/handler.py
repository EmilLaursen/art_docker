# Always available in Lambda runtime.
import boto3

# Native deps
import json
from datetime import datetime
import time
import zipfile
from pathlib import Path
from typing import List
from itertools import chain

# Non-native deps
from jq import jq

# Application imports
from jq_scripts import NON_EMPTY_FILEKEYS, EMPTY_FILEKEYS, DELETE_FILTER

# TODO: Change this for lambda production.
TEMP_DIR = Path("/tmp/")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

s3 = boto3.client("s3")
BUCKET_NAME = BUCKET_NAME = "dk-new-scrape"

scraper_dirs = [
    "arbejderen_frontpage",
    "bt_frontpage",
    "finans_frontpage",
    "dr_frontpage",
    "kristeligt_frontpage",
]


def hello(event, context):

    upload_statuss, empty_file_keys = [], []
    for s_dir in scraper_dirs:

        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=s_dir + "/")

        empty_file_keys = extract_keys(response=response, jq_filter=EMPTY_FILEKEYS)
        keys = extract_keys(response=response, jq_filter=NON_EMPTY_FILEKEYS)

        if keys:

            local_files = download_keys(keys=keys, output_dir=TEMP_DIR)
            zipped = zip_files(files=local_files, destination_folder=TEMP_DIR)

            success = upload_file(
                zipped, BUCKET_NAME, object_name=s_dir + "/" + zipped.name
            )
            upload_statuss.append(success)
            if success:
                print(f"Uploaded file: {s_dir + '/' +  zipped.name}")
                for key in keys:
                    delete_resp = s3.delete_object(Bucket=BUCKET_NAME, Key=str(key),)
                    print(
                        f"Deleted key: {key}. Delete response: {jq(DELETE_FILTER).transform(delete_resp)}"
                    )

        if empty_file_keys:
            for key in empty_file_keys:
                delete_resp = s3.delete_object(Bucket=BUCKET_NAME, Key=str(key),)
                print(
                    f"Deleted empty key: {key}. Delete response: {jq(DELETE_FILTER).transform(delete_resp)}"
                )

    print(f"Upload success: {all(upload_statuss)}. Details: {upload_statuss}")
    return upload_statuss


def extract_keys(response: dict, jq_filter: str = NON_EMPTY_FILEKEYS) -> List[Path]:
    parsed_aws_response = jsonify(response)
    key_strings = jq(jq_filter).transform(parsed_aws_response, multiple_output=True)
    keys = [Path(key) for key in key_strings]
    return keys


def datetime2str(dt: datetime) -> str:
    if isinstance(dt, datetime):
        return str(dt)
    return dt


def jsonify(response):
    return json.loads(json.dumps(response, default=datetime2str))


def download_keys(keys: List[Path], output_dir: Path) -> List[Path]:
    output_files = [(output_dir / key.name) for key in keys]

    start = time.time()
    for local_file, key in zip(output_files, keys):
        with local_file.open("wb") as lfile:
            s3.download_fileobj(BUCKET_NAME, str(key), lfile)

    print(f"Downloaded keys in {time.time() - start:.1f} secs: {keys}")
    return output_files


def datetime_now_hr_min():
    return datetime.now().strftime("%Y-%m-%d_%H:%M")


def zip_files(files: List[Path], destination_folder: Path):
    destination_folder.mkdir(parents=True, exist_ok=True)
    zip_dst = destination_folder / f"{datetime_now_hr_min()}.zip"

    file_sizes = []
    start = time.time()
    with zipfile.ZipFile(
        zip_dst, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as f_out:

        for file in files:
            file_sizes.append(file.stat().st_size)
            f_out.write(file, arcname=file.name)

    zip_size = zip_dst.stat().st_size
    print(
        f"Zipped file: {zip_dst} Elasped time: {(time.time() - start) / 1000:.1f} ms. Space savings: {(1 - zip_size / sum(file_sizes))*100:.1f} percent"
    )
    return zip_dst


def upload_file(file_path: Path, bucket: str, object_name: str = None):
    """Upload a file to an S3 bucket

    :param file_path: File Path object to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_path.name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_path
    if object_name is None:
        object_name = file_path.name
    # Upload the file
    s3_client = boto3.client("s3")
    try:
        _ = s3_client.upload_file(str(file_path), bucket, object_name)
    except (ClientError, s3_client.exceptions.NoSuchBucket, S3UploadFailedError) as e:
        print(e)
        return False
    return True
