import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

BUCKET = 'distributed-course-bucket'


@pytest.fixture(scope="module")
def s3_client():
    client = boto3.client(
        's3',
        endpoint_url='http://localhost:9001',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadminpassword',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1',
    )
    names = [b['Name'] for b in client.list_buckets()['Buckets']]
    if BUCKET not in names:
        client.create_bucket(Bucket=BUCKET)
    return client


def test_s3_bucket_existence(s3_client):
    buckets = [b['Name'] for b in s3_client.list_buckets()['Buckets']]
    assert BUCKET in buckets


def test_s3_object_upload_and_read(s3_client):
    key, content = "test_dir/sample.txt", b"Stream Data Content"
    s3_client.put_object(Bucket=BUCKET, Key=key, Body=content)
    obj = s3_client.get_object(Bucket=BUCKET, Key=key)
    assert obj['Body'].read() == content


def test_s3_custom_metadata(s3_client):
    key = "test_dir/meta.txt"
    s3_client.put_object(Bucket=BUCKET, Key=key, Body=b"x",
                         Metadata={'owner': 'student', 'course': 'css4004'})
    meta = s3_client.head_object(Bucket=BUCKET, Key=key)['Metadata']
    assert meta == {'owner': 'student', 'course': 'css4004'}


def test_s3_prefix_listing(s3_client):
    for name in ("a.txt", "b.txt"):
        s3_client.put_object(Bucket=BUCKET, Key=f"prefix_test/{name}", Body=b"1")
    resp = s3_client.list_objects_v2(Bucket=BUCKET, Prefix="prefix_test/")
    keys = sorted(o['Key'] for o in resp['Contents'])
    assert keys == ["prefix_test/a.txt", "prefix_test/b.txt"]


def test_s3_overwrite_replaces_object(s3_client):
    key = "test_dir/overwrite.txt"
    s3_client.put_object(Bucket=BUCKET, Key=key, Body=b"v1")
    s3_client.put_object(Bucket=BUCKET, Key=key, Body=b"v2")
    assert s3_client.get_object(Bucket=BUCKET, Key=key)['Body'].read() == b"v2"


def test_s3_delete_object(s3_client):
    key = "test_dir/delete_me.txt"
    s3_client.put_object(Bucket=BUCKET, Key=key, Body=b"bye")
    s3_client.delete_object(Bucket=BUCKET, Key=key)
    with pytest.raises(ClientError):
        s3_client.head_object(Bucket=BUCKET, Key=key)
