# myimagelib

myimagelib is a collection of image analysis code, including particle tracking, PIV, file manipulations and more. These code are initially just for my own convenience. As time goes on, they gradually become an integral part of my daily coding. When I share my code with friends, I always find it a problem when they cannot import in their local environment, and I have to ask them to download the code from my GitHub, or rewrite my code using packages that are already available on PyPI. This has been a PITA for a while, and I realize that it could be useful to make the code available on PyPI, too. So that my friends can download my code with a simple `pip install`. 

I understand that this package consists of code for many different purposes and they are not organized very nicely. It is only intended for people who are going to run my notebooks, but need the functions that I wrote earlier in this library. 

## Installation

```
pip install myimagelib
```

## Examples of use

```python
>>> from myimagelib.myImageLib import readdata
>>> readdata(".", "py")
```
The result is:
```
               Name                                                Dir
0          __init__  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
1           corrLib  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
2         corrTrack  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
3             deLib  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
4  fit_circle_utils  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
5           miscLib  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
6        myImageLib  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
7            pivLib  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
8       xcorr_funcs  C:\Users\liuzy\Miniconda3\envs\testpip\Lib\sit...
```



