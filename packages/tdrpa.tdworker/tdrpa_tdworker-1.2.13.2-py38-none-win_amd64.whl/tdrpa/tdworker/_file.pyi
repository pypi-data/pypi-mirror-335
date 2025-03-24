class INI:
    @staticmethod
    def Read(iniPath: str, sectionName: str, keyName: str, defaultValue: str = '', encoding: str = 'GBK') -> str:
        """
        读键值

        value = INI.Read('D:\\conf.ini','section1', 'key1', defaultValue='', encoding='GBK')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param keyName:[必选参数]要访问 INI 配置文件的键名
        :param defaultValue:[可选参数]当 INI 配置文件键名不存在时，返回的默认内容。默认是空字符串
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: 返回读取的值，字符串类型
        """
    @staticmethod
    def Write(iniPath: str, sectionName: str, keyName: str, value, encoding: str = 'GBK') -> None:
        """
        写键值

        INI.Write('D:\\conf.ini','section1', 'key1', 'value1', encoding='GBK')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param keyName:[必选参数]INI 文件中被写入的键值对中的键名，若为空字符串，则此键值对不被写入
        :param value:[必选参数]INI 文件中被写入的键值对中的键值
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: None
        """
    @staticmethod
    def EnumSection(iniPath: str, encoding: str = 'GBK') -> list:
        """
        枚举小节

        sections = INI.EnumSection('D:\\conf.ini', encoding='GBK')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: 返回一个列表，列表中每个元素为一个section的名字
        """
    @staticmethod
    def EnumKey(iniPath: str, sectionName: str, encoding: str = 'GBK') -> list:
        """
        枚举键

        keys = INI.EnumKey('D:\\conf.ini', 'section1', encoding='GBK')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: 返回一个列表，列表中每个元素为一个key的名字
        """
    @staticmethod
    def DeleteSection(iniPath: str, sectionName: str, encoding: str = 'GBK') -> None:
        """
        删除小节

        INI.DeleteSection('D:\\conf.ini','section1', encoding='GBK')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: None
        """
    @staticmethod
    def DeleteKey(iniPath: str, sectionName: str, keyName: str, encoding: str = 'GBK'):
        """
        删除键

        INI.DeleteKey('D:\\conf.ini','section1', 'key1', encoding='GBK')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param keyName:[必选参数]要访问 INI 配置文件的键名
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: None
        """
