SonyPy - Implements the Sony Camera Remote API
==============================================

Scott Torborg - `Cart Logic <http://www.cartlogic.com>`_


Installation
============

Install with pip::

    $ pip install sonypy


Quick Start
===========

1. Install ``sonypy``.
2. Enable remote control over Wifi on your camera.
3. Connect your computer to the wifi network hosted by the camera.
4. Open a Python shell.

Now you can start playing::

    >>> from sonypy import Discoverer, Camera

First try to connect to a camera::

    >>> discoverer = Discoverer()
    >>> cameras = discoverer.discover()
    >>> cameras
    [<Camera ...>, <Camera ...>]

Take a shot with current settings::

    >>> cam = cameras[0]
    >>> cam.act_take_picture()


License
=======

SonyPy is licensed under an MIT license. Please see the LICENSE file for more
information.
