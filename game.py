# -*- coding: utf-8 -*-
"""
Created on Thu May 26 09:23:38 2022

@author: 86180
"""

import os
import sys
from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QPushButton

from panda3d.core import *
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
import time

class Ui_browse(QDialog):
    def __init__(self):
        super().__init__()
        self.setGeometry(400,400,500,200)
        self.setWindowTitle("游戏结束")
        self.closed = QPushButton('关闭', self)
        self.closed.setGeometry(350, 15, 100, 30)
        self.closed.clicked.connect(self.close)

#一些基础设置（具体panda3d官网可查）
ConfVar="""win-size 1280 720
       window-title GAME"""
loadPrcFileData=(" ", ConfVar)#加载基础设置
keymap = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "rise": False,
    "fall": False,
    "acc": False,
    "change": False,
    "fp": True,
    "tp": False,
}#按键状态

def updateKeyMap(key, state):#上传按键状态
    keymap[key] = state

class MyApp(ShowBase):#该类为游戏主题
    loadPrcFile=("config/PRC")#加载基础设置
    def __init__(self):
        ShowBase.__init__(self) 

        # 禁用鼠标
        self.disableMouse()

        # 隐藏鼠标
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        # 设定摄像机初始位置
        self.camera.setPos(-40,-40, 300)

        # 载入环境模型
        #self.environ = self.loader.loadModel("models/environment")
        self.environ = self.loader.loadModel("mymodel/untitled2")

        #载入飞机模型
        self.plane = self.loader.loadModel("mymodel2/plane")
        self.plane.reparentTo(self.render)
        self.plane.setPos(0, 30, 80)

        # 设置环境模型的父实例
        self.environ.reparentTo(self.render)

        # 对模型进行比例及位置调整
        #self.environ.setScale(0.25, 0.25, 0.25)
        #self.environ.setPos(-8, 42, 0)
        self.environ.setScale(40, 40, 40)
        self.environ.setPos(30, 20, 0)
     

        # 设置键盘映射
        self.accept("a", updateKeyMap, ["left", True])
        self.accept("a-up", updateKeyMap, ["left", False])
        self.accept("d", updateKeyMap, ["right", True])
        self.accept("d-up", updateKeyMap, ["right", False])
        self.accept("w", updateKeyMap, ["up", True])
        self.accept("w-up", updateKeyMap, ["up", False])
        self.accept("s", updateKeyMap, ["down", True])
        self.accept("s-up", updateKeyMap, ["down", False])
        self.accept("space", updateKeyMap, ["rise", True])
        self.accept("space-up", updateKeyMap, ["rise", False])
        self.accept("control", updateKeyMap, ["fall", True])
        self.accept("control-up", updateKeyMap, ["fall", False])
        self.accept("shift", updateKeyMap, ["acc", True])
        self.accept("shift-up", updateKeyMap, ["acc", False])
        self.accept("mouse3", updateKeyMap, ["change", True])
        self.accept('escape', self.Exit)

        # 通知任务管理器调用SpinCameraTask控制相机
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")


        # 创建HUD（第一人称）
        global X1, X2, text, text2, L1, L2l, L2r, Sc1, Sc2, Ls, Su, Sd
        if keymap["fp"]:
            text = OnscreenText(fg=(255, 255, 0, 255), pos=(-0.1, -0.1), scale=0.1, mayChange=True)
            text2 = OnscreenText(pos=(-0.7, 0), scale=0.1, mayChange=True)
            Sc1 = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(-0.04, 0.04, -0.002, 0.002), pos=(0, 0, 0))
            Sc2 = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(-0.002, 0.002, -0.04, 0.04), pos=(0, 0, 0))
            X1 = DirectFrame(frameColor=(0, 0, 0, 255), frameSize=(-0.04, 0.04, -0.002, 0.002), pos=(0, 0, 0))
            X2 = DirectFrame(frameColor=(0, 0, 0, 255), frameSize=(-0.002, 0.002, -0.04, 0.04), pos=(0, 0, 0))
            Ls = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(-0.5, -0.51, 0.5, -0.5), pos=(0, 0, 0))
            L1 = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(0.2, 0.11, 0.005, -0.005), pos=(0, 0, 0))
            L2l = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(-0.1, -0.04, 0.002, -0.002), pos=(0, 0, 0))
            L2r = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(0.04, 0.1, 0.002, -0.002), pos=(0, 0, 0))
            Su = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(-0.1, 0.1, 0.002, -0.002), pos=(0, 0, 0.5))
            Sd = DirectFrame(frameColor=(255, 255, 0, 255), frameSize=(-0.1, 0.1, 0.002, -0.002), pos=(0, 0, -0.5))

    #退出函数
    def Exit(self):
       os._exit(0)

    # 定义旋转相机
    def spinCameraTask(self, task):
        #读取鼠标在窗口中的位置
        (mouse, size) = (base.win.getPointer(0), self.get_size())
        (mx0, my0) = (size[0] - mouse.getX(), mouse.getY())
        (mx, my) = (mx0 / 160, my0 / 160)

        if keymap["tp"]:
            self.plane.setScale(0.25, 0.25, 0.25)
            hpr = self.plane.getHpr()#若是第三人称，选取飞机视角的hpr
            (rx, ry) = (mx - size[0] / 320 + hpr[0], my - size[1] / 320 + hpr[1])#根据鼠标位置旋转镜头
        else:
            self.plane.setScale(0, 0, 0)
            hpr = self.camera.getHpr()#若是第一人称，选取镜头视角的hpr
            (rx, ry) = (mx - size[0] / 320 + hpr[0], -my + size[1] / 320 + hpr[1])

        pos = self.camera.getPos()#读取相机坐标
        (lx, ly, lz) = (pos[0], pos[1], pos[2])
        pos1 = self.plane.getPos()#读取飞机坐标
        (lx1, ly1, lz1) = (pos1[0], pos1[1], pos1[2])
        (angle, angle2) = (hpr[0], hpr[1])#读取hpr

        if keymap["acc"]:
            distance = 1.8#按“shift”加速后改变步长（可调）
        else:
            distance = 0.6#正常状态下步长

        #保证欧拉角在0到360度之间
        if angle < 0:
            while angle < 0:
                angle = angle + 360
        else:
            angle = angle % 360

        if angle2 < 0:
            while angle2 < 0:
                angle2 = angle2 + 360
        else:
            angle2 = angle2 % 360

        #单步长在x,y轴的投影长度（z轴另作计算）
        distance2 = cos(angle2 * pi / 180) * distance

        #防止欧拉角自锁
        if angle % 90 == 0:
            if angle == 0:
                (ax, ay) = (0, 1)
                (x, y) = (0, distance2)
                (x_lor, y_lor) = (0, distance)
            elif angle == 90:
                (ax, ay) = (1, 0)
                (x, y) = (distance2, 0)
                (x_lor, y_lor) = (distance, 0)
            elif angle == 180:
                (ax, ay) = (0, -1)
                (x, y) = (0, -distance2)
                (x_lor, y_lor) = (0, -distance)
            else:
                (ax, ay) = (-1, 0)
                (x, y) = (-distance2, 0)
                (x_lor, y_lor) = (-distance, 0)
        else:
            #根据飞机/镜头角度调整在各轴的运动步长
            if angle <= 45:
                ax = sin(angle * pi / 180)
                ay = cos(angle * pi / 180)
            elif angle < 90:
                angle = 90 - angle
                ax = cos(angle * pi / 180)
                ay = sin(angle * pi / 180)
            elif angle <= 135:
                angle = angle - 90
                ax = cos(angle * pi / 180)
                ay = -sin(angle * pi / 180)
            elif angle < 180:
                angle = 180 - angle
                ax = sin(angle * pi / 180)
                ay = -cos(angle * pi / 180)
            elif angle <= 225:
                angle = angle - 180
                ax = -sin(angle * pi / 180)
                ay = -cos(angle * pi / 180)
            elif angle < 270:
                angle = 270 - angle
                ax = -cos(angle * pi / 180)
                ay = -sin(angle * pi / 180)
            elif angle < 315:
                angle = angle - 270
                ax = -cos(angle * pi / 180)
                ay = sin(angle * pi / 180)
            else:
                angle = 360 - angle
                ax = -sin(angle * pi / 180)
                ay = cos(angle * pi / 180)
            x = ax * distance2
            y = ay * distance2
            x_lor = ax * distance
            y_lor = ay * distance

        #z轴步长单独计算（方法同上）
        if angle2 % 90 == 0:
            if angle2 == 0:
                az = 0
                az1 = 1
                z = distance
            elif angle2 == 90:
                az = 1
                az1 = 0
                z = distance
            elif angle2 == 180:
                az = 0
                az1 = -1
                z = 0
            else:
                az = -1
                az1 = 0
                z = 0
        else:
            if angle2 <= 45:
                az = sin(angle2 * pi / 180)
                az1 = cos(angle2 * pi / 180)
            elif angle2 < 90:
                angle2 = 90 - angle2
                az = cos(angle2 * pi / 180)
                az1 = sin(angle2 * pi / 180)
            elif angle2 <= 135:
                angle2 = angle2 - 90
                az = cos(angle2 * pi / 180)
                az1 = -sin(angle2 * pi / 180)
            elif angle2 < 180:
                angle2 = 180 - angle2
                az = sin(angle2 * pi / 180)
                az1 = -cos(angle2 * pi / 180)
            elif angle2 <= 225:
                angle2 = angle2 - 180
                az = -sin(angle2 * pi / 180)
                az1 = -cos(angle2 * pi / 180)
            elif angle2 < 270:
                angle2 = 270 - angle2
                az = -cos(angle2 * pi / 180)
                az1 = -sin(angle2 * pi / 180)
            elif angle2 < 315:
                angle2 = angle2 - 270
                az = -cos(angle2 * pi / 180)
                az1 = sin(angle2 * pi / 180)
            else:
                angle2 = 360 - angle2
                az = -sin(angle2 * pi / 180)
                az1 = cos(angle2 * pi / 180)
            z = az * distance
        zo = 1.2 * distance

        # 响应第三人称的键盘映射
        if keymap["tp"]:
            if keymap["up"] and keymap["left"]:
                self.plane.setPos(x + 0.4 * y_lor + lx1, -y + 0.4 * x_lor + ly1, -z + lz1)
            elif keymap["up"] and keymap["right"]:
                self.plane.setPos(x - 0.4 * y_lor + lx1, -y - 0.4 * x_lor + ly1, -z + lz1)
            elif keymap["down"] and keymap["left"]:
                self.plane.setPos(-x + 0.4 * y_lor + lx1, y + 0.4 * x_lor + ly1, z + lz1)
            elif keymap["down"] and keymap["right"]:
                self.plane.setPos(-x - 0.4 * y_lor + lx1, y - 0.4 * x_lor + ly1, z + lz1)
            elif keymap["up"]:
                self.plane.setPos(x + lx1, -y + ly1, -z + lz1)
            elif keymap["down"]:
                self.plane.setPos(-x + lx1, y + ly1, z + lz1)
            elif keymap["left"]:
                self.plane.setPos(0.4 * y_lor + lx1, 0.4 * x_lor + ly1, lz1)
            elif keymap["right"]:
                self.plane.setPos(-0.4 * y_lor + lx1, -0.4 * x_lor + ly1, lz1)
            if keymap["rise"]:
                self.plane.setPos(lx1, ly1, zo + lz1)
            if keymap["fall"]:
                self.plane.setPos(lx1, ly1, -zo + lz1)

        # 响应第一人称的键盘映射
        if keymap["fp"]:
            if keymap["up"] and keymap["left"]:
                self.camera.setPos(-x - 0.4 * y_lor + lx, y - 0.4 * x_lor + ly, z + lz)
            elif keymap["up"] and keymap["right"]:
                self.camera.setPos(-x + 0.4 * y_lor + lx, y + 0.4 * x_lor + ly, z + lz)
            elif keymap["down"] and keymap["left"]:
                self.camera.setPos(x - 0.4 * y_lor + lx, -y - 0.4 * x_lor + ly, -z + lz)
            elif keymap["down"] and keymap["right"]:
                self.camera.setPos(x + 0.4 * y_lor + lx, -y + 0.4 * x_lor + ly, -z + lz)
            elif keymap["up"]:
                self.camera.setPos(-x + lx, y + ly, z + lz)
            elif keymap["down"]:
                self.camera.setPos(x + lx, -y + ly, -z + lz)
            elif keymap["left"]:
                self.camera.setPos(-0.4 * y_lor + lx, -0.4 * x_lor + ly, lz)
            elif keymap["right"]:
                self.camera.setPos(0.4 * y_lor + lx, 0.4 * x_lor + ly, lz)
            if keymap["rise"]:
                self.camera.setPos(lx, ly, zo + lz)
            if keymap["fall"]:
                self.camera.setPos(lx, ly, -zo + lz)
            text2['text'] = str(int(z + lz))

            #根据当前位置，朝向调整hud显示的数值
            if z + lz > 100:
                L1.setPos(-0.7, 0, 0.5)
                text2['pos'] = (-0.7, 0.48)
            else:
                L1.setPos(-0.7, 0, (z + lz) / 100 - 0.5)
                text2['pos'] = (-0.7, (z + lz) / 100 - 0.52)
            if z + lz < 11:
                text2['fg'] = (255, 0, 0, 255)
            elif z + lz < 31:
                text2['fg'] = (0, 255, 255, 255)
            else:
                text2['fg'] = (255, 255, 0, 255)

        if keymap["tp"]:
            # 在飞机撞地时结束游戏
            if lz1 < -1:
                self.closeWindow(self.win)#关闭游戏界面

                #若不注释这一行则以报错形式退出
                #raise RuntimeError('You crash the ground!')

                #弹出游戏结束页面（可改进）
                if __name__ == "__main__":
                    app = QApplication(sys.argv)
                    window = Ui_browse()
                    window.show()
                    sys.exit(app.exec_())

            # 转换为第三人称后转为飞机视角
            self.plane.setHpr(rx, ry, 0)

            #第三人称下，在移动镜头时通过延时实现拖曳感（可调，可关）
            time.sleep(0.01)

            #以下两行为相机相对于飞机的角度（可选）（第一行是相机在飞机后方的45度俯视，第二行是相机在飞机正后方）
            #self.camera.setPos(lx1 - 20 * az1 * ax + 20 * az * ax, ly1 + 20 * az1 * ay - 20 * az * ay, lz1 + 20 * az + 20 * az1)
            self.camera.setPos(lx1 - 20 * az1 * ax, ly1 + 20 * az1 * ay, lz1 + 20 * az)
            rx1 = rx - 180

            # 以下两行为相机相对于飞机的角度（同上）
            #ry1 = -ry - 45
            ry1 = -ry

            #旋转相机
            self.camera.setHpr(rx1, ry1, 0)

        else:#转换为第一人称后初始化视角
            # 在飞机撞地时结束游戏（同上）
            if lz < -1:
                self.closeWindow(self.win)#关闭游戏界面

                # 若不注释这一行则以报错形式退出（同上）
                #raise RuntimeError('You crash the ground!')

                # 弹出游戏结束页面（同上）
                if __name__ == "__main__":
                    app = QApplication(sys.argv)
                    window = Ui_browse()
                    window.show()
                    sys.exit(app.exec_())

            # 转换为第三人称后转为相机视角
            self.camera.setHpr(rx, ry, 0)

        #保证ry在0到360度之间
        if ry >= 360:
            while ry >= 360:
                ry = ry - 360
        elif ry < 0:
            while ry < 0:
                ry = ry + 360
        if ry // 180 == 0:
            ry = ry
        elif ry // 180 == 1:
            ry = ry - 360

        # 根据当前位置，朝向调整hud中移动线条的显示
        if keymap["fp"]:
            L2l.setPos(0, 0, ry / 180)
            L2r.setPos(0, 0, ry / 180)
            b = size[1] / 2
            a = mouse.getX() / b - size[0] / size[1], 0, 1 - mouse.getY() / b
            X1.setPos(a)
            X2.setPos(a)
            text['text'] = str(int(ry))


        if keymap["change"]:
            if keymap["fp"]:
                #转换人称后更新按键状态
                keymap.update({"fp": False})
                keymap.update({"tp": True})

                #转换人称后更新飞机的位置和朝向
                self.plane.setPos(lx, ly, lz)
                self.plane.setHpr(rx + 180, -ry, 0)

                # 转换为第三人称后隐藏第一人称的仰角/高度显示
                text.setScale(0)
                text2.setScale(0)
                X1.setScale(0)
                X2.setScale(0)
                L1.setScale(0)
                L2l.setScale(0)
                L2r.setScale(0)
                Sc1.setScale(0)
                Sc2.setScale(0)
                Ls.setScale(0)
                Su.setScale(0)
                Sd.setScale(0)

            else:
                # 转换人称后更新按键状态
                keymap.update({"fp": True})
                keymap.update({"tp": False})

                # 转换人称后更新相机的位置
                self.camera.setPos(lx1, ly1, lz1)

                # 转换为第一人称后恢复第一人称的仰角/高度显示
                text.setScale(0.1)
                text2.setScale(0.1)
                X1.setScale(1)
                X2.setScale(1)
                L1.setScale(1)
                L2l.setScale(1)
                L2r.setScale(1)
                Sc1.setScale(1)
                Sc2.setScale(1)
                Ls.setScale(1)
                Su.setScale(1)
                Sd.setScale(1)

            keymap.update({"change": False})

        return Task.cont

MyApp().run()
