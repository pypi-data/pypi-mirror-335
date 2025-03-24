class Clipboard:
    @staticmethod
    def GetText():
        """
        读取剪贴板文本

        Clipboard.GetText()

        :return:剪贴板的文本内容
        """
    @staticmethod
    def SaveImage(savePath: str):
        '''
        保存剪贴板图像

        Clipboard.SaveImage(savePath)

        :param savePath:[必选参数]要将剪贴板的图像保存到的文件路径，如"D:\\1.png"
        :return:图像保存成功返回True，保存失败返回False
        '''
    @staticmethod
    def SetFile(paths: str | list):
        '''
        文件设置到剪贴板

        Clipboard.SetFile(paths)

        :param paths:[必选参数]文件的路径，单个文件用字符串类型，如"D:\x01.txt"，多个文件用 list 类型，其中每个元素用字符串，如["D:\x01.txt", "D:\x01.png"]
        :return:成功返回True，失败返回False
        '''
    @staticmethod
    def SetImage(picPath):
        '''
        图片设置到剪贴板

        Clipboard.SetImage(picPath)

        :param picPath:[必选参数]要放入剪贴板的图片路径，如"D:\\1.png"
        :return:成功返回True，失败返回False
        '''
    @staticmethod
    def SetText(content: str = ''):
        '''
        设置剪贴板文本

        Clipboard.SetText(\'\')

        :param content:[必选参数]新的剪贴板文本内容，默认""
        :return:成功返回True，失败返回False
        '''
