import json


# 定义一个嵌套类
class NestedClass:
    def __init__(self):
        pass

    def __str__(self):
        co = self.__dict__
        return json.dumps(co)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def get_json(self):
        return json.dumps(self.__dict__)


class msg:
    topic = "/not_set_topic"

    def __init__(self):
        pass

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def get_json(self):
        co = self.__dict__
        for key in co.keys():
            if isinstance(co[key], NestedClass):
                co[key] = co[key].__dict__
            if isinstance(co[key], list):
                for i in range(len(co[key])):
                    if isinstance(co[key][i], NestedClass):
                        co[key][i] = co[key][i].__dict__
        return json.dumps(co)

    @staticmethod
    def getMsg(data, msg_type=None):
        if isinstance(data, str):
            data = json.loads(data)
        if msg_type is None:
            msg_test = msg()
            for keyValue in data:
                msg_test.__setattr__(keyValue, data[keyValue])
            return msg_test
        else:
            msg_test = msg_type()
            co = msg_test.__dir__()
            co_final = []
            co_module = None
            # 抛开topic，getMsg以及__开头的属性
            for i in range(len(co)):
                if co[i] == 'topic' or co[i] == 'getMsg' or co[i][0] == '_' or co[i].endswith('get_json'):
                    continue
                if co[i].endswith('_module'):
                    co_module = co[i]
                    continue
                co_final.append(co[i])
            # 找到co_final中的_class结尾的键
            for key in co_final:
                if key.endswith('_class'):
                    tmp_class = getattr(msg_test, key)()
                    # key去掉_class结尾，并且把类型转换为对象
                    tmp_key = key[:-6]
                    tmp_dict = data[tmp_key]
                    # 转成对象
                    for keyValue in tmp_class.__dict__:
                        tmp_class.__setattr__(keyValue, tmp_dict[keyValue])
                    co_final.remove(key)
                    co_final.remove(tmp_key)
                    msg_test.__setattr__(tmp_key, tmp_class)
                    break
            for keyValue in co_final:
                msg_test.__setattr__(keyValue, data[keyValue])
            # msg_test，如果属性是list，则转换为对象
            if co_module is not None:
                for keyValue in msg_test.__dict__:
                    if isinstance(msg_test.__dict__[keyValue], list):
                        tmp_list = []
                        tmp_data = msg_test.__dict__[keyValue]
                        for item in tmp_data:
                            item = json.loads(item)
                            tmp_class = getattr(msg_test, co_module)()
                            for k in item:
                                tmp_class.__setattr__(k, item[k])
                            tmp_list.append(tmp_class)
                        msg_test.__setattr__(keyValue, tmp_list)
            return msg_test


class test_msg(msg):
    """
    定义一个测试消息,消息结构如下：
    {
        "test": {
            "x": 1, //测试消息的x坐标
            "y": 2, //测试消息的y坐标
            "z": 3 //测试消息的z坐标
        }
    }
    """
    topic = "/test"

    class test_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.x = ""
            self.y = ""
            self.z = ""

    def __init__(self):
        super().__init__()
        self.test = self.test_class()


# 底盘控制消息
class app_cmd_vel(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "priority": 2, //消息优先级,默认为2,int类型
        "msg": {
            "v": 1, //线速度,单位m/s,float类型
            "w": 2, //角速度,单位rad/s,float类型
            "sn": "123" //只有web端发送带sn,str类型
        }
    }
    """
    topic = "/app_cmd_vel"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.v = ""
            self.w = ""
            self.sn = ""

    def __init__(self):
        super().__init__()
        self.priority = 2  # 消息优先级，默认为2
        self.msg = self.msg_class()  # 消息体


# 底盘控制消息返回值
class app_cmd_vel_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/app_cmd_vel_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 云台控制
class cloud_platform_c(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "status":"left", //left左;right右;up上;down下;leftup左上;leftdown左下;-rightup右上;rightdown右下;zoomup放大;zoomdown缩小;stop停止;String类型
            "isPreset":"1", //是否到预置点-1:设置预置点;0:保持;1:转到预置点;2:删除预置点,int类型
            "preset_state":"", //当前预置位状态Byte
        }
    }
    """
    topic = "/cloud_platform_c"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.status = ""  # string型
            self.isPreset = ""  # int型
            self.preset_state = ""  # 当前预置位状态Byte

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 云台控制返回值
class cloud_platform_c_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/cloud_platform_c_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭录包
class data_record(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动录包;0:关闭录包,int类型
        }
    }
    """
    topic = "/data_record"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭录包返回值
class data_record_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/data_record_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭建图
class slam(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动建图;0:关闭建图,int类型
        }
    }
    """
    topic = "/slam"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭建图返回值
class slam_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/slam_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭导航功能
class ctrl_nav(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动建图;0:关闭建图,int类型
        }
    }
    """
    topic = "/ctrl_nav"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭导航功能返回值
class ctrl_nav_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/ctrl_nav_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 实时位置上报
class pose_message(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            'x':0, //小车的x坐标,int类型
            'y':0, //小车的y坐标,int类型
            'z':0, //小车的z坐标,int类型
            'theta':0 //小车的theta坐标,int类型
        }
    }
    """
    topic = "/pose_message"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.x = ""  # int型
            self.y = ""  # int型
            self.z = ""  # int型
            self.theta = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取录包程序运行状态
class get_data_record(msg):
    """
    定义一个应用消息,消息结构如下：
    {

    }
    """
    topic = "/get_data_record"

    def __init__(self):
        super().__init__()
        self.msg = ""


# 获取录包程序运行状态返回值
class get_data_record_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/get_data_record_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取导航程序运行状态
class get_navigation(msg):
    """
    定义一个应用消息,消息结构如下：
    {

    }
    """
    topic = "/get_navigation"

    def __init__(self):
        super().__init__()
        self.msg = ""


# 获取导航程序运行状态返回值
class get_navigation_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/get_navigation_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取建图进度
class process_message(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "p":1, //建图进度,int类型
        }
    }
    """
    topic = "/process_message"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.p = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 底盘io操作
class io_ctrl(msg):
    """
    定义一个应用消息,消息结构如下：
    {
       "priority": 1, //优先级0-5 遥操作:0 跟随:1 自主导航:2 其它:3
        "msg":{
            "sn":"123",//只有web端发送带sn,服务端转发给客户端不需要sn
            "io":[
                {
                "name":"",//控制模块名称
                "value":0//值0-255,如果是开关状态,则用0表示关,1表示开
                }
            ]
        }
    }
    """
    topic = "/io_ctrl"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # int型
            self.io = []  # list型

    def __init__(self):
        super().__init__()
        self.priority = 2  # 消息优先级,默认为2
        self.msg = self.msg_class()  # 消息体


# 底盘io操作返回值
class io_ctrl_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "io":[
                {
                "name":"",//控制模块名称
                "value":0//值0-255,如果是开关状态,则用0表示关,1表示开
                }
            ]
        }
    }
    """
    topic = "/io_ctrl_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.io = ""  # list型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 电池电压上报
