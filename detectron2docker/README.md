Create Pose Coordinates and store as JSON File
```shell
mkdir /tmp/mountdir
# fetch the test video. This one has 3 seconds.
wget -O /tmp/mountdir/input.mp4 https://github.com/wenyaozhang-11/imge-share/raw/main/3053.MP4
# mount the directory and run the docker container
docker run -v /tmp/mountdir:/home/appuser/detectron2_repo/mountdir -it zwy8203302/detectron2cpu
# output contains a list of maps. Each frame in the video has a map in the list.
less /tmp/mountdir/video_output.json
```
To run bicep evaluation:
```shell
python evaluation_bicep.py /tmp/mountdir/video_output.json side
```
where side can take values either left or right

Once you run bicep evaluation, a percentage will be outputted showing the scale
  of how good/bad the form of the particular exercise is. 

Evaluate the exercise
1) Before running, unzip poses_compressed.zip
```shell
python evaluation_bicep.py video_output.json
```
or 
```shell
python evaluation_shoulderpress.py video_output.json
```
