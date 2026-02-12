# Performance and Filesystem Optimizations

## Why Filesystem Performance Matters

KLara scans large virus collections using Yara rules. Scan speed is directly limited by how fast the filesystem can read files. Optimizing storage hardware and filesystem configuration can dramatically improve throughput.

## Recommended Hardware: SSD RAID Arrays

From production experience, storing file repositories on multiple SSDs in a RAID configuration provides the best performance.

### Benchmarks (8× Samsung SSDs)

| Configuration | Throughput | Trade-off |
|--------------|------------|-----------|
| RAID 5 | ~3.0 GB/s | Tolerates 1 disk failure |
| RAID 0 | ~3.5 GB/s (+20%) | No fault tolerance — one disk failure loses the entire array |

> **Recommendation**: RAID 5 offers a good balance of speed and reliability. RAID 6 provides tolerance for up to 2 disk failures at a slight performance cost.

## Recommended Filesystem: XFS

[XFS](https://en.wikipedia.org/wiki/XFS) provides the best performance for KLara workloads. ReiserFS also performs reasonably well.

### Creating the Filesystem

For an 8× SSD RAID 5 array (7 data drives + 1 parity):

```bash
mkfs.xfs -f -d su=256k,sw=7,agcount=24 -l version=2,su=256 -i size=512 <target_device>
```

### Mount Options

```bash
mount -o noatime,nodiratime,nobarrier,largeio,inode64,swalloc,logbufs=8,logbsize=256k,allocsize=131072k <target_device> <target_dir>
```

Key options explained:

| Option | Purpose |
|--------|---------|
| `noatime,nodiratime` | Disables access time updates, reducing write overhead |
| `nobarrier` | Disables write barriers (safe with battery-backed RAID controllers) |
| `largeio` | Optimizes for large sequential I/O operations |
| `inode64` | Allows inodes across the entire filesystem |
| `swalloc` | Aligns allocations to stripe width |
| `logbufs=8,logbsize=256k` | Increases journal buffer size for throughput |
| `allocsize=131072k` | Sets large preallocation size for sequential writes |