class get_voltage(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn,服务端转发给客户端不需要sn
            "time":10, //发送周期,int类型
            "status":"subscribe" //subscribe:开始获取,unsubscribe:停止获取
        }
    }
    """
    topic = "/get_voltage"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # string型
            self.time = ""  # int型
            self.status = ""  # string型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 电池电压上报返回值
class get_voltage_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "voltage":[80000,0],//电池1电压，电池2电压,单位mv
            "current":[1000,0], //电池1电流,电池2电流
            "temperature":0, //当前温度,int类型
            "now_percent":0, //剩余电量百分比,单位%,int类型
            "max_capacity":0, //满电容量,单位0.1AH,int类型
            "now_capacity":0, //当前剩余容量,单位0.1AH,int类型
            "state":0, //电池状态，参考各电池状态说明表
            "charging_state":0, //充电状态	0:未充电 1:充电
        }
    }
    """
    topic = "/get_voltage_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.voltage = ""  # list型
            self.current = ""  # list型
            self.temperature = ""  # int型
            self.now_percent = ""  # int型
            self.max_capacity = ""  # int型
            self.now_capacity = ""  # int型
            self.state = ""  # int型
            self.charging_state = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 轮速反馈
class get_speed(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn,服务端转发给客户端不需要sn
            "time":10, //发送周期,int类型
            "status":"subscribe" //subscribe:开始获取,unsubscribe:停止获取
        }
    }
    """
    topic = "/get_speed"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # string型
            self.time = ""  # int型
            self.status = ""  # string型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 轮速反馈返回值
class get_speed_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "speed":{
                "v":0.1,//float类型
                "w":0.1//float类型
            },
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/get_speed_response"

    class msg_class(NestedClass):

        def __init__(self):
            super().__init__()
            self.speed = {
                "v": "",
                "w": ""
            }  # dict型
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 机器人电机信息上报
class motor_info_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "rpm":[0,0,0,0],        //list[int]，必存。 电机转速，单位：rpm
            "current":[0,0,0,0],    //list[int]，必存。 电机电流，单位：0.01A
            "state":[0,0,0,0]       //list[int]，必存。 电机状态，草考电机说明表
        }
    }
    """
    topic = "/motor_info_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.rpm = []  # list[int]
            self.current = []  # list[int]
            self.state = []  # list[int]

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 机器人超声波上报
class sonic_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sonic":[100,100,100,100,100,100]   //list[int]，必存。 超声数据，单位：mm
        }
    }
    """
    topic = "/sonic_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sonic = []  # list[int]

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 机器人停止状态上报
class stop_state_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "button": 0,    //int，必存。 急停按钮急停 0：无触发 1：触发
            "collision": 0, //int，必存。 触边急停 二进制第0位 前触边 第1位后触边，0：无触发 1：触发
            "sonic": 0,     //int，必存。 超声急停 二进制第x位 第X个超声， 0：无触发 1：触发
            "soft": 0       //int，必存。 软件急停 0：无触发 1：触发
        }
    }
    """
    topic = "/stop_state_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.button = int()  # int
            self.collision = int()  # int
            self.sonic = int()  # int
            self.soft = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 机器人温度信息上报
class temperature_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "temperature":[     //list[json]，必存。 反馈temperature对象
                {
                    "name":"",  //string，必存。     对应温度点名称
                    "value":0   //int，必存。        值，单位：°C
                }
            ]
        }
    }
    """
    topic = "/temperature_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.temperature = [
                {
                    "name": "",  # string
                    "value": int()  # int
                }
            ]  # list[json]

        def __init__(self):
            super().__init__()
            self.msg = self.msg_class()  # 消息体


# 控制机器人触发软件急停
class software_stop(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "control":1    //int，必选。 控制指令 0：控制软件不急停 1：控制软件急停
        }
    }
    """
    topic = "/software_stop"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.control = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 传感器反馈
class get_sensor_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "collide":0, //防撞触边状态:0:未触发 1:前触边触发 2:后触边触发 3:前后触边触发,int类型
            "button_stop":0, //急停按钮状态:off:正常 on:急停,string类型
            "sonic_stop":0, //超声停障状态:0:未触发 x:触发状态,int类型
            "sonic":[100,100,100,100,100,100] //超声数据 单位mm	,list型
        }
    }
    """
    topic = "/get_sensor_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.collide = ""  # int型
            self.button_stop = ""  # string型
            self.sonic_stop = ""  # int型
            self.sonic = ""  # list型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 温控系统：控制机器人温控系统
class heater_control(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "control_1":0,   //int，非必选。加热系统1控制 0：关闭 1：开启
            "min_1":40,      //int，非必选。加热系统1温度下限
            "max_1":65,      //int，非必选。加热系统1温度上限
            "control_2":1,   //int，非必选。加热系统2控制 0：关闭 1：开启
            "min_2":30,      //int，非必选。加热系统2温度下限
            "max_2":65,      //int，非必选。加热系统2温度上限
            "save":1         //int，非必选。0: 不保存参数 1: 保存参数
        }
    }
    """
    topic = "/heater_control"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.control_1 = int()  # int
            self.min_1 = int()  # int
            self.max_1 = int()  # int
            self.control_2 = int()  # int
            self.min_2 = int()  # int
            self.max_2 = int()  # int
            self.save = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 温控系统：控制机器人温控系统 返回
class heater_control_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "control_1":0,   //int，必存。加热系统1控制 0：关闭 1：开启
            "min_1":40,      //int，必存。加热系统1温度下限
            "max_1":65,      //int，必存。加热系统1温度上限
            "control_2":1,   //int，必存。加热系统2控制 0：关闭 1：开启
            "min_2":30,      //int，必存。加热系统2温度下限
            "max_2":65       //int，必存。加热系统2温度上限
        }
    }
    """
    topic = "/heater_control_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.control_1 = int()  # int
            self.min_1 = int()  # int
            self.max_1 = int()  # int
            self.control_2 = int()  # int
            self.min_2 = int()  # int
            self.max_2 = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取任务程序运行状态
class get_task_status(msg):
    """
    定义一个应用消息,消息结构如下：
    {
    }
    """
    topic = "/get_task_status"

    def __init__(self):
        super().__init__()
        self.msg = ""


# 获取任务程序运行状态
class get_task_status(msg):
    """
    定义一个应用消息,消息结构如下：
    {
    }
    """
    topic = "/get_task_status"

    def __init__(self):
        super().__init__()
        self.msg = ""


# 获取任务程序运行状态返回值
class get_task_status_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:执行任务可用，1:停止任务可用
        }
    }
    """
    topic = "/get_task_status_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 开始任务
