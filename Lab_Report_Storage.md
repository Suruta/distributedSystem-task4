# Lab 8-9 Report: HDFS vs S3 (MinIO)
**Name:** ________  **Course:** CSS4004

## Section 1: HDFS
Commands used:
```
docker-compose up -d
docker exec -it hdfs_namenode hdfs dfs -mkdir -p /user/student/data
docker exec -it hdfs_namenode dd if=/dev/urandom of=sample_100m.bin bs=1M count=100
docker exec -it hdfs_namenode hdfs dfs -put sample_100m.bin /user/student/data/
docker exec -it hdfs_namenode hdfs fsck /user/student/data/sample_100m.bin -files -blocks -locations
```
- [Screenshot: http://localhost:9870 showing 2 live DataNodes]
- [Screenshot: fsck output showing 1 block, 2 replicas]

Expected: 100 MB < 128 MB block size, so the file is **1 block** with **2 replicas** (one per DataNode).

## Section 2: MinIO
Run `python s3_client.py`, then:
- [Screenshot: http://localhost:9002 (minioadmin / minioadminpassword) showing `data/sample_100m.bin` and its metadata `owner`, `course`]

## Section 3: Fault injection
```
docker stop hdfs_datanode1
docker exec hdfs_namenode hdfs dfsadmin -report
docker exec hdfs_namenode hdfs fsck /user/student/data/sample_100m.bin
```
- [Paste logs / screenshot of Web UI]

Expected observation: after the NameNode heartbeat timeout (~10.5 min by default; Web UI shows the node as "Dead"), the file is **Under-Replicated** (1 of 2 replicas). It does **not** self-heal here because only one DataNode remains, so there is no second target. Data stays readable. After `docker start hdfs_datanode1`, the block report restores replication to 2/2.

## Section 4: Comparison
| Attribute | HDFS (Block) | S3 / MinIO (Object) |
|---|---|---|
| Storage hierarchy | POSIX-like directory tree | Flat namespace (bucket + keys; "/" is only a prefix convention) |
| Modification pattern | Append-only, single writer | Immutable objects; overwrite via full PUT |
| Unit size | Fixed blocks (128/256 MB) | Arbitrary objects (0 B to 5 TB) |
| Metadata management | NameNode in-memory namespace | Per-object metadata + key index; HEAD returns it |
| Fault tolerance | Block replication (N=2 here) | Erasure coding / replication |
| Access | HDFS RPC / CLI | REST API (boto3) |

Measured read latency (`python benchmark.py`, 100 MB, 5 runs):
| System | Avg read time |
|---|---|
| HDFS | ____ s |
| MinIO | ____ s |

Discussion: HDFS has data locality and is built for large sequential analytics; the NameNode is a metadata bottleneck. S3 scales via a flat key-value model and simple HTTP access, but has no in-place edits. Overwrites are atomic per key.
