# MotionPhoto2

A small script to create Motion Photo v2/v3 from HEIC or JPG files and videos. Resulting files appear to be compatible with Google Photos and Samsung Gallery as a motion/live photo.

In case the source is an iPhone Live Photo, the presentation timestamp will be migrated as well, thus the photo will start from the same keyframe.

Photos are created to mimic the way Galaxy S23 Ultra and Tab S9 phones create HEIC and JPG motion photos. This format internally refers to itself as mpv2 (and recently also mpv3), thus the name of this script.

![GUI Screenshot](documentation/images/GUI.png?raw=true "GUI")

## Installation

### Windows

Please install ExifTool so that it is added to your path. The easiest is to use [installer by Oliver Betz](https://oliverbetz.de/pages/Artikel/ExifTool-for-Windows). Use the file "ExifTool_install_nn.nn_64.exe" and accept all defaults.

Then download the Windows release and enjoy!

### Unix and MacOS

The script requires [ExifTool](https://exiftool.org/) and [Python 3.7+](https://www.python.org/) on your computer. Both Python and ExifTool should be in your package managers or installed already, please install them if you did not yet.

Once you have Python and ExifTool installed on your OS, navigate to the script's directory and run following command to download script's dependencies

```
> pip install -r requirements.txt
```

## Usage

Just run the script! If you run it without parameters, it'll present a GUI with explanations. Alternatively, you can use it using commandline as per below examples.

### Individual photos

To convert image and video pair to Motion Photo v2, run:

```
> motionphoto2 --input-image ImageFile.HEIC --input-video VideoFile.MP4
```

### Directory mode

The script will automatically search file in directory that have the same name but different extension, for example: IMG_1496.HEIC, IMG_1496.MP4

```
> motionphoto2 --input-directory /your/directory
```

### Notes

- The output of new images file will be: original_name.**LIVE**.ext
- If you want to process recursively all subdirectories use: `--recursive`
- If you provide a `--output-directory` the file will be: **output-directory**/original_name.ext
- While the script muxes the image and video two temp files will be created and deleted automatically, you can keep it with `--keep-temp`
- If you want to replace the original image file with the live one use: `--overwrite` (use at your risk)
- If you want to remove the video file after muxing use: `--delete-video` (use at your risk)

## Limitations

If the source image is an Apple HDR HEIC image, Google Photos will say that the resulting photo is not HDR. This is not true - if you save the photo back to iPhone camera roll, you'll see the photo is HDR.

Google Photos _will_ actually show it too, but only when it is stored in local photos on an iPhone/iPad.

The reason is probably directly related to Motion Photos - the same place where Motion Photos are defined (in XMP object GCamera - `http://ns.google.com/photos/1.0/camera/`) is also the place where Google/Android stores JPEG/R HDR information.

It appears that the server-side processing of Google Photos does not check for Apple HDR once it finds Google Camera header in XMP tags. For JPG files, a conversion is possible by adjusting metadata and is on the roadmap. Unfortunately there is no support for Gainmap HDR HEIF images in libultrahdr or any modern Android devices at the moment.

Hopefully, as Gainmap HDR matures, both Google and Apple will converge on ISO/CD 21496-1 and things will just start working. On Apple side this has happened already - as of iOS18 RC on iPhone 15(pro), iOS stores HDR in ISO "urn:iso:std:iso:ts:21496:-1" format for both JPG and HEIF. Unfortunately iPhones 12-14 are stuck with Apple Gainmaps (for JPGs, it should be possible to remux them to ISO format, though). On Google side keep an eye on [libultrahdr](https://github.com/google/libultrahdr) used in Android and also most likely in GPhotos backend. It currently only supports JPEG/R, but HEIC support [is on the way](https://github.com/google/libultrahdr/issues/195).

## Credits

Huge thanks to [@Tkd-Alex](https://github.com/Tkd-Alex) for porting the original PowerShell script to Python. It is now much faster and easier to adjust to boot.

Thanks to [@tribut](https://github.com/tribut), [@Tkd-Alex](https://github.com/Tkd-Alex), [@4Urban](https://github.com/4Urban), [@IamRysing](https://github.com/IamRysing) and [@NightMean](https://github.com/NightMean) for providing sample Motion Photo pictures (check them out [here](https://github.com/PetrVys/MotionPhotoSamples))

#### Documentation

Google official documentation of the format

- https://developer.android.com/media/platform/motion-photo-format

Samsung trailer tags are well explained in doodspav's repo

- https://github.com/doodspav/motionphoto

HEIC muxing is similar to doodspav's work, but additionally uses MP4 top-level boxes "mpvd" and "sefd" to add the MP data into heic and mp4 in standard-compliant way (see source in this repo).