class start_task(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "id":1 ,//任务id,string类型
        }
    }
    """
    topic = "/start_task"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.id = ""  # string类型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 开始任务返回值
class start_task_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:失败，1:成功
        }
    }
    """
    topic = "/start_task_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 停止任务
class stop_task(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "id":1 ,//任务id,string类型
        }
    }
    """
    topic = "/stop_task"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.id = ""  # string类型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 停止任务返回值
class stop_task_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:失败，1:成功
        }
    }
    """
    topic = "/stop_task_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取自主任务列表信息
class get_task_list(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":{
            "data":"true" //true: 获取
        }
    }
    """
    topic = "/get_task_list"

    class data_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.data = ""  #

    def __init__(self):
        super().__init__()
        self.data = self.data_class()  # 消息体


# 获取自主任务列表信息返回值
class task_list(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":[
            {
                "isStart":true, //是否循环true:循环 false:不循环,bool类型
                "task_id":"line_1654655590", //路线id,string类型
                "task_name":"0608", //路线名称,string类型
                "taskcontent":[
                    {
                        "createtime":"1654655744", //创建时间,string类型
                        "preset":"1", //预置点,string类型
                        "task_id":"task_1654655744", //任务id,string类型
                        "theta":"-1.57", //角度,string类型
                        "time":"1", //周期,string类型
                        "type":"digital", //任务类型,string类型
                        "type_text":"指针表识别",//任务类型文本,string类型
                        "x":"0.37", //x坐标,string类型
                        "y":"-0.73" //y坐标,string类型
                    }
                ]
            }
        ]
    }
    """
    topic = "/task_list"

    class data_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.isStart = ""  # string类型
            self.task_id = ""  # string类型
            self.task_name = ""  # string类型
            self.taskcontent = [{
                "createtime": "",
                "preset": "",
                "task_id": "",
                "theta": "",
                "time": "",
                "type": "",
                "type_text": "",
                "x": "",
                "y": ""
            }]  # list类型

    def __init__(self):
        super().__init__()
        self.data = self.data_class()  # 消息体


# 实时日志
class task_status(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "type":"pointer", //当前任务类型,string类型
        "content":"digital", //任务内容,string类型
        "sn":130, //机器人名称,string类型
        "task_id":"line_1655865282", //任务id,string类型
        "rec_num":"22.8", //识别结果,string类型
        "rec_type":"pointer", //执行任务类型,string类型
        "rec_in":"", //抓拍原图,string类型
        "rec_out":"", //识别图片,string类型
        "status":"end" //机器人状态,string类型
    }
    """
    topic = "/task_status"

    def __init__(self):
        super().__init__()
        self.type = ""  # string类型
        self.content = ""  # string类型
        self.sn = ""  # string类型
        self.task_id = ""  # string类型
        self.rec_num = ""  # string类型
        self.rec_type = ""  # string类型
        self.rec_in = ""  # string类型
        self.rec_out = ""  # string类型
        self.status = ""  # string类型


# 设置自主任务列表信息
class set_task_list(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":[
            {
                "isStart":true, //是否循环true:循环 false:不循环,bool类型
                "task_id":"line_1654655590", //路线id,string类型
                "task_name":"0608", //路线名称,string类型
                "taskcontent":[
                    {
                        "createtime":"1654655744", //创建时间,string类型
                        "preset":"1", //预置点,string类型
                        "task_id":"task_1654655744", //任务id,string类型
                        "theta":"-1.57", //角度,string类型
                        "time":"1", //周期,string类型
                        "type":"digital", //任务类型,string类型
                        "type_text":"指针表识别",//任务类型文本,string类型
                        "x":"0.37", //x坐标,string类型
                        "y":"-0.73" //y坐标,string类型
                    }
                ]
            }
        ]
    }
    """
    topic = "/set_task_list"

    class data_class_module(NestedClass):
        def __init__(self):
            super().__init__()
            self.isStart = ""  # string类型
            self.task_id = ""  # string类型
            self.task_name = ""  # string类型
            self.taskcontent = [{
                "createtime": "",
                "preset": "",
                "task_id": "",
                "theta": "",
                "time": "",
                "type": "",
                "type_text": "",
                "x": "",
                "y": ""
            }]  # list类型

    def __init__(self):
        super().__init__()
        self.data = []


# 启动或关闭跟随功能
class ctrl_follow(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动跟随;0:关闭跟随,int类型
        }
    }
    """
    topic = "/ctrl_follow"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭跟随功能返回值
class ctrl_follow_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "action:0, //结果，0:关闭，1:开启
            "result":1 //0:失败，1:成功
        }
    }
    """
    topic = "/ctrl_follow_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.action = ""  # int型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行音频播放
class audio_output_play(msg):
    """
    定义一个应用消息,消息结构如下：
    {   "task_id":"10000", //任务唯一表示符
        "msg":{
            "name":"follow_start", //播放音频名称,string类型
            "volume":"" //播放音量 0-100,string类型
        }
    }
    """
    topic = "/audio/output/play"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # string型
            self.volume = ""  # string型

    def __init__(self):
        super().__init__()
        self.task_id = ''
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行音频播放返回值
class audio_output_play_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {   "task_id":"10000", //任务唯一表示符
        "msg":{
            "error_code": 0, //出错代码
            "error_msg": "", //出错信息
            "result": 1 //结果 0:失败,1:成功
        }
    }
    """
    topic = "/audio/output/play_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # string型
            self.error_msg = ""  # string型
            self.result = ""  # string型

    def __init__(self):
        super().__init__()
        self.task_id = ''
        self.msg = self.msg_class()  # 消息体


# 读取或写入单板硬件配置信息
class hardware_ctrl(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        {
            "priority": 0, //优先级0-5 遥操作:0 跟随:1 自主导航:2 其它:3
            "msg":{
                "Mode":1, //uint8_t,操作模式 0:读取 1:写入
                "MaxRPM":1, //uint16_t,电机最高转速 RPM
                "DriverType":1, //uint8_t,控制指令：0x00:惠斯通 0x01:拓达 0x02:中菱
                "ChassisType":1, //uint8_t,底盘类型
                "VoltageType":1, //uint8_t,电压表类型 0:电压表 1:速遥电池 2:RS485电压模块
                "UltrasonicType":1, //uint8_t,超声类型 104:KS104 136:KS136A
                "FrontNumber":1, //uint8_t,前侧超声数量
                "BackNumber":1, //uint8_t,后侧超声数量
                "SideNumber":1, //uint8_t,左右侧超声数量
                "GearBoxDirection":1, //uint8_t,减速器转向 0:反向 1:正向
            }
        }
    }
    """
    topic = "/hardware_ctrl"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.Mode = ""  # uint8_t,
            self.MaxRPM = ""  # uint16_t,
            self.DriverType = ""  # uint8_t,
            self.ChassisType = ""  # uint8_t,
            self.VoltageType = ""  # uint8_t,
            self.UltrasonicType = ""  # uint8_t,
            self.FrontNumber = ""  # uint8_t,
            self.BackNumber = ""  # uint8_t,
            self.SideNumber = ""  # uint8_t,
            self.GearBoxDirection = ""  # uint8_t,

    def __init__(self):
        super().__init__()
        self.priority = ""
        self.msg = self.msg_class()  # 消息体


