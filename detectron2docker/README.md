```shell
mkdir /tmp/mountdir
# fetch the test video. This one has 3 seconds.
wget -O /tmp/mountdir/input.mp4 https://github.com/wenyaozhang-11/imge-share/raw/main/3053.MP4
# mount the directory and run the docker container
docker run -v /tmp/mountdir:/home/appuser/detectron2_repo/mountdir -it zwy8203302/detectron2cpu
# output contains a list of maps. Each frame in the video has a map in the list.
less /tmp/mountdir/video_output.json
```

