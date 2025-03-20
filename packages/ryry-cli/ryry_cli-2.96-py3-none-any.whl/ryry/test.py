import wx
import os

class DragPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        # 要被拖拽出去的文件路径（示例：本地的某个文件）
        self.file_path = "/Users/pengjun/Downloads/Mohini.jpg"
        self.file_path2 = "/Users/pengjun/Downloads/Krishna.png"

        # 在面板上放一个静态文本做示例
        self.label = wx.StaticText(self, label="按住这里把文件拖到微信/QQ/Explorer等")
        # 布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 0, wx.ALL|wx.ALIGN_CENTER, 10)
        self.SetSizer(sizer)

        # 绑定鼠标事件：左键按下开始拖拽
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)

    def on_left_down(self, event):
        """
        当用户在面板上按下鼠标左键时，启动一次拖拽操作。
        """
        if not os.path.isfile(self.file_path):
            print("文件不存在，无法拖拽：", self.file_path)
            return

        # 创建一个 FileDataObject 对象，并添加文件
        data_obj = wx.FileDataObject()
        data_obj.AddFile(self.file_path)
        data_obj.AddFile(self.file_path2)


        # 创建一个 DropSource，设置 data_obj 为其数据对象
        drop_source = wx.DropSource(self)
        drop_source.SetData(data_obj)

        # 执行拖拽操作
        result = drop_source.DoDragDrop(wx.Drag_AllowMove)
        # result 可用于查看拖拽结果，如成功/取消/移动等
        print("拖拽结果：", result)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Drag File Demo", size=(400, 200))
        panel = DragPanel(self)
        self.Show()

if __name__ == "__main__":
    app = wx.App(False)
    MainFrame()
    app.MainLoop()