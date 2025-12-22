# NAS Drive Mapping Reference

Standardized drive letters keep cloud mirrors predictable after Windows reinstalls or profile migrations. The
Windows NAS bootstrap scripts mount each network share with these assignments:

- **G:** → `\\nas\Cloud-GDrive` (Google Drive mirror)
- **I:** → `\\nas\Cloud-iCloud` (iCloud mirror)
- **O:** → `\\nas\Cloud-OneDrive` (OneDrive mirror)

Re-run the bootstrap or use these paths directly in File Explorer if drive letters need to be restored. The
mappings also serve as a portable reference when recreating shortcuts or validating rclone configuration.
