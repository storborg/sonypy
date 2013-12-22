import requests
import json
import struct


class CameraError(Exception):

    def __init__(self, code, s):
        self.code = code
        self.s = s

    def __repr__(self):
        return '<%s %d: %s>' % (self.__class__.__name__, self.code, self.s)


class RawCamera(object):
    """
    A camera control object which only implements raw API commands, and does
    not provide any control layer on top of the API.
    """
    version = "1.0"

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def _do_request(self, method, *args):
        body = dict(method=method,
                    params=args,
                    id=1,
                    version=self.version)
        data = json.dumps(body)
        r = requests.post(self.endpoint, data=data)
        resp = r.json
        assert resp['id'] == 1
        error = resp.get('error')
        if error:
            self._handle_error(error)
        else:
            return resp['results']

    def _handle_error(self, error):
        raise CameraError(*error)

    def set_shoot_mode(self, mode):
        """
        Set the shooting mode. Can be one of 'still', 'movie', or 'audio'.
        """
        valid_modes = ('still', 'movie', 'audio')
        if mode not in valid_modes:
            raise ValueError('mode must be one of %r' % valid_modes)
        result = self._do_request('setShootMode', mode)
        assert result == [0], "unexpected result"

    def get_shoot_mode(self):
        """
        Get the shooting mode. Will be one of 'still', 'movie', or 'audio'.
        """
        result = self._do_request('getShootMode')
        mode = result[0]
        return mode

    def get_supported_shoot_mode(self):
        """
        Get a list of supported shooting modes.
        """
        result = self._do_request('getSuppoedShootMode')
        return result[0]

    def get_available_shoot_mode(self):
        """
        Get a list of available shooting modes at the moment.
        """
        result = self._do_request('getAvailableShootMode')
        return result[0]

    def act_take_picture(self):
        """
        Take a picture. Returns a list of URLs for postview of JPGs.
        """
        result = self._do_request('actTakePicture')
        return result[0]

    def await_take_picture(self):
        """
        Await the camera taking a picture. Returns a list of URLs for
        postview of JPGs.
        """
        result = self._do_request('awaitTakePicture')
        return result[0]

    def start_movie_rec(self):
        """
        Start movie recording. Returns None.
        """
        result = self._do_request('startMovieRec')
        assert result == [0], "unexpected result"

    def stop_movie_rec(self):
        """
        Stop movie recording. Returns a list of URLs for postview thumbnails.
        """
        result = self._do_request('stopMovieRec')
        return result[0]

    def start_audio_rec(self):
        """
        Start audio recording. Returns None.
        """
        result = self._do_request('startAudioRec')
        assert result == [0]

    def stop_audio_rec(self):
        """
        Stop audio recording. Returns None.
        """
        result = self._do_request('stopAudioRec')
        assert result == [0]

    def start_liveview(self):
        """
        Start liveview stream. Returns the liveview stream URL.
        """
        result = self._do_request('startLiveview')
        return result[0]

    def stop_liveview(self):
        """
        Stop liveview stream.
        """
        result = self._do_request('stopLiveView')
        assert result == [0]

    def act_zoom(self, direction, movement):
        """
        Start zoom movement. Parameters are:

            direction - either "in" or "out"
            movement - can be "start", "stop", or "1shot".
        """
        result = self._do_request('actZoom', direction, movement)
        assert result == [0]

    def set_self_timer(self, delay):
        """
        Set self-timer delay in seconds. Must be one of the supported values,
        as returned by .get_supported_self_timer().
        """
        result = self._do_request('setSelfTimer', delay)
        assert result == [0]

    def get_self_timer(self):
        """
        Get the current self-timer delay.
        """
        result = self._do_request('getSelfTimer')
        return result[0]

    def get_supported_self_timer(self):
        """
        Get supported self-timer settings.
        """
        result = self._do_request('getSupportedSelfTimer')
        return result[0]

    def get_available_self_timer(self):
        """
        Get the current self-timer setting and the available self-timer
        settings. Returns a tuple of (current setting, list of available
        settings).
        """
        result = self._do_request('getAvailableSelfTimer')
        return result[0]

    def set_postview_image_size(self, size):
        """
        Set the postview image size. Note that the parameter is actually a
        named size (as a string) rather than any kind of numeric dimension.
        """
        result = self._do_request('setPostViewImageSize', size)
        assert result == [0]

    def get_postview_image_size(self):
        """
        Get currently avtive postview image size.
        """
        result = self._do_request('getPostviewImageSize')
        return result[0]

    def get_supported_postview_image_size(self):
        """
        Get list of supported postview image sizes.
        """
        result = self._do_request('getSupportedPostviewImageSize')
        return result[0]

    def get_available_postview_image_size(self):
        """
        Get the current postview image size setting and the available postview
        image sizes. Returns a tuple of (current setting, list of available
        settings).
        """
        return self._do_request('getAvailablePostviewImageSize')

    def get_event(self, long_poll):
        """
        This method is a mechanism to get asynchronous updates from the camera.
        When used with long_poll=True, it will block until a camera event
        occurs, and then return state data. When used with long_poll=False, it
        will return immediately with state data, for synchronous use.

        Most likely, it's desirable to wrap this function for consumption by a
        higher-level program.

        The structure of the return value of this method is fairly involved,
        see docs for more info.
        """
        return self._do_request('getEvent', long_poll)

    def start_rec_mode(self):
        """
        Initializes the camera for remote shooting.

        From the docs:
        "Some camera models need this API call before starting liveview,
        capturing still image, recording movie, or accessing all other camera
        remote shooting functions."
        """
        result = self._do_request('startRecMode')
        assert result == [0]

    def stop_rec_mode(self):
        """
        Stop remote shooting functions.
        """
        result = self._do_request('stopRecMode')
        assert result == [0]

    def get_available_api_list(self):
        """
        Get a list of available API names.
        """
        return self._do_request('getAvailableApiList')

    def get_application_info(self):
        """
        Get the name and camera remote API version.
        """
        return self._do_request('getApplicationInfo')

    def get_versions(self):
        """
        Get supported versions of the API service. As of the time of this
        writing, this will probably just be "1.0" on all cameras.
        """
        return self._do_request('getVersions')

    def get_method_types(self):
        """
        Get supported APIs for this version. This differs from
        .get_available_api_list() in that it includes parameter and version
        information with each method name.
        """
        return self._do_request('getMethodTypes')

    def _decode_common_header(self, buf):
        start, ptype, seq, timestamp = struct.unpack('BBHI', buf)
        return seq, timestamp

    def _decode_payload_header(self, buf):
        format = 'IBBBBIB'
        buf = buf[:struct.calcsize(format)]
        d = struct.unpack(format, buf)
        start = d[0]
        assert start == '\x24\x35\x68\x79', "payload start mismatch"
        jpeg_size = struct.pack('I', [0] + d[1])
        padding_size = d[2]
        return jpeg_size, padding_size

    def stream_liveview(self, url):
        """
        Connect to a liveview-format URL and yield a series of JPEG frames.
        """
        r = requests.get(url)
        while True:
            # Read common header, 8 bytes.
            seq, timestamp = self._decode_common_header(r.raw.read(8))
            # Read payload header, 128 bytes.
            jpeg_size, padding_size = \
                self._decode_payload_header(r.raw.read(128))
            # Read JPEG frame.
            jpeg_frame = r.raw.read(jpeg_size)
            # Throw away the padding.
            r.raw.read(padding_size)
            yield jpeg_frame


class Camera(RawCamera):

    def get_event_mapped(self, long_poll):
        """
        Wraps the getEvent call to parse the result and make it possible to
        look up values diretly. Specifically:

        The raw result value is a list of dict, where each dict includes a
        'type' key. Rearrange the list into a dict, where each top-level key
        remaps to a dict based on it's type value.
        """
        result = self.get_event(long_poll)
        return {obj['type']: obj for obj in result}

    def tether(self):
        """
        Begin a rudimentary "tether mode" by returning a generator which yields
        the liveview data for each new photo that is taken.
        """
        while True:
            liveview_url = self.await_take_picture()
            r = requests.get(liveview_url)
            yield r.body