# 读取或写入单板硬件配置信息返回值
class hardware_ctrl_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        {
            "msg":{
                "Mode":1, //uint8_t,操作模式 0:读取 1:写入
                "MaxRPM":1, //uint16_t,电机最高转速 RPM
                "DriverType":0x00, //uint8_t,控制指令：0x00:惠斯通 0x01:拓达 0x02:中菱
                "ChassisType":1, //uint8_t,底盘类型
                "VoltageType":1, //uint8_t,电压表类型 0:电压表 1:速遥电池 2:RS485电压模块
                "UltrasonicType":104, //uint8_t,超声类型 104:KS104 136:KS136A
                "FrontNumber":1, //uint8_t,前侧超声数量
                "BackNumber":1, //uint8_t,后侧超声数量
                "SideNumber":1, //uint8_t,左右侧超声数量
                "GearBoxDirection":1, //uint8_t,减速器转向 0:反向 1:正向
                "PSC": int(),  //PWM分频系数
                "PER": int(),  //PWM自动重载值 T=(PSC-1)/(PER-1)/72000 ms
                "Retained1": int(),  //备用
                "Retained2": int(),  //备用
                "Retained3": int(),  //备用
                "Retained4": int(),  //备用
                "Retained5": int(),  //备用
                "Retained6": int(),  //备用
                "Retained7": int(),  //备用
                "Retained8": int(),  //备用
                "Retained9": int(),  //备用
                "Retained10": int(),  //备用
            }
        }
    }
    """
    topic = "/hardware_ctrl_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.Mode = ""  # uint8_t,
            self.MaxRPM = ""  # uint16_t,
            self.DriverType = ""  # uint8_t,
            self.ChassisType = ""  # uint8_t,
            self.VoltageType = ""  # uint8_t,
            self.UltrasonicType = ""  # uint8_t,
            self.FrontNumber = ""  # uint8_t,
            self.BackNumber = ""  # uint8_t,
            self.SideNumber = ""  # uint8_t,
            self.GearBoxDirection = ""  # uint8_t,
            self.PSC = ""  # uint8_t
            self.PER = ""  # uint8_t
            self.Retained1 = ""
            self.Retained2 = ""
            self.Retained3 = ""
            self.Retained4 = ""
            self.Retained5 = ""
            self.Retained6 = ""
            self.Retained7 = ""
            self.Retained8 = ""
            self.Retained9 = ""
            self.Retained10 = ""

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 连接自检：检查各设备硬件连接情况
class check_hardware_connect(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "list": ["LIDAR:192.168.2.200","ttyUSB_IMU","ttyUSB_GPS","Video_CAR"]   //list[string]，必选。 需要检测的硬件名称，可含ip
        }
    }
    """
    topic = "/check_hardware_connect"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.list = []  # list[string]

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 连接自检：检查各设备硬件连接情况 返回
class check_hardware_connect_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "find_list": ["LIDAR","ttyUSB_IMU","ttyUSB_GPS","Video_CAR"],  //list[string]，必存。 检测到的硬件名称
            "unlink_list": ["LIDAR","ttyUSB_IMU","ttyUSB_GPS","Video_CAR"] //list[string]，必存。 可能未映射的硬件名称，即存在对应类型未映射的dev
        }
    }
    """
    topic = "/check_hardware_connect_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.find_list = []  # list[string]
            self.unlink_list = []  # list[string]

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 数据自检：检查各模块传感器数据情况
class check_data(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "list": ["LIDAR:192.168.2.200","IMU","GPS","SONIC"]   //list[string]，必选。 需要检测的硬件名称，可含ip
        }
    }
    """
    topic = "/check_data"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.list = []  # list[string]

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 数据自检：检查各模块传感器数据情况 返回
class check_data_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            //int，非必存。 对应检查数据结果，0：异常，1：正常
            "right_list" = ["LIDAR","IMU"],
            "error_list" = ["SONIC"]
        }
    }
    """
    topic = "/check_data_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.find_list = ""  # int
            self.error_list = ""  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 音频自检：检查扬声器、拾音器情况
class check_audio(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "output": 1,    //int，必选。0有效，屏蔽检测，无参数默认检查
            "input": 0      //int，必选。0有效，屏蔽检测，无参数默认检查
        }
    }
    """
    topic = "/check_audio"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.output = ""  # int
            self.input = ""  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 音频自检：检查扬声器、拾音器情况 返回
class check_audio_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0:失败，1:成功，2:进行中
        }
    }
    """
    topic = "/check_audio_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int
            self.error_msg = ""  # string
            self.result = ""  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# DOKO自检：底盘模块自检DOKO，chassis模块响应
class check_DOKO(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{}
    }
    """
    topic = "/check_DOKO"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# DOKO自检：底盘模块自检DOKO，chassis模块响应 返回
class check_DOKO_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0:失败，1:成功，2:进行中
        }
    }
    """
    topic = "/check_DOKO_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# USB摄像头检查：USB摄像头检查情况
class check_video(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "name": "Video_CAR",    //string，必选。 摄像头名称
            "time": 30              //int，必选。    摄像头名称
        }
    }
    """
    topic = "/check_video"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # string
            self.time = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# USB摄像头检查：USB摄像头检查情况 返回
