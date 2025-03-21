f_time = 20250321.1
print(f_time)

def install_package_with_pip(pip_executable_path=r"D:\Python313\Scripts\pip.exe", package_name="pandas"):
    """
    使用指定的pip可执行文件路径和包名来安装Python包。
    
    :param pip_executable_path: pip可执行文件的路径，默认为D盘Python3.13版本的pip路径
    :param package_name: 要安装的包名，默认为pandas
    """
    #from frankyu import frankyu  # 从frankyu模块中导入frankyu对象
    
    #mirror_source = frankyu.qinghua  # 获取清华镜像源URL
    mirror_source = r"https://pypi.tuna.tsinghua.edu.cn/simple/"  # 获取清华镜像源URL
    language_pack = "jupyterlab-language-pack-zh-CN"  # 定义一个语言包名
    print("Language Pack:", language_pack)  # 打印语言包名
    print("Package Name:", package_name)  # 打印要安装的包名
    
    # 构造pip命令字符串
    pip_command = f"{pip_executable_path} install -i {mirror_source} {package_name}"
    print(pip_command)  # 打印构造的pip命令字符串
    import os
    os.system(pip_command)  # 执行pip命令
    print("Installation Complete")  # 安装完成提示

def install_package_with_python310_default_pip(package_name="xlwings"):
    """
    使用默认的Python 3.10 pip可执行文件路径来安装指定的包。
    
    :param package_name: 要安装的包名，默认为xlwings
    """
    # 调用install_package_with_pip函数，指定Python 3.10的pip路径
    install_package_with_pip(pip_executable_path=r"C:\Users\Public\Python310\Scripts\pip.exe", package_name=package_name)



def startT(pan = "T:"):
    import os
    conm = "start " + pan
    os.system(conm)
    print(pan,"已经成功打开")
    import time
    time.sleep(2)


def shijinzhi2other(shi,jishu):
    shijinzhi = [i for i in range(0,10+26)]
    shiliu = [str(i) for i in range(0,10)] + [i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    dic = dict(zip(shijinzhi,shiliu))   #字典对照表
    lis = []          #先做成列表,再做成字符串
    shang = 100   #声明变量,只要不是零就可以,随便
    st = ""    #需要返回的结果    
    while shang !=0:   #变成0,循环停止    
        shang = (  shi//jishu)    #求商并向下取整
        yu = shi - shang * jishu    #求余数
        lis.append(dic[yu])    # 余数映射十六进制 让后加入空列表
        #print(lis)
        shi = shang          # 余数变成十进制数字,进行下一个循环
    for j in list( reversed(lis)):      #列表反向
        st+=  str(j)               # 空字符串自己增加
        #print(st)
    return st                #返回转换后的数字


def gbc(cheng_xu="chrome"):
    import subprocess
    import os
    a = "tasklist"
    c = subprocess.run(a, stdout=subprocess.PIPE, shell=True, text=True)
    b = c.stdout

    with open("data.txt", "w") as f:
        f.write(b)
        f.close()



    zt = "pause"
    zt = ""
    os.system(zt)

    m = [cheng_xu, ]

    for i in m:
        # i = " edge "
        # for i in m:
        d = '   findstr /i ' + i + ' data.txt  ' + "     >  data4.txt "
        print(d)
        zt = "pause"
        zt = ""
        # os.system(zt)

        os.system(d)
        print(d + "執行成功,data4已經生成")

        # g = 'for /f "tokens=2" %b in (data2.txt)  do taskkill /f /t /pid %b  '
        """
        p = 'for /f "tokens=2" %b in (data4.txt)  do type %b >"data3.txt"   '

        print(p)

        os.system(zt)
        print("data3.txt")
        """
        os.system(zt)

        g = 'for /f "tokens=2" %b in (data4.txt)  do taskkill /f /t /pid %b  '

        print(g)

        print("警告")
        os.system(zt)

        # j =  subprocess.run(g,stdout=subprocess.PIPE,shell=True,text=True)
        j = subprocess.getoutput(g)
        print(i + "已經成功關閉")
        import time

        time.sleep(0.3)

        # k = e.stdout

 


 

def dao_ji_shi(aaaa):
    dddd = aaaa
    while dddd > 0:
        print(f"\r倒計時{dddd}",end="\n")
        import time
        time.sleep(1)
        dddd = dddd -1
 

cc = r"C:\Users\frank_yu" + "\\" + "cqzy.bat"
cc = "cqzy.bat"


import subprocess
#subprocess.Popen(cc, shell=True, stdout=subprocess.PIPE)



def dianliang():
    

    import psutil
    battery = psutil.sensors_battery()
    if battery is None:
        print("No battery is found.")
        exit()
    print (battery)
    percentage=battery.percent
    print(f"Battery Percentage: {percentage}%")


def jietu2mail():
    jietu_file = r"C:\Users\Public\jietu.bmp"
    
    
    import win32gui
    import win32ui
    import win32con
    import win32api
    
    
    import time
    
    # 获取桌面
    hdesktop = win32gui.GetDesktopWindow()
    # 分辨率适应
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    # 创建设备描述表
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    # 创建一个内存设备描述表
    mem_dc = img_dc.CreateCompatibleDC()
    # 创建位图对象
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)
    
    
    
    import win32gui
    import win32con
    
    
    hw = win32gui.FindWindow(None,r"C:\Windows\py.exe")
    
    win32gui.ShowWindow(hw,win32con.SW_SHOWMINIMIZED)
    
    
    time.sleep(0.9)
    
    
    
    
    # 截图至内存设备描述表
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)
    # 将截图保存到文件中
    screenshot.SaveBitmapFile(mem_dc, jietu_file)
    # 内存释放
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())
    
    
    import win32com.client
    
    
    # In[2]:
    
    
    app = win32com.client.Dispatch("outlook.application")
    
    
    # In[3]:
    
    
    app
    
    
    # In[4]:
    
    
    mail = app.CreateItem(0)
    
    
    # In[5]:
    
    
    mail
    
    
    # In[6]:
    
    
    mail.To = "yufengguang@hotmail.com"
    mail.CC = "frank_yu@prime3c.com"
    
    
    # In[8]:
    
    import datetime
    
    jt = datetime.datetime.now()
    jt= str(jt).replace(" ","").replace("-","").replace(":","").replace(".","").\
    replace("","")
    
    
    mail.Subject = "截图"+jt
    fujian = jietu_file
    
    
    # In[9]:
    
    
    mail.Attachments.Add(fujian)
    
    
    # In[10]:
    
    
    #mail.Display()
    
    
    # In[11]:
    
    
    mail.Body = "1"
    
    
    # In[12]:
    
    
    mail.Send()
    
    win32gui.ShowWindow(hw,win32con.SW_SHOWMAXIMIZED)
    
    
    print(jt,"发送成功")
    
    
    time.sleep(2)
    

