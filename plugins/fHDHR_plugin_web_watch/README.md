<p align="center">fHDHR web Plugin Watch    <img src="docs/images/logo.ico" alt="Logo"/></p>


Welcome to the world of streaming content as a DVR device! We use some fancy python here to achieve a system of:

**f**un
**H**ome
**D**istribution
**H**iatus
**R**ecreation

fHDHR is labeled as beta until we reach v1.0.0

Join us in `#fHDHR <irc://irc.freenode.net/#fHDHR>`_ on Freenode.

# Installation

1) Review Installation guide located at [Docs](https://github.com/fHDHR/fHDHR/blob/main/docs/README.md)

2) Insert this plugin into the `plugins` directory of fHDHR using `git clone` or downloading a release zip file.

3) Adjust your configuration file with the below settings:

````
[webwatch]
# ffmpeg_path =
````


# Developer Note

This plugin Orerwrites the normal Guide page, includes all original functionality, but also provides a method to stream content in the browser.

This was made as a plugin, instead of being included in core, due to its dependency on ffmpeg.