class check_video_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "name": "Video_CAR",    //string，必存。 摄像头名称
            "data_str": "data"      //int，必存。    String格式的RGB数据base64编码
        }
    }
    """
    topic = "/check_video_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # string
            self.data_str = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 关闭工控机
class power_off(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "key": "XXXXXX" //string， 必选。内部校验码，本地获取及验证，仅响应底盘模块发出
        }
    }
    """
    topic = "/power_off"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.key = ""  # string

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 关闭工控机 返回
class power_off_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0:失败，1:成功
        }
    }
    """
    topic = "/power_off_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取跟随运动参数
class get_navigation_info(msg):
    """
    定义一个应用消息,消息结构如下：
    {
    }
    """
    topic = "/get_navigation_info"

    def __init__(self):
        super().__init__()


# 获取跟随运动参数返回值
class get_navigation_info_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "move_speed_v":1.0, //最大速度,float型
            "move_speed_w":1.0, //最大角速度,float型
            "follow_dis":1.0, //跟随距离,float型
            "result":1, //跟随状态,0:未开启,1:已开启,2:错误,int型
            "error_msg":"" //错误信息,string型
        }
    }
    """
    topic = "/get_navigation_info_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.move_speed_v = ""  # float型
            self.move_speed_w = ""  # float型
            self.follow_dis = ""  # float型
            self.result = ""  # float型
            self.error_msg = ""  # float型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人云台进行运动
class actuator_ptz_control(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "status":"",//状态String
            "isPreset":"",//是否设置到预置点Int
            "preset_state":"",//当前预置位状态Byte
            "cam_ex_code:"",//云台异常代码Int
            "x":"", //云台水平轴转动到指定角度;0:初始点;
            "y":"" //云台垂直轴转动到指定角度;0:初始点;
        }
    }
    """
    topic = "/actuator/ptz/control"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.status = ""  # String型
            self.isPreset = ""  # Int型
            self.preset_state = ""  # Byte型
            self.cam_ex_code = ""  # Int型
            self.x = ""  # Int型
            self.y = ""  # Int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# pc端开启关闭话筒
class audio_voice_control(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn,服务端转发给客户端不需要sn
            "action":1 ,//1:话筒开;0:话筒关,int类型
        }
    }
    """
    topic = "/audio_voice_control"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # String型
            self.action = ""  # Int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# pc端开启关闭话筒返回值
