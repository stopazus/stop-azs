# NAS Drive Mapping Reference

Investigation workstations map common cloud storage providers to consistent drive letters. Use these UNC paths to reconnect the network shares after OS reinstalls or profile migrations.

| Drive letter | UNC path | Notes |
| --- | --- | --- |
| G: | \\\\nas\\Cloud-GDrive | Google Drive |
| I: | \\\\nas\\Cloud-iCloud | iCloud |
| O: | \\\\nas\\Cloud-OneDrive | OneDrive |

Add shortcuts or reconnect the drives using these mappings so tools and scripts referencing the standard letters continue to function.
