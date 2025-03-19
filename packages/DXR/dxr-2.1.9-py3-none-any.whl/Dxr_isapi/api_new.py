"""
hikvision.api
~~~~~~~~~~~~~~~~~~~~

Provides methods for interacting with hikvision

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""

import logging
from xml.etree import ElementTree
import re

import requests
from requests.exceptions import ConnectionError as ReConnError
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from .error import HikvisionError, MissingParamError
from .constants import DEFAULT_PORT, DEFAULT_HEADERS, XML_ENCODING
from .constants import DEFAULT_SENS_LEVEL

_LOGGING = logging.getLogger(__name__)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes


def build_url_base(host, port, is_https):
    """
    Make base of url based on config
    """
    base = "http"
    if is_https:
        base += 's'

    base += "://"
    base += host

    if port:
        base += ":"
        base += str(port)

    return base


def log_response_errors(response):
    """
    Logs problems in a response
    """

    _LOGGING.error("status_code %s", response.status_code)


def enable_logging():
    """ Setup the logging for home assistant. """
    logging.basicConfig(level=logging.INFO)


def remove_namespace(response):
    """ Removes namespace element from xml"""
    return re.sub(' xmlns="[^"]+"', '', response)


def tree_no_ns_from_string(response):
    """ Removes namespace element from response"""
    text = remove_namespace(response)
    return ElementTree.fromstring(text)


class CreateDevice:
    """
    Creates a new camera api device
    """

    def __init__(self, host=None, port=DEFAULT_PORT,
                 username=None, password=None, is_https=False,
                 sensitivity_level=DEFAULT_SENS_LEVEL,
                 digest_auth=True, strict_isapi=True, channel=1):
        enable_logging()
        # _LOGGING.info("Initialising new hikvision camera client")

        if not host:
            # _LOGGING.error('Missing hikvision host!')
            raise MissingParamError('Connection to hikvision failed.', None)

        if not digest_auth and not is_https:
            # _LOGGING.warning("%s: HTTP Basic Auth without SSL is insecure",
            #                  host)
            pass

        self._username = username
        self._host = host
        self._password = password
        self._sensitivity_level = sensitivity_level
        self._digest_auth = digest_auth
        self._strict_isapi = strict_isapi
        self._auth_fn = HTTPDigestAuth if self._digest_auth else HTTPBasicAuth
        self.xml_motion_detection_off = None
        self.xml_motion_detection_on = None
        self.channel = str(channel)

        # Now build base url
        self._base = build_url_base(host, port, is_https)

        # need to support different channel
        if self._strict_isapi:
            self.all_capabilities_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/capabilities"
            self.motion_url = f"{self._base}/ISAPI/System/Video/Inputs/channels/{self.channel}/motionDetection"
            self.deviceinfo_url = f"{self._base}/ISAPI/System/deviceInfo"
            self.ptzctrl_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/continuous"
            self.ptzpreset_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/presets"
            self.pic_url = f"{self._base}/ISAPI/Streaming/channels/{self.channel}/picture"
            self.ptz_senior_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/absoluteExt"
            self.set_preset_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/presets"
            self.ptzfocus_url = f"{self._base}/ISAPI/System/Video/inputs/channels/{self.channel}/focus"
            self.capabilities_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/absoluteEx/capabilities"
            self.ptz_absoluteEx_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/absoluteEx"
            self.onepushfocus_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/onepushfoucs/start"
            self.imageFocus_url = f"{self._base}/ISAPI/Image/channels/{self.channel}/focusConfiguration"
            self.ptz_capabilities_url = f"{self._base}/ISAPI/PTZCtrl/capabilities"
            self.ptz_autopan_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/autopan"
            self.streamParam_url = f"{self._base}/ISAPI/Thermal/channels/{self.channel}/streamParam"
            self.auxcontrol_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/auxcontrols/1"
            self.set_auxcontrol_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/auxcontrols/1"
            self.get_auxcontrol_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/auxcontrols"
            self.wdr_url = f"{self._base}/ISAPI/Image/channels/{self.channel}/WDR"
            self.thermometry_basic_url = f"{self._base}/ISAPI/Thermal/channels/{self.channel}/thermometry/basicParam"
            self.stream_set_url = f"{self._base}/ISAPI/Streaming/channels/"
            self.status_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/status"
            self.set_absolute_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/absolute"
            self.get_common_url = f"{self._base}/ISAPI/Image/channels/{self.channel}?parameterType=recommendation"
            self.set_position3d_url = f"{self._base}/ISAPI/PTZCtrl/channels/{self.channel}/position3D"
            self.ir_url = f"{self._base}/ISAPI/Thermal/channels/{self.channel}/thermometry/jpegPicWithAppendData?format=json"
        else:
            self.motion_url = '%s/MotionDetection/1' % self._base
            self.deviceinfo_url = '%s/System/deviceInfo' % self._base
            self.ptzctrl_url = '%s/PTZCtrl/capabilities' % self._base
            self.ptzpreset_url = '%s/PTZCtrl/channels/1/presets' % self._base
            self.pic_url = '%s/System/Video/channels/1/picture' % self._base
            self.rtsp_url = '%s/Streaming/channels/1' % self._base
            self.ptz_senior_url = '%s/PTZCtrl/channels/1/absoluteExt' % self._base
            self.ir_url = '%s/Thermal/channels/2/thermometry/pixelToPixelParam/capabilities?format=json' % self._base
        #            self._xml_namespace = "{http://www.hikvision.com/ver10/XMLSchema}"
        self._xml_namespace = ""

    #   获取设备信息
    def get_all_capabilities(self, element_to_query=None):
        response = requests.get(
            self.all_capabilities_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            # print(response.text)
            # 返回的是json格式的数据，返回的是一个字典
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:

            return None
        return None

    def get_common(self):
        print(self.get_common_url)
        response = requests.get(
            self.get_common_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return response.text

        return response.text

    def get_absolute_capabilities(self):
        response = requests.get(
            self.status_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return response.text

        return response.text

    def set_absolute(self, elevation, azimuth, absoluteZoom):
        data_xml = '<?xml version="1.0" encoding="UTF-8"?>' + \
                   '<PTZData xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">' + \
                   '<AbsoluteHigh>' + \
                   '<elevation>' + str(elevation) + '</elevation>' + \
                   '<azimuth>' + str(azimuth) + '</azimuth>' + \
                   '<absoluteZoom>' + str(absoluteZoom) + '</absoluteZoom>' + \
                   '</AbsoluteHigh>' + \
                   '</PTZData>'
        # 转换为UTF-8编码
        data_xml = data_xml.encode('utf-8')
        # print(data_xml)
        response = requests.put(
            self.set_absolute_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            print('http code:', response.status_code)
            print('response:', response.text)
            # log_response_errors(response)
            return None

        return response.text

    def set_position3d(self, StartPoint_x, StartPoint_y, EndPoint_x=None, EndPoint_y=None):
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?><position3D><StartPoint><positionX>{StartPoint_x}</positionX><positionY>{StartPoint_y}</positionY></StartPoint><EndPoint><positionX>{EndPoint_x}</positionX><positionY>{EndPoint_y}</positionY></EndPoint></position3D>'
        # 转换为UTF-8编码
        # data_xml = data_xml.encode('utf-8')
        if EndPoint_x is None and EndPoint_y is None:
            EndPoint_x = StartPoint_x
            EndPoint_y = StartPoint_y
        data_xml = data_xml.format(StartPoint_x=StartPoint_x, StartPoint_y=StartPoint_y, EndPoint_x=EndPoint_x,
                                   EndPoint_y=EndPoint_y)
        # print(data_xml)
        response = requests.put(
            self.set_position3d_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            print('http code:', response.status_code)
            print('response:', response.text)
            # log_response_errors(response)
            return None
        return response.text

    def get_ptz_capabilities(self, element_to_query=None):
        response = requests.get(
            self.ptz_capabilities_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            # print(response.text)
            # 返回的是json格式的数据，返回的是一个字典
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:

            return None
        return None

    def get_absolutestatus(self, element_to_query=None):
        # print(self.ptz_absoluteEx_url)
        response = requests.get(
            self.ptz_absoluteEx_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return response.text

        if element_to_query is None:
            # print(response.text)
            # 返回的是json格式的数据，返回的是一个字典
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:
            return None
        return None

    def set_ptzabsoluteEx(self, elevation, azimuth, absoluteZoom, focus, focalLen, horizontalSpeed=10.00,
                          verticalSpeed=10.00, zoomType='absoluteZoom', element_to_query=None):
        data_xml = '<?xml version="1.0" encoding="UTF-8"?>' + \
                   '<PTZAbsoluteEx version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">' + \
                   '<elevation>' + str(elevation) + '</elevation>' + \
                   '<azimuth>' + str(azimuth) + '</azimuth>' + \
                   '<absoluteZoom>' + str(absoluteZoom) + '</absoluteZoom>' + \
                   '<focus>' + str(focus) + '</focus>' + \
                   '<focalLen>' + str(focalLen) + '</focalLen>' + \
                   '<horizontalSpeed>' + str(horizontalSpeed) + '</horizontalSpeed>' + \
                   '<verticalSpeed>' + str(verticalSpeed) + '</verticalSpeed>' + \
                   '<zoomType>' + str(zoomType) + '</zoomType>' + \
                   '</PTZAbsoluteEx>'
        # 转换为UTF-8编码
        data_xml = data_xml.encode('utf-8')
        # print(data_xml)
        response = requests.put(
            self.ptz_absoluteEx_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            print('http code:', response.status_code)
            print('response:', response.text)
            # log_response_errors(response)
            return None

        if element_to_query is None:
            # print(response.status_code)
            # print(response.text)
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    def set_onepushfocus(self, element_to_query=None):
        response = requests.put(
            self.onepushfocus_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return response.text

        if element_to_query is None:
            # 返回的是json格式的数据，返回的是一个字典
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:

            return None
        return None

    def set_auopan(self, autoPan=0, element_to_query=None):
        autoPan = 15 * autoPan
        data_xml = '<?xml version="1.0" encoding="UTF-8"?><autoPanData><autoPan>' + str(
            autoPan) + '</autoPan></autoPanData> '
        # 转换为UTF-8编码
        data_xml = data_xml.encode('utf-8')
        # print(data_xml)
        response = requests.put(
            self.ptz_autopan_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            print('http code:', response.status_code)
            print('response:', response.text)
            # log_response_errors(response)
            return None

        if element_to_query is None:
            # print(response.text)
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    def ir_test(self, element_to_query=None):
        response = requests.get(
            self.ir_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            log_response_errors(response)
            return None

        if element_to_query is None:
            # 返回的是json格式的数据，返回的是一个字典
            return response.json()
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:

            return None
        return None

    def get_pic(self, element_to_query=None):
        response = requests.get(
            self.pic_url,
            auth=self._auth_fn(self._username, self._password),
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:

            return None
        return None

    def set_preset(self, preset_number: int, element_to_query=None):
        set_p_url = self.set_preset_url + '/' + str(preset_number)
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?>' + \
                   '<PTZPreset xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">' + \
                   '<id>' + str(preset_number) + '</id>' + \
                   '<presetName>预置点 ' + str(preset_number) + '</presetName>' + \
                   '</PTZPreset>'
        # 转换为UTF-8编码
        data_xml = data_xml.encode('utf-8')
        response = requests.put(
            set_p_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            print('something wrong', response)
            # log_response_errors(response)
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    def goto_preset(self, preset_number: int, element_to_query=None):
        ptz_preset_url = self.ptzpreset_url + '/' + str(preset_number) + '/goto'
        response = requests.put(
            ptz_preset_url,
            auth=self._auth_fn(self._username, self._password),
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()

        except AttributeError as attib_err:
            return None
        return None

    def delete_preset(self, preset_number: int, element_to_query=None):
        ptz_preset_url = self.ptzpreset_url + \
                         '/' + str(preset_number)
        response = requests.delete(
            ptz_preset_url,
            auth=self._auth_fn(self._username, self._password),
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()

        except AttributeError as attib_err:

            return None
        return None

    # 聚焦控制 0-停止 1-聚焦+ -1-聚焦-
    def ptz_focus(self, add_sub=0, element_to_query=None):
        focus = 15 * add_sub
        if focus > 100:
            focus = 100
        elif focus < -100:
            focus = -100
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?><FocusData><focus>' + str(focus) + '</focus></FocusData>'
        response = requests.put(
            self.ptzfocus_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            print(response)
            return response.text

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()

        except AttributeError as attib_err:
            return None
        return None

    def ptz_senior(self, element_to_query=None):
        data_xml = '<?xml version="1.0" encoding="UTF-8"?>' + \
                   '<PTZAbsoluteEx xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">' + \
                   '<elevation>0.000</elevation>' + \
                   '<azimuth>0.000</azimuth>' + \
                   '<absoluteZoom>0</absoluteZoom>' + \
                   '<focus>1</focus>' + \
                   '<focalLen>1</focalLen>' + \
                   '<horizontalSpeed>0.00</horizontalSpeed>' + \
                   '<verticalSpeed>0.00</verticalSpeed>' + \
                   '<zoomType>%s</zoomType>' + \
                   '</PTZAbsoluteEx>'
        response = requests.get(
            self.ptz_senior_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            log_response_errors(response)
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()

        except AttributeError as attib_err:
            return None
        return None

    # 设置图像参数,聚焦模式,聚焦限制 focusStyle: SEMIAUTOMATIC 半自动, MANUAL 手动, AUTO 自动，focusLimited: 聚焦限制 int, [10#10厘米,50#50厘米,100#1米,150#1.5米,300#3米,600#6米,1000#10米,2000#20米,5000#50米,20000#200米,50000#500米,65535#655.35米]
    def set_image_capabilities(self, focusStyle='SEMIAUTOMATIC', focusLimited=10, element_to_query=None):
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?>' + \
                   '<FocusConfiguration>' + \
                   '<focusStyle>' + str(focusStyle) + '</focusStyle>' + \
                   '<focusLimited>' + str(focusLimited) + '</focusLimited>' + \
                   '</FocusConfiguration>'

        response = requests.put(
            self.imageFocus_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            print(response)
            return response.text

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()

        except AttributeError as attib_err:
            return None
        return None

    def set_ptz(self, element_to_query=None, up_down=0, left_right=0, zoom=0):
        pan = left_right * 15
        tilt = -up_down * 15
        zoom_ = zoom * 15
        # 最大值为正负100
        if pan > 100:
            pan = 100
        if pan < -100:
            pan = -100
        if tilt > 100:
            tilt = 100
        if tilt < -100:
            tilt = -100
        if zoom_ > 100:
            zoom_ = 100
        if zoom_ < -100:
            zoom_ = -100

        data_xml = '<?xml version: "1.0" encoding="UTF-8"?><PTZData><pan>%s</pan><tilt>%s</tilt><zoom>%s</zoom></PTZData>' % (
            pan, tilt, zoom_)
        response = requests.put(
            self.ptzctrl_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    def get_streamParam(self, element_to_query=None):
        response = requests.get(
            self.streamParam_url,
            auth=self._auth_fn(self._username, self._password),
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:

            return None
        return None

    # 配置指定通道热成像码流参数 videoCodingType:thermal_raw_data#热成像裸数据,pixel-to-pixel_thermometry_data#全屏测温数据,real-time_raw_data#实时裸数据,spectrogramData#科学仪器谱图数据（包括检测物质中的光谱波长与能量值）
    def set_streamParam(self, element_to_query=None, videoCodingType='pixel-to-pixel_thermometry_data'):
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?><ThermalStreamParam xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">' + \
                   '<videoCodingType>' + str(videoCodingType) + '</videoCodingType>' + \
                   '</ThermalStreamParam>'

        print(data_xml)

        response = requests.put(
            self.streamParam_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    # 开关宽动态
    def set_wdr(self, element_to_query=None, wdrMode='open', ):
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?>' + \
                   '<WDR><mode>' + str(wdrMode) + '</mode>'
        if wdrMode == 'open':
            data_xml += '<WDRLevel>50</WDRLevel>'
        data_xml += '</WDR>'
        print(data_xml)

        response = requests.put(
            self.wdr_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return response.text

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)
            print(tree)
            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            print(element_to_query)
            result = tree.findall(element_to_query)
            print(result)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    def get_version(self):
        """
        Returns the firmware version running on the camera
        """
        return self.get_about(element_to_query='firmwareVersion')

    def get_about(self, element_to_query=None):
        """
        Returns ElementTree containing the result of
        <host>/System/deviceInfo
        or if element_to_query is not None, the value of that element
        """

        response = requests.get(
            self.deviceinfo_url,
            auth=self._auth_fn(self._username, self._password))

        if response.status_code != 200:
            log_response_errors(response)
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()


        except AttributeError as attib_err:

            return None
        return None

    def is_motion_detection_enabled(self):
        """Get current state of Motion Detection.

        Returns False on error or if motion detection is off."""

        response = requests.get(self.motion_url, auth=self._auth_fn(
            self._username, self._password))

        if response.status_code != 200:
            return False

        try:

            tree = tree_no_ns_from_string(response.text)
            enabled_element = tree.findall(
                './/%senabled' % self._xml_namespace)
            sensitivity_level_element = tree.findall(
                './/%ssensitivityLevel' % self._xml_namespace)
            if len(enabled_element) == 0:
                return False
            if len(sensitivity_level_element) == 0:
                return False

            result = enabled_element[0].text.strip()

            if int(sensitivity_level_element[0].text) == 0:
                sensitivity_level_element[0].text = str(
                    self._sensitivity_level)

            if result == 'true':
                # Save this for future switch off
                self.xml_motion_detection_on = ElementTree.tostring(
                    tree, encoding=XML_ENCODING)
                enabled_element[0].text = 'false'
                self.xml_motion_detection_off = ElementTree.tostring(
                    tree, encoding=XML_ENCODING)
                return True
            # Save this for future switch on
            self.xml_motion_detection_off = ElementTree.tostring(
                tree, encoding=XML_ENCODING)
            enabled_element[0].text = 'true'
            self.xml_motion_detection_on = ElementTree.tostring(
                tree, encoding=XML_ENCODING)
            return False

        except AttributeError as attib_err:
            return False

    def enable_motion_detection(self):
        """ Enable Motion Detection """

        self.put_motion_detection_xml(self.xml_motion_detection_on)

    def disable_motion_detection(self):
        """ Disable Motion Detection """

        self.put_motion_detection_xml(self.xml_motion_detection_off)

    def put_motion_detection_xml(self, xml):
        """ Put request with xml Motion Detection """

        headers = DEFAULT_HEADERS
        headers['Content-Length'] = str(len(xml))
        headers['Host'] = self._host
        response = requests.put(self.motion_url, auth=self._auth_fn(
            self._username, self._password), data=xml, headers=headers)

        if response.status_code != 200:
            return

        try:
            tree = tree_no_ns_from_string(response.text)
            enabled_element = tree.findall(
                './/%sstatusString' % self._xml_namespace)
            if len(enabled_element) == 0:
                return

            if enabled_element[0].text.strip() == 'OK':
                pass

        except AttributeError as attrib_err:
            return

    # 打开雨刷
    def enable_wiper(self, status='on', element_to_query=None):
        """ Enable Wiper """
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?><PTZAux><id>1</id><type>WIPER</type><status>' + status + '</status></PTZAux>'
        response = requests.put(
            self.auxcontrol_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    # 补光灯控制
    def enable_light(self, status='on', element_to_query=None):
        """ Enable Light """
        data_xml = '<?xml version: "1.0" encoding="UTF-8"?><PTZAux><id>1</id><type>LIGHT</type><status>' + status + '</status></PTZAux>'
        response = requests.put(
            self.auxcontrol_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    # 辅助通道控制
    def set_auxcontrol(self, target, status='on', element_to_query=None):
        """ Enable Light """
        data_xml = f'<?xml version: "1.0" encoding="UTF-8"?><PTZAux><id>1</id><type>{target}</type><status>{status}</status></PTZAux>'
        response = requests.put(
            self.set_auxcontrol_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return None

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    def get_auxcontrol(self, element_to_query=None):
        response = requests.get(
            self.get_auxcontrol_url,
            auth=self._auth_fn(self._username, self._password),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return response.text
        if element_to_query is None:
            # print(response.text)
            # 返回的是json格式的数据，返回的是一个字典
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)
            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    # 新增红外测温开启关闭
    def enable_thermometry(self, status='on', element_to_query=None):
        if status.lower() == 'on':
            enable_flag = 'true'
        else:
            enable_flag = 'false'

        data_xml = '<?xml version: "1.0" encoding="UTF-8"?><ThermometryBasicParam xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">' + \
                   '<id>2</id>' + \
                   '<enabled>' + enable_flag + '</enabled>' + \
                   '<streamOverlay>true</streamOverlay>' + \
                   '<pictureOverlay>false</pictureOverlay>' + \
                   '<temperatureRange>-20~150</temperatureRange>' + \
                   '<temperatureUnit>degreeCentigrade</temperatureUnit>' + \
                   '<emissivity>0.96</emissivity>' + \
                   '<distanceUnit>centimeter</distanceUnit>' + \
                   '<specialPointThermType>centerPoint</specialPointThermType>' + \
                   '<distance>3000</distance>' + \
                   '<reflectiveEnable>false</reflectiveEnable>' + \
                   '<alert>45.0</alert>' + \
                   '<alarm>55.0</alarm>' + \
                   '<showTempStripEnable>' + enable_flag + '</showTempStripEnable>' + \
                   '<AlertOutputIOPortList>' + \
                   '<OutputIOPort>' + \
                   '<portID>1</portID>' + \
                   '<enabled>false</enabled>' + \
                   '</OutputIOPort>' + \
                   '<OutputIOPort>' + \
                   '<portID>2</portID>' + \
                   '<enabled>false</enabled>' + \
                   '</OutputIOPort>' + \
                   '</AlertOutputIOPortList>' + \
                   '<AlarmOutputIOPortList>' + \
                   '<OutputIOPort>' + \
                   '<portID>1</portID>' + \
                   '<enabled>false</enabled>' + \
                   '</OutputIOPort>' + \
                   '<OutputIOPort>' + \
                   '<portID>2</portID>' + \
                   '<enabled>false</enabled>' + \
                   '</OutputIOPort>' + \
                   '</AlarmOutputIOPortList>' + \
                   '<alertFilteringTime>0</alertFilteringTime>' + \
                   '<alarmFilteringTime>0</alarmFilteringTime>' + \
                   '<displayMaxTemperatureEnabled>true</displayMaxTemperatureEnabled>' + \
                   '<displayMinTemperatureEnabled>true</displayMinTemperatureEnabled>' + \
                   '<displayAverageTemperatureEnabled>false</displayAverageTemperatureEnabled>' + \
                   '<thermometryInfoDisplayposition>rules_around</thermometryInfoDisplayposition>' + \
                   '<emissivityMode>customsettings</emissivityMode>' + \
                   '<VehicleBlur>' + \
                   '<enabled>false</enabled>' + \
                   '<sensitiveLevel>2</sensitiveLevel>' + \
                   '<filterEnabled>false</filterEnabled>' + \
                   '</VehicleBlur></ThermometryBasicParam>'
        # print(data_xml)
        response = requests.put(
            self.thermometry_basic_url,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return response.text

        if element_to_query is None:
            return response.text
        try:
            tree = tree_no_ns_from_string(response.text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                return result[0].text.strip()
        except AttributeError as attib_err:
            return None
        return None

    # 新增配置指定通道视频参数，暂时只开放视频编码
    # videoCodingType: 1:H.264 2:H.265 3:MJPEG
    # resolution: 1:704*576 2:352*288
    def set_videoParam(self, channel='102', videoCodingType='1', resolution='1'):
        if videoCodingType == '1':
            videoCodingType = 'H.264'
        elif videoCodingType == '2':
            videoCodingType = 'H.265'
        elif videoCodingType == '3':
            videoCodingType = 'MJPEG'
        else:
            videoCodingType = 'MJPEG'
        # 分辨率
        if resolution == '1':
            videoResolutionWidth = '704'
            videoResolutionHeight = '576'
        elif resolution == '2':
            videoResolutionWidth = '352'
            videoResolutionHeight = '288'
        else:
            videoResolutionWidth = '704'
            videoResolutionHeight = '576'
        data_xml = '''"1.0" encoding="UTF-8"?><StreamingChannel xmlns="http://www.hikvision.com/ver20/XMLSchema" version="2.0">
        <id>102</id>
        <channelName>Camera 01</channelName>
        <enabled>true</enabled>
        <Transport>
        <maxPacketSize>1000</maxPacketSize>
        <ControlProtocolList>
        <ControlProtocol>
        <streamingTransport>RTSP</streamingTransport>
        </ControlProtocol>
        <ControlProtocol>
        <streamingTransport>HTTP</streamingTransport>
        </ControlProtocol>
        <ControlProtocol>
        <streamingTransport>SHTTP</streamingTransport>
        </ControlProtocol>
        <ControlProtocol>
        <streamingTransport>SRTP</streamingTransport>
        </ControlProtocol>
        </ControlProtocolList>
        <Unicast>
        <enabled>true</enabled>
        <rtpTransportType>RTP/TCP</rtpTransportType>
        </Unicast>
        <Multicast>
        <enabled>true</enabled>
        <destIPAddress>0.0.0.0</destIPAddress>
        <videoDestPortNo>8866</videoDestPortNo>
        <audioDestPortNo>8868</audioDestPortNo>
        </Multicast>
        <Security>
        <enabled>true</enabled>
        <certificateType>digest</certificateType>
        <SecurityAlgorithm>
        <algorithmType>MD5</algorithmType>
        </SecurityAlgorithm>
        </Security>
        <SRTPMulticast>
        <SRTPVideoDestPortNo>18866</SRTPVideoDestPortNo>
        <SRTPAudioDestPortNo>18868</SRTPAudioDestPortNo>
        </SRTPMulticast>
        </Transport>

        <Audio>
        <enabled>false</enabled>
        <audioInputChannelID>1</audioInputChannelID>
        <audioCompressionType>G.711alaw</audioCompressionType>
        </Audio>
        <Video xmlns=""><enabled>true</enabled><videoInputChannelID>1</videoInputChannelID><videoCodecType>{videoCodecType}</videoCodecType><videoResolutionWidth>{videoResolutionWidth}</videoResolutionWidth><videoResolutionHeight>{videoResolutionHeight}</videoResolutionHeight><videoQualityControlType>vbr</videoQualityControlType><fixedQuality>20</fixedQuality><vbrUpperCap>1024</vbrUpperCap><maxFrameRate>2500</maxFrameRate><GovLength>50</GovLength></Video></StreamingChannel>'''
        # 替换videoCodecType占位符，替换为实际的值
        data_xml = data_xml.format(videoCodecType=videoCodingType, videoResolutionWidth=videoResolutionWidth,
                                   videoResolutionHeight=videoResolutionHeight)

        response = requests.put(
            self.stream_set_url + channel,
            auth=self._auth_fn(self._username, self._password),
            data=data_xml,
        )
        if response.status_code != 200:
            return response.text
        return response.text