class audio_voice_control_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "action:0, //结果,0:关闭,1:开启
            "result":1 //0:失败,1:成功
        }
    }
    """
    topic = "/audio_voice_control_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.action = ""  # int型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 模块管理
class modules_manage_pub(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":[
            {
                "name":"Joysticks", //模块名称
                "status":true //模块状态,true:开启,false:关闭
            }
        ]
    }
    """
    topic = "/audio/voice/control_response"

    class data_class_module(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # int型
            self.status = ""  # string型

    def __init__(self):
        super().__init__()
        self.msg = []  # 消息体


# 服务器控制机器人进行音频录制
class audio_input_record(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": 10000, //任务唯一表示符
        "msg":
            {
                "name": "test_1", //录制音频名称
                "time": 4 //录制音频时间（单位s）
            }

    }
    """
    topic = "/audio/input/record"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # int型
            self.time = ""  # string型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        self.task_id = ""  # int型


# 服务器控制机器人进行音频录制返回
class aduio_input_record_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:失败,1:成功
        }
    }
    """
    topic = "/audio/input/record_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行巡检点声音采集并分析
class audio_analysis_check_voice(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",
        "msg":
            {
                "index": 10, //对比允许频率强度索引
                "description": "test_1", //采样点说明
                "time": 4, //录制音频时间（单位s）
                "get_method": 1, //频率强度获取方法 现仅有1
                "analysis_method": 1, // 异常分析方法 现仅有1
                "save": 1 //采样音频是否保留 0:不保留 1:保留 文件名为<description>_<task_id>.wav
                "image": 1 //是否需要上传图片 0:不需要 1:上传采样点频谱图 2:上传采样点及索引点频谱图
            }

    }
    """
    topic = "/audio/analysis/check_voice"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = ""  # int型
            self.description = ""  # string型
            self.time = ""  # int型
            self.get_method = ""  # int型
            self.analysis_method = ""  # int型
            self.save = ""  # int型
            self.image = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        self.task_id = ""  # int型


# 服务器控制机器人进行巡检点声音采集并分析返回
class audio_analysis_check_voice_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:失败,1:成功
        }
    }
    """
    topic = "/audio/analysis/check_voice_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行允许频率清除
class audio_analysis_clear_frequency_allow(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000", //string，必选。任务唯一表示符
        "msg":{
            "index": 1      //int，必选。目标索引，0-n为对应索引，负数为清除全部
        }
    }
    """
    topic = "/audio/analysis/clear_frequency_allow"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = int()  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行允许频率清除 返回
class audio_analysis_clear_frequency_allow_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必存。任务唯一表示符
        "msg":{
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0：失败， 1：成功
        }
    }
    """
    topic = "/audio/analysis/clear_frequency_allow_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行允许频率强度设定，通过录音及音频分析
class audio_analysis_set_frequency_allow(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",             //string，必选。 任务唯一表示符
        "msg": {
            "index": 10,                //int，必选。    设定允许频率强度索引
            "description": "normal_1",  //string，必选。 采样点说明
            "time": 4,                  //int，必选。    录制音频时间，单位：s
            "get_method": 1,            //int，必选。    频率强度获取方法，现仅有1
            "save": 0                   //int，必选。    采样音频是否保留 0：不保留 1：保留 文件名为<index>_<description>.wav
        }
    }
    """
    topic = "/audio/analysis/set_frequency_allow"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = int()  # int
            self.description = ""  # string
            self.time = int()  # int
            self.get_method = int()  # int
            self.save = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行允许频率强度设定，通过录音及音频分析 返回
class audio_analysis_set_frequency_allow_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必存。 任务唯一表示符
        "msg":{
            "error_code": 0,    //int，必存。    出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。 出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。    结果，0：失败， 1：成功
        }
    }
    """
    topic = "/audio/analysis/set_frequency_allow_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行允许频率强度上传
class audio_analysis_upload_frequency_allow(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000", //string，必选。任务唯一表示符
        "msg":{
            "index": 1      //int，必选。   目标索引，0-n为对应索引，负数为清除全部
        }
    }
    """
    topic = "/audio/analysis/upload_frequency_allow"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行允许频率强度上传 返回
class audio_analysis_upload_frequency_allow_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必存。 任务唯一表示符
        "msg":{
            "error_code": 0,    //int，必存。    出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。 出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。    结果，0：失败， 1：成功
            /*  result为1时，error_msg为返回数据：
                返回数据格式：
                单个索引格式：<index>:<description>:[允许频率强度list]
                如：
                “[1:normal_1:[[1000, 200], [1000, 300]]]”
                “[索引1:描述1:[[允许频率1, 允许强度1], [允许频率2, 允许强度2]]]”
                全部索引格式：[<index>:<description>:[允许频率强度list]]
                如：
                “[1:normal_1:[[1000, 200], [1000, 300]]],[2:normal_2:[[1500, 300], [1600, 500]]]”
                “[索引1:描述1:[[允许频率1, 允许强度1], [允许频率2, 允许强度2]]],[索引2:描述2:[[允许频率1, 允许强度1], [允许频率2, 允许强度2]]]”
            */
        }
    }
    进行操作时，机器人系统会留有一张对应<allow_data_+index>的频谱图，如:
    allow_data_1.jpg
    """
    topic = "/audio/analysis/upload_frequency_allow_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 机器人像服务器进行音频模块下jpg图像文件传输，由机器人发布
class audio_data_jpg_file(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。 任务唯一表示符
        "msg":{
            "format": "jpg",    //string，必选。 图像格式
            "type": 1,          //int，必选。    图像类型 0：预置频谱图 1：采样频谱图
            "data_str": ""      //string，必选。 图片数据 base64编码格式
        }
    }
    """
    topic = "/audio/data/jpg_file"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.format = ""  # string
            self.type = int()  # int
            self.data_str = ""  # string

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 机器人像服务器进行音频模块下wav音频文件传输，由机器人发布
class audio_data_wav_file(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。 任务唯一表示符
        "msg":{
            "format": "wav",    //string，必选。 音频格式
            "framerate": 0,     //string，必选。 音频采样频率
            "channels": 2,      //string，必选。 音频通道数
            "sampwidth": 2,     //int，必选。    图像类型 0:预置频谱图 1:采样频谱图
            "data_str": ""      //int，必选。    图片数据 base64编码格式
        }
    }
    """
    topic = "/audio/data/wav_file"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.format = ""  # string
            self.framerate = ""  # string
            self.channels = ""  # string
            self.sampwidth = int()  # int
            self.data_str = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人上传音频文件
class audio_file_upload(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。 任务唯一表示符
        "msg": {
            "name": "normal_1", //string，必选。 上传音频文件的名称
            "allow_size": 200   //string，必选。 上传音频允许大小，文件超过会进行压缩
        }
    }
    """
    topic = "/audio/file/upload"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # string
            self.allow_size = ""  # string

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人上传音频文件 返回
class audio_file_upload_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。任务唯一表示符
        "msg": {
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0：失败， 1：成功
        }
    }
    """
    topic = "/audio/file/upload_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行删除音频文件
class audio_file_remove(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。 任务唯一表示符
        "msg": {
            "name": "test_1"    //string，必选。 删除音频文件的名称
        }
    }
    """
    topic = "/audio/file/remove"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # string

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器控制机器人进行删除音频文件 返回
class audio_file_remove_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。任务唯一表示符
        "msg": {
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0：失败， 1：成功
        }
    }
    """
    topic = "/audio/file/remove_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器设置音量
class audio_output_set_volume(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。任务唯一表示符
        "msg": {
            "volume": 100       //int，必选。   播放音量0-100
        }
    }
    """
    topic = "/audio/output/set_volume"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.volume = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器设置音量 返回
class audio_output_set_volume_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必存。 任务唯一表示符
        "msg": {
            "error_code": 0,    //int，必存。    出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。 出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。    结果，0：失败， 1：成功
        }
    }
    """
    topic = "/audio/output/set_volume_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器获取音量
class audio_output_get_volume(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。任务唯一表示符
        "msg": {}
    """
    topic = "/audio/output/get_volume"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器获取音量 返回
class audio_output_get_volume_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必存。 任务唯一表示符
        "msg": {
            "error_code": 0,    //int，必存。    出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。 出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。    结果，0：失败， 1：成功
        }
    }
    """
    topic = "/audio/output/get_volume_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 设置导航目标点
class set_targetpoint(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "x":"1.0",//单位m
            "y":"2.5",//单位m
            "z":"0",//2D平面导航永远为0
            "theta":"1.57",//单位弧度
        }

    }
    """
    topic = "/set_targetpoint"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.x = ""
            self.y = ""
            self.z = ""
            self.theta = ""

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


class set_targetpoint_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:失败,1:成功
        }
    }
    """
    topic = "/set_targetpoint_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 视频识别获取数据
class get_data(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":{
            "iType":0, //识别类型 0 digital 1 pointer 2 power
            "camera_id":"", //相机id
            "task_type":1 , //任务类型
            "task_id":10000, // 任务id

        }
    }
    """
    topic = "/get_data"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.iType = ""  # int型
            self.camera_id = ""  # string型
            self.task_type = ""  # int型
            self.task_id = ""  # int型

    def __init__(self):
        super().__init__()
        self.data = self.msg_class()  # 消息体


class get_data_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "iType":0, //识别类型 0 digital 1 pointer 2 power
            "srcframe":"",
            "outframe":'' ,
            "outmessage":'',
            "task_type":'',
            "task_id":'',
            "timestamp":"",
            "camera_id":"",
            "bFlag":"",
            "sMessage":"",
            "sType":"",
            "sImgname":""

        }
    }
    """
    topic = "/get_data_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.iType = ""  # int型
            self.camera_id = ""  # string型
            self.task_type = ""  # int型
            self.task_id = ""  # int型
            self.srcframe = ""
            self.outframe = ""
            self.outmessage = ""
            self.timestamp = ""
            self.bFlag = ""
            self.sMessage = ""
            self.sType = ""
            self.sImgname = ""

    def __init__(self):
        super().__init__()
        self.data = self.msg_class()  # 消息体


# 给传感器发送充电指令
class charging_order(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":"start" //指令说明： start： 开始充电； stop： 停止充电
    }
    """
    topic = "/charging/order"

    def __init__(self):
        super().__init__()
        self.data = ''  # 消息体


# 给传感器发送充电指令返回值
class charging_order_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":true //指令说明： 指令成功
    }
    """
    topic = "/charging/order_response"

    def __init__(self):
        super().__init__()
        self.data = ''  # 消息体


