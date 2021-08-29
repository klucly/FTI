# FTI
File To Image converter. Converts any combination of bytes into the image. I didn't make decoder btw

`__init__.py` can be runned manually.

To convert bytes into image use *fast_image*:

`fast_image (obj: bytes, mode = "linear", channels = 3, encoder_more = "RGB") -> Image`

There are 3 modes:
* linear
* channel
* single
