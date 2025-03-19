

for using face detection module use the below code 

```
from lipsync_seisei.face_det import extract_faces


extract_faces(
    face_path= "path/to/the/input/video",
    output_dir='path/to/output/folder',
)

```

for lipsync video generation using the face detection results 

```
from lipsync_seisei.video_gen import run_lipsync

run_lipsync(
    checkpoint_path="path/to/the/checkpoint",
    metadata_path="path/to/metadata/file",
    audio_dir= "path/to/the/audio/folder",
    output_dir="path/to/output/folder",
)

```