# 无线充电传感器状态
class charging_status(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "",
        "data": {
            "voltage": 22.00,  //电压
            "current": 12.10, //电流
            "temperature": 30.00, //充电器温度
            "status": 0.0 , //系统状态： 0x00 表示未充电； 0x01 表示在充电段1，涓流充电； 0x02 表示在充电段2，恒流充电； 0x03 表示在充电段3，恒压充电； 0x04 表示在充电段4，预留； 0x05 表示在充电段5，预留。
            "error": 0.0, //故障码： 0x00 表示无故障； 0x02 表示充电过流； 0x03 表示充电欠流; 0x04 表示充电前级电压过压； 0x05 表示充电前级电压欠压； 0x06 表示充电过压； 0x07 表示电池异常； 0x08 表示过温； 0x09 表示电池充满； 0x0A 表示线圈零距离。
            "sys_code": 0.0, //系统状态： 0x00 表示系统正常待机，等待接收 上位机控制指令； 0x01 表示系统 接 收 到 不 正 确 的 上位机指令，需要重新发送指令； 0x02 表示系统接收到正确的上位机 指令，开始正常启动工作。
            }
    }
    """
    topic = "/charging/status"

    class data_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.voltage = ""  # float型
            self.current = ""  # float型
            self.temperature = ""  # float型
            self.status = ""  # float型
            self.error = ""  # float型
            self.sys_code = ""  # float型

    def __init__(self):
        super().__init__()
        self.data = self.data_class()  # 消息体
        self.task_id = ''  # string型


class get_radio(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {

            }
    }
    """
    topic = "/get_radio"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


class get_radio_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "radio": 0.1 (0.1至1.0)
            error_code : ""  # int型
            error_msg : ""  # string型
            result : ""  # int型
            }
    }
    """
    topic = "/get_radio_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.radio = ""
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


class set_radio(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "radio": 0.1 (0.1至1.0)
            }
    }
    """
    topic = "/set_radio"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.radio = ""

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


class set_radio_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            error_code : ""  # int型
            error_msg : ""  # string型
            result : ""  # int型
            }
    }
    """
    topic = "/set_radio_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 循迹列表请求
class track_list(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "data": true
            }
    }
    """
    topic = "/track_list"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.data = True

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 循迹任务列表返回
class track_list_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "data":[
                {
                    "index":0,
                    "x":"0.1",
                    "y":"0.1",
                    "theta":"1.6",
                    "createtime":'1654655744',
                    "preset":1,
                    "type": "digital",
                    "type_text": "数字表识别"
                }
            ]
        }
    }
    """
    topic = "/track_list_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.data = []

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 循迹关键点添加
class add_taskpoint(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "index":0 #第几个关键点
            }
    }
    """
    topic = "/add_taskpoint"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = ''  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 循迹关键点添加返回
class add_taskpoint_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/add_taskpoint_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 循迹关键点删除
class delete_taskpoint(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "index":0 #第几个关键点
            }
    }
    """
    topic = "/delete_taskpoint"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 循迹关键点删除返回
class delete_taskpoint_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/delete_taskpoint_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 客户端添加循迹关键点
class add_taskpoint_client(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "index":0,
                "x":"0.1",
                "y":"0.1",
                "theta":"1.6",
                "createtime":'1654655744',
                "preset":1,
                "type": "digital",
                "type_text": "数字表识别"
            }
    }
    """
    topic = "/add_taskpoint_client"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = ''
            self.x = ''
            self.y = ''
            self.theta = ''
            self.createtime = ''
            self.preset = ''
            self.type = ''
            self.type_text = ''
            self.cream = ''
            self.cream_text = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 客户端添加循迹关键点返回
class add_taskpoint_client_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/add_taskpoint_client_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 客户端删除循迹关键点
class delete_taskpoint_client(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "index":0
            }
    }
    """
    topic = "/delete_taskpoint_client"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 客户端删除循迹关键点返回
class delete_taskpoint_client_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/delete_taskpoint_client_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 客户端修改循迹关键点
class update_taskpoint_client(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "index":0,
                "x":"0.1",
                "y":"0.1",
                "theta":"1.6",
                "createtime":'1654655744',
                "preset":1,
                "type": "digital",
                "type_text": "数字表识别"
            }
    }
    """
    topic = "/update_taskpoint_client"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = ''
            self.x = ''
            self.y = ''
            self.theta = ''
            self.createtime = ''
            self.preset = ''
            self.type = ''
            self.type_text = ''
            self.cream = ''
            self.cream_text = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 客户端修改循迹关键点返回
class update_taskpoint_client_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/update_taskpoint_client_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 到达关键点
class reach_taskpoint(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "index":0,
            }
    }
    """
    topic = "/reach_taskpoint"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.index = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 到达关键点返回
class reach_taskpoint_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/reach_taskpoint_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 录制循迹
class track_record(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "action":0, 1:开始录制 0:结束录制
            }
    }
    """
    topic = "/track_record"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.action = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 录制循迹返回
class track_record_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/track_record_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 开始循迹
class start_track(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "action":0, 1:开始循迹 0:结束循迹
            }
    }
    """
    topic = "/start_track"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.action = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 开始循迹返回
class start_track_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/start_track_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 获取循迹状态
class get_track(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "action":1, 1 默认1
            }
    }
    """
    topic = "/get_track"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.action = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 获取循迹状态返回
class get_track_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 # 1:循迹中 0:未循迹
        }
    }
    """
    topic = "/get_track_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 获取循迹录制状态
class get_track_record(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
                "action":1, 1 默认1
            }
    }
    """
    topic = "/get_track_record"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.action = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 获取循迹录制状态返回
class get_track_record_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 # 1:录制中 0:未录制
        }
    }
    """
    topic = "/get_track_record_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ''
            self.error_msg = ''
            self.result = ''

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()


# 日志上传
class task_update_log(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":{
            "task_type":"",
            "content":"",
            "task_id":"",
            "rec_num":"",
            "rec_type":"",
            "rec_in":"",
            "rec_out":"",
            "iType":"",
            "camera_id":"",
            "sType":"",
            "sImgname":""
        }
    }
    """
    topic = "/task/update_log"

    class data_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.task_type = ''
            self.content = ''
            self.task_id = ''
            self.rec_num = ''
            self.rec_type = ''
            self.rec_in = ''
            self.rec_out = ''
            self.iType = ''
            self.camera_id = ''
            self.sType = ''
            self.sImgname = ''

    def __init__(self):
        super().__init__()
        self.data = self.data_class()


