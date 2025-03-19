import ctypes
import time
import struct
import os

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        # print(f"{func.__name__} 运行时间为 {end_time - start_time} 秒")
        # 打印函数运行时间，微秒级别
        print(f"{func.__name__} 运行时间为 {(end_time - start_time) * 1000 * 1000} 微秒")
        return result
    return wrapper

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Dxr_Crypto(metaclass=Singleton):
    """
    DXR_TSDK类用于初始化SDK并提供加密、解密、创建组和获取组密钥等功能。

    Args:
        app_type_string (str): 应用类型字符串。
        app_account (str): 应用账号。
        pin_code (str): PIN码。
        phone_number (str): 手机号码。
        csp_addr (str): CSP地址。
        lib_path (str, optional): TSDK库文件路径，默认为"/root/TSDKTest/libtsdkTest.so"。

    Attributes:
        lib (ctypes.CDLL): TSDK库对象。

    Methods:
        __pre_main(): 内部方法，用于预激活安全介质。
        __init_sdk(app_type_string, app_account, pin_code, phone_number, csp_addr): 内部方法，用于初始化SDK。
        __auth(): 内部方法，用于进行入网测试。
        encrypt(inputString): 加密给定的字符串。
        decrypt(cipherBuff, cipherLen): 解密给定的密文。
        createGroupAndApplyKey(): 创建组并获取组密钥。
        destoryKey(): 销毁密钥。
        getGroupKey(groupID): 根据组ID获取组密钥。
    """
    def __init__(self, lib=None):
        if lib is not None:
            self.lib = lib
        else:
            app_type_string = "60"
            app_account = "lch6@quantum.com"
            pin_code = "12345678"
            phone_number = "13988888888"
            csp_addr = "qkeys.cn"
            current_path = os.path.dirname(os.path.abspath(__file__))
            # 判断下当前的系统，是windows还是linux
            lib_path = current_path + "/libtsdkTest_linux.so"
            platform = os.name
            if platform == "nt":
                # windows系统
                lib_path = current_path + "/lib/windows/x64/libtsdkTest.dll"
                pass
            elif platform == "posix":
                # linux系统
                lib_path = current_path + "/lib/linux/libtsdkTest_linux.so"
            self.lib = ctypes.CDLL(lib_path)

        self.dekey = None  # 新增属性来存储明文密钥
        need_init = True
        # 如果密钥文件存在，则从文件中读取密钥，否则执行初始化和认证操作，并导出密钥
        if os.path.exists('key.txt'):
            self.dekey = self.read_key_from_file()
            if self.dekey == None:
                print("从文件中读取密钥失败")
            else:
                print("从文件中读取密钥成功")
                need_init = False
        if need_init:
            self.__pre_main()
            self.__init_sdk(app_type_string, app_account, pin_code, phone_number, csp_addr)
            self.__auth()

    def __pre_main(self):
        """
        预激活安全介质。
        """
        self.lib.pre_main.argtypes = []
        self.lib.pre_main.restype = ctypes.c_int

        ret = self.lib.pre_main()
        if ret == 0:
            print("预激活安全介质成功")
        else:
            print("预激活安全介质失败")

    def __init_sdk(self, app_type_string, app_account, pin_code, phone_number, csp_addr):
        """
        初始化SDK。

        Args:
            app_type_string (str): 应用类型字符串。
            app_account (str): 应用账号。
            pin_code (str): PIN码。
            phone_number (str): 手机号码。
            csp_addr (str): CSP地址。
        """
        self.lib.init_sdk.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self.lib.init_sdk.restype = ctypes.c_int

        app_type_string = app_type_string.encode('utf-8')
        app_account = app_account.encode('utf-8')
        pin_code = pin_code.encode('utf-8')
        phone_number = phone_number.encode('utf-8')
        csp_addr = csp_addr.encode('utf-8')

        ret = self.lib.init_sdk(app_type_string, app_account, pin_code, phone_number, csp_addr)

        if ret == 0:
            print("初始化成功")
        else:
            print("初始化失败")

    def __auth(self):
        """
        进行入网测试。
        """
        self.lib.test_Auth.argtypes = []
        self.lib.test_Auth.restype = ctypes.c_int

        ret = self.lib.test_Auth()
        if ret == 0:
            print("入网测试成功")
        else:
            print("入网测试失败")

    @timer_decorator
    def encrypt(self, inputString="hello world"):
        """
        加密给定的字符串。

        Args:
            inputString (str, optional): 待加密的字符串，默认为"hello world"。

        Returns:
            tuple: 包含加密后的数据和加密后数据的长度。
        """
        self.lib.lu_encrypt.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_int)]
        self.lib.lu_encrypt.restype = ctypes.c_int

        plainBuff = ctypes.create_string_buffer(inputString.encode('utf-8'))
        plainLen = ctypes.c_int(len(plainBuff.value))

        cipherBuff = ctypes.c_char_p()
        cipherLen = ctypes.c_int()
        # print("当前的明文密钥为：", self.dekey)
        keyBuff = ctypes.create_string_buffer(self.dekey.encode('utf-8')) 
        ret = self.lib.lu_encrypt(plainBuff, plainLen, ctypes.byref(cipherBuff), ctypes.byref(cipherLen), keyBuff)  # 使用明文密钥进行加密
        if ret == 0:
            # print("加密成功")
            encrypted_data = ctypes.string_at(cipherBuff, cipherLen.value)
            # print("Encrypted data: ", encrypted_data)
            # print("Length of encrypted data: ", cipherLen.value)
        else:
            print("加密失败")
        print("self.dekey: ", self.dekey)
        print("加密后的数据：", encrypted_data)
        # 十六进制字符串 'aa55' 对应的字节
        prefix = bytes.fromhex('aa55')
        
        length = cipherLen.value
        
        print(cipherLen.value)
        # 添加到后面，长度占用4个字节，不足4个字节的话，前面补0
        prefix += length.to_bytes(4, byteorder='big', signed=False)
        # 然后连接这个前缀和你的加密数据
        new_encrypted_data = prefix + encrypted_data
        

        return new_encrypted_data, cipherLen.value

    @timer_decorator
    def decrypt(self, cipherBuff, cipherLen=-1):
        """
        解密给定的密文。

        Args:
            cipherBuff (ctypes.c_char_p): 密文。
            cipherLen (int): 密文长度。

        Returns:
            tuple: 包含解密后的数据和解密后数据的长度。
        """
        # 取前4个字节，转成int，得到长度
        length = int.from_bytes(cipherBuff[:4], byteorder='big', signed=False)
        print("length: ", length)
        if cipherLen==-1:
            cipherLen = length
        print(f"cipherLen:{cipherLen}")
        cipherBuff = cipherBuff[4:]
        self.lib.lu_decrypt.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_int)]
        self.lib.lu_decrypt.restype = ctypes.c_int

        plainBuff = ctypes.c_char_p()
        plainLen = ctypes.c_int()

        keyBuff = ctypes.create_string_buffer(self.dekey.encode('utf-8')) 
        ret = self.lib.lu_decrypt(cipherBuff, cipherLen, ctypes.byref(plainBuff), ctypes.byref(plainLen), keyBuff)  # 使用明文密钥进行解密
        if ret == 0:
            # print("解密成功")
            print(plainBuff.value)
            decryptedString = plainBuff.value.decode('utf-8')
            # print("Decrypted data: ", decryptedString)
            # print("Length of decrypted data: ", plainLen.value)
        else:
            print("解密失败")

        return decryptedString, plainLen.value

    def createGroupAndApplyKey(self):
        """
        创建组并获取组密钥。

        Returns:
            str: 组ID。
        """
        self.lib.lu_createGroupAndApplyKey.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
        self.lib.lu_createGroupAndApplyKey.restype = ctypes.c_int

        groupKeyLen = 14
        groupMembersCnt = 2

        members_info = [
            {"appType": 60, "appAccount": "test00", "cspID": "cspID1"},
            {"appType": 60, "appAccount": "test01", "cspID": "cspID2"}
        ]

        inputString = f"{groupMembersCnt}"
        for member in members_info:
            inputString += f",{member['appType']},{member['appAccount']},{member['cspID']}"

        inputString = inputString.encode('utf-8')

        backgroupID_ptr = ctypes.c_char_p()
        backgroup_id = ""

        ret = self.lib.lu_createGroupAndApplyKey(inputString, ctypes.byref(backgroupID_ptr))
        if ret == 0:
            print("创建组并获取组密钥成功")
            try:
                backgroup_id = backgroupID_ptr.value.decode('utf-8')
                print("backgroupID:", backgroup_id)
            except UnicodeDecodeError as e:
                print("解析 backgroupID 失败: ", e)
            finally:
                ctypes.cdll.LoadLibrary("libc.so.6").free(backgroupID_ptr)
        else:
            print("创建组并获取组密钥失败")
        return backgroup_id

    def destoryKey(self):
        """
        销毁密钥。
        """
        self.lib.destoryKey.argtypes = []
        self.lib.destoryKey.restype = ctypes.c_int

        ret = self.lib.destoryKey()

        if ret == 0:
            print("销毁密钥成功")
        else:
            print("销毁密钥失败")

    def getGroupKey(self, groupID):
        """
        根据组ID获取组密钥。

        Args:
            groupID (str): 组ID。

        Returns:
            None
        """
        self.lib.lu_getGroupKey.argtypes = [ctypes.c_char_p]
        self.lib.lu_getGroupKey.restype = ctypes.c_int

        ret = self.lib.lu_getGroupKey(groupID.encode('utf-8'))

        if ret == 0:
            print("根据组ID获取组密钥成功")
        else:
            print("根据组ID获取组密钥失败")

    def write_key_to_file(self, key, filename='key.txt'):
        """
        将密钥写入文件。

        Args:
            key (str): 密钥。
            filename (str, optional): 文件名，默认为'key.txt'。
        """
        # int 直接写入
        with open(filename, 'w') as f:
            f.write(str(key))
        
       

    def read_key_from_file(self, filename='key.txt'):
        """
        从文件中读取密钥。

        Args:
            filename (str, optional): 文件名，默认为'key.txt'。

        Returns:
            str: 读取的密钥。
        """
        with open(filename, 'r') as f:
            hex_key = f.read()
        return int(hex_key)

    def exportSessionKey(self):
        """
        导出会话密钥或组密钥。

        Returns:
            str: 导出的密钥。
        """
        # ...

        key = self.lib.lu_exportSessionKey()
        if key == None:
            print("导出会话密钥或组密钥失败")
        else:
            print("导出会话密钥或组密钥成功")
            self.write_key_to_file(key)  # 将密钥写入文件
            key = self.read_key_from_file()  # 从文件中读取密钥
            
        return key

if __name__ == "__main__":
    tsdk = Dxr_Crypto("60", "lch6@quantum.com", "12345678", "13988888888", "qkeys.cn")
    if tsdk.dekey == None:
        bid = tsdk.createGroupAndApplyKey()
        if bid == "":
            print("创建组并获取组密钥失败")
        else:
            print("创建组并获取组密钥成功")
            tsdk.getGroupKey(bid)
        key = tsdk.exportSessionKey()
    else:
        key = tsdk.dekey
    print("key: ", key)
    while True:
        inputString = input("请输入要加密的字符串：")
        if inputString == "exit":
            break
        if inputString == "":
            inputString = "hello world"
        cipherBuff, cipherLen = tsdk.encrypt(inputString)
        decryptedString, plainLen = tsdk.decrypt(cipherBuff, cipherLen)
        print(f'加密前的字符串：{inputString}, 加密后的字符串：{cipherBuff}, 解密后的字符串：{decryptedString}')
        print(f"加密前和解密后的字符串是否相等：{inputString == decryptedString}")
    tsdk.destoryKey()
    print("test.py end")