# vbumper

A comprehensive version management tool for Python projects.

It handles version bumping in a wide variety of formats, including pre-releases, development versions, and Git operations following PEP 440. It supports major.minor.patch versioning, with pre-release and post-release versions including dev, alpha, beta, rc, and post.

## Usage

```python
# Regular version bumping
vbumper                # 1.2.3    -> 1.2.4
vbumper minor          # 1.2.3    -> 1.3.0
vbumper major          # 1.2.3    -> 2.0.0

# Pre-release versions
vbumper dev            # 1.2.3    -> 1.2.4.dev0
vbumper alpha          # 1.2.3    -> 1.2.4a1
vbumper beta           # 1.2.4a1  -> 1.2.4b1
vbumper rc             # 1.2.4b1  -> 1.2.4rc1
vbumper patch          # 1.2.4rc1 -> 1.2.4

# Post-release version
vbumper post           # 1.2.4    -> 1.2.4.post1
```

All operations also include Git tagging and pushing changes to remote repository.