def importf(aaa = "C:\\Users\\admin\\OneDrive\\sb_yufengguang\\sb_py"):

    import sys
    path2 = sys.path
    import os
    print("根目录:",os.getcwd())
    path = aaa
    print("模块地址:",path)
    sys.path.append(path)



qinghua = r"https://pypi.tuna.tsinghua.edu.cn/simple"



def pipi(aaa="ipython"):

    import os
    com = r"pip install -i " + qinghua  + " " + aaa
    print(com)
    print("正在安裝下列第三方庫\n",aaa)
    os.system(com)


def jiantieban_get():
    import win32clipboard
    

    # get clipboard data
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    #print(data)
    return data








print(pipi)



def new_excel():
    import win32com.client
    
    app = win32com.client.DispatchEx("excel.application")
    
    import os
    app.Visible = 1
    
    book = app.Workbooks.Add()
    
    
    import datetime
    aaa = str(datetime.datetime.now()).replace("-","").replace(" ","").replace(":","").replace(".","")
    aaa =  aaa +r".xlsx"
    aaa =  os.path.join("T:\\", "xls" ,aaa)
                        
    
    book.SaveAs(aaa)
    
    book.Saved
    
    book



import time

def countdown(t):
    """
    倒计时函数，接受一个整数 t 作为倒计时的秒数。
    修改：现在可以正确显示年、天、小时、分钟和秒数，格式为 YY:DD:HH:MM:SS。
    设定每年为 365 天，不考虑闰年。
    """
    while t:
        years, remainder = divmod(t, 31536000)   # 计算年数，31536000 秒/年 (365 * 24 * 3600)
        days, remainder = divmod(remainder, 86400)    # 从余数中计算天数，86400 秒/天
        hours, remainder = divmod(remainder, 3600) # 从余数中计算小时，3600 秒/小时
        mins, secs = divmod(remainder, 60)     # 从余数中计算分钟和秒
        timer = '{:02d}:{:02d}:{:02d}:{:02d}:{:02d}'.format(years, days, hours, mins, secs) # 修改：格式化字符串，现在显示年、天、小时、分钟和秒，YY:DD:HH:MM:SS 格式
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

    print('倒计时结束!')

# 设置倒计时时间为一个较大的值，例如 31622460 秒 (约 1 年 1 天 1 分钟 0 秒) 来测试包含年份的情况
t = 31622460
#countdown(int(t))

def daoJiShi_t2(t=20):
    print(r"YY:DD:HH:MM:SS")
    import time
    countdown(t)



def f_os_system(aaa = "shutdown -l"):
        
    
    import time
    
    #aaa = "shutdown -t -s 3600"
    import os
    print(aaa)
    time.sleep(2)
    
    
    os.system(aaa)


if __name__ == '__main__':
    #jiantieban_get()
    

    #jietu2mail()
    

    #guanbi_time = 3
    #print(f"{guanbi_time}s 后关闭")
    #dao_ji_shi(guanbi_time)
    #dianliang()
    importf()
    #new_excel()
    daoJiShi_t2(3600*24+60)
