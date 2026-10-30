#!/usr/bin/env python3
"""Upload a video to Zernio's own storage (the route that works for Instagram).

  1. Zernio: call_tool media_get_media_presigned_url {"filename": "<name>.mp4", "content_type": "video/mp4", "size": <bytes>}
  2. python3 studio/tools/zernio_upload.py '<uploadUrl>' <file.mp4>      -> "upload status 200"
  3. Use the returned publicUrl (https://media.zernio.com/temp/...) in posts_create / posts_update_post media_items.
     Creating or updating the post copies the file to permanent storage, so posts can be scheduled weeks ahead.
     Unused uploads expire after 7 days. The upload URL expires 1 hour after it is issued.

  python3 studio/tools/zernio_upload.py size <file.mp4>                  -> byte size for step 1
"""
import os, sys, urllib.request

if len(sys.argv) == 3 and sys.argv[1] == "size":
    print(os.path.getsize(sys.argv[2])); sys.exit()
if len(sys.argv) != 3:
    sys.exit(__doc__)
url, path = sys.argv[1], sys.argv[2]
data = open(path, "rb").read()
req = urllib.request.Request(url, data=data, method="PUT", headers={"Content-Type": "video/mp4"})
with urllib.request.urlopen(req, timeout=300) as r:
    print("upload status", r.status, f"{len(data)/1e6:.1f} MB")