# .......................... RS485 Start 20230609..........................
# RS485接口绑定：rs485管理模块绑定接口
class target_com_binding(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000", //string，必选。任务唯一表示符
        "msg": {
            "address": 1    //int，必选。   表示绑定rs485串口的地址位
        }
    }
    """
    # 其中,target_com为串口对象名称。如：从站搭载在rs485串口1上，则topic="/rs485_1/binding"
    topic = "/target_com/binding"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.address = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# RS485接口绑定：rs485管理模块绑定接口 返回
class target_com_address_binding_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必选。 任务唯一表示符
        "msg": {
            /*  错误代码列表：
                0: "",  # 无错误
                1: "json data attribute lost",  # Json必要属性缺失
                2: "target address already exist, rebinding",  # 目标串口该地址位已绑定，重新绑定
                3: "target address already exist, refuse",  # 目标串口该地址位已绑定，拒绝绑定
                4: "rs485_module is exited",  # 管理模块退出
                254: "json data format error",  # Json格式错误
                255: "unknown error",  # 未知错误
            */
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0:失败，1:成功
        }
    }
    """
    # 其中，target_com为串口对象名称。如：从站搭载在rs485串口1上，绑定地址address=1，则 topic="/rs485_1/1/binding_response"
    topic = "/target_com/address/binding_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# RS485数据发送：rs485管理模块发送接口，用于从站进行串口发送
class target_com_send(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "priority": 1,          //int，必选。   优先级，0为高，1为低
        "address": 1,           //int，必选。   从站地址位
        "data": "Hex string"    //string，必选。从站需要发送的数据所对应的Hex字符串
    }
    """
    # 其中，target_com为串口对象名称。如：从站搭载在rs485串口1上，则topic="/rs485_1/send"
    topic = "/target_com/send"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.priority = int()  # int
            self.address = int()  # int
            self.data = ""  # string

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# RS485数据发送：rs485管理模块发送接口，用于从站进行串口发送 返回
class target_com_address_send_response(msg):
    """
    若rs485管理模块对应串口接收到未绑定的从站的send指令，会先进行绑定并发布binding_response消息
    定义一个应用消息,消息结构如下：
    {
        "data": "Hex string"    //string，必存。 从站数据发送后收到的返回值所对应的Hex字符串
    }
    """
    # 其中，target_com为串口对象名称。如：从站搭载在rs485串口1上，绑定地址address=1，则 topic="/rs485_1/1/send_response"
    topic = "/target_com/address/send_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.data = ""  # string

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 传感器控制：服务器控制机器人传感器
class sensor_target_control(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "",      //string，非必选。任务唯一表示符，不给task_id则返回默认””,Json格式错误时返回默认”65535”
        "msg": {
            "time": 1.0     //float，非必选。 任务唯一表示符，不给task_id则返回默认””,Json格式错误时返回默认”65535”
        }
    }
    """
    # 其中，target为传感器名称。如：甲烷传感器，则topic="/sensor/ch4/control"
    topic = "/sensor/target/control"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.time = float()  # float

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 传感器控制：服务器控制机器人传感器 返回
class sensor_target_control_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "task_id": "10000",     //string，必存。 任务唯一表示符
        "msg": {
            /*  错误代码列表：
                0: "",  # 无错误
                1: "json data attribute lost",  # Json必要属性缺失
                254: "json data format error",  # Json格式错误
                255: "unknown error"            # 未知错误
            */
            "error_code": 0,    //int，必存。   出错代码，具体内容参照错误代码列表
            "error_msg": "",    //string，必存。出错信息，具体内容参考错误代码列表
            "result": 1         //int，必存。   结果，0:失败，1:成功
        }
    }
    """
    # 其中，target为传感器名称。如：甲烷传感器，则topic="/sensor/ch4/control_response"
    topic = "/sensor/target/control_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = int()  # int
            self.error_msg = ""  # string
            self.result = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 阈值查询：服务器查询机器人传感器阈值
class sensor_target_parameters(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "mode": 1,              //int，必选。     0:读取参数 1:写入参数
            "time": 1.0,            //float，非必选。 time大于0传感器上传周期为time,time等于0传感器停止上传
            "temperature":          //string，非必选。需要设置阈值的数据对象
            {
                "limit_low": 10,    //float，非必选。 需要设置阈值下限
                "limit_high": 50,   //float，非必选。 需要设置阈值上限
                "limit_times":3     //int，非必选。   需要设置阈值的连续次数
            },
            "humidity":
            {
                "limit_low": 10,    //float，非必选。 需要设置阈值下限
                "limit_high": 50,   //float，非必选。 需要设置阈值上限
                "limit_times":3     //int，非必选。   需要设置阈值的连续次数
            }
        }
    }
    """
    # 其中，target为传感器名称。如：温湿度传感器则话题为sensor/p_h_t/parameters
    topic = "/sensor/target/parameters"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.mode = int()  # int
            self.time = float()  # float
            self.temperature = ""  # string
            self.limit_low = float()  # float
            self.limit_high = float()  # float
            self.limit_times = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 阈值查询：服务器查询机器人传感器阈值 返回
class sensor_target_parameters_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "time": 1.0,            //float，非必存。 time大于0传感器上传周期为time,time等于0传感器停止上传
            "temperature":          //string，非必存。需要设置阈值的数据对象
            {
                "limit_low": 10,    //float，非必存。 需要设置阈值下限
                "limit_high": 50,   //float，非必存。 需要设置阈值上限
                "limit_times":3     //int，非必存。   需要设置阈值的连续次数
            },
            "humidity":
            {
                "limit_low": 10,    //float，非必存。 需要设置阈值下限
                "limit_high": 50,   //float，非必存。 需要设置阈值上限
                "limit_times":3     //int，非必存。   需要设置阈值的连续次数
            }
        }
    }
    """
    # 其中target为传感器名称，举例：甲烷传感器，则topic="/sensor/ch4/control_response"
    topic = "/sensor/target/parameters_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.time = float()  # float
            self.temperature = ""  # string
            self.limit_low = float()  # float
            self.limit_high = float()  # float
            self.limit_times = int()  # int

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# .......................... RS485 End 20230609............................
# 服务器查询机器人系统时间
class time_sync(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {}
    }
    """

    topic = "/time_sync"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 服务器查询机器人系统时间 返回
class time_sync_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "time": "",            //string，必存。 工控机系统时间
        }
    }
    """

    topic = "/time_sync_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.time = ""  # string

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# rs485标准传感器的报警信息发布
class recognize_warning(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg": {
            "sn": "",               //string，必选。 序列号，传感器不涉及
            "bFlag": True,          //bool，必选。   是否有检测结果，传感器不涉及
            "sType": "",            //string，必选。 传感器名字
            "sValue": "",           //string，必选。 传感器数据
            "iTarget": 0,           //int，必选。    异常目标，传感器不涉及
            "LocationMessage": [],  //list，必选。   异常目标画面位置，传感器不涉及
            "error": False          //bool，必选。   是否处于异常，传感器不涉及
        }
    }
    """

    topic = "/recognize_warning"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # string
            self.bFlag = bool()  # bool
            self.sType = ""  # string
            self.sValue = ""  # string
            self.iTarget = int()  # int
            self.LocationMessage = []  # list
            self.error = bool()  # bool

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
