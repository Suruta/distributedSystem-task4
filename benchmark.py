"""Task 4: read-latency comparison HDFS vs MinIO (run after docker-compose up)."""
import subprocess, time, os, tempfile
import s3_client as s3c

KEY, HDFS_PATH = 'data/sample_100m.bin', '/user/student/data/sample_100m.bin'

def time_hdfs_read():
    t = time.time()
    subprocess.run(['docker', 'exec', 'hdfs_namenode', 'hdfs', 'dfs', '-cat', HDFS_PATH],
                   stdout=subprocess.DEVNULL, check=True)
    return time.time() - t

def time_s3_read():
    out = tempfile.mktemp()
    t = s3c.download_object(KEY, out)
    os.remove(out)
    return t

if __name__ == '__main__':
    runs = 5
    h = [time_hdfs_read() for _ in range(runs)]
    s = [time_s3_read() for _ in range(runs)]
    print(f'HDFS avg read (100MB): {sum(h)/runs:.2f}s  runs={[round(x,2) for x in h]}')
    print(f'S3   avg read (100MB): {sum(s)/runs:.2f}s  runs={[round(x,2) for x in s]}')
