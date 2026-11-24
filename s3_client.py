import time

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9001',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadminpassword',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1',
)

BUCKET_NAME = 'distributed-course-bucket'


def init_storage():
    """Create the bucket if it does not exist yet."""
    buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]
    if BUCKET_NAME not in buckets:
        s3.create_bucket(Bucket=BUCKET_NAME)


def upload_object(key_name, file_path, metadata=None):
    """Upload a file with custom metadata. Returns elapsed seconds."""
    start = time.time()
    s3.upload_file(
        Filename=file_path,
        Bucket=BUCKET_NAME,
        Key=key_name,
        ExtraArgs={'Metadata': metadata or {}},
    )
    return time.time() - start


def download_object(key_name, dest_path):
    """Download an object to a local file. Returns elapsed seconds."""
    start = time.time()
    s3.download_file(BUCKET_NAME, key_name, dest_path)
    return time.time() - start


def read_object_metadata(key_name):
    """HEAD the object and return its custom metadata dict."""
    return s3.head_object(Bucket=BUCKET_NAME, Key=key_name)['Metadata']


def list_objects(prefix=''):
    resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    return [o['Key'] for o in resp.get('Contents', [])]


def delete_object(key_name):
    s3.delete_object(Bucket=BUCKET_NAME, Key=key_name)


def object_exists(key_name):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key_name)
        return True
    except ClientError:
        return False


if __name__ == '__main__':
    import os
    import tempfile

    init_storage()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(os.urandom(100 * 1024 * 1024))   # 100 MB payload
        path = f.name
    t = upload_object('data/sample_100m.bin', path,
                      {'owner': 'student', 'course': 'CSS4004'})
    print(f'Upload: {t:.2f}s')
    print('Metadata:', read_object_metadata('data/sample_100m.bin'))
    print(f'Download: {download_object("data/sample_100m.bin", path + ".out"):.2f}s')
    os.remove(path)
    os.remove(path + '.out')
