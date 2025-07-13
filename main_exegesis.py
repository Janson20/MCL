'''Update Log
v1.0
start project
v1.1
add forge install
v1.2
add logs module
v1.3
add ui
v1.4
add mouse detect
'''
# 导入必要的库
import minecraft_launcher_lib  # Minecraft启动器库
import subprocess  # 用于运行外部命令
import tkinter as tk  # GUI库
import forgepy  # Forge安装库
import os  # 操作系统接口
import sys  # 系统相关功能
import requests  # HTTP请求库
import threading  # 多线程支持
import time  # 时间相关功能
import logzero  # 日志库
import pyautogui  # 自动化GUI操作
import threading  # 多线程支持(重复导入)
from tqdm import tqdm  # 进度条显示
from logzero import logger  # 日志记录器

# 配置日志系统
logzero.logfile("./latest.log")  # 设置日志文件路径
logzero.loglevel(logzero.INFO)  # 设置日志级别为INFO

# 全局变量用于跟踪下载进度
downloaded_bytes = 0  # 已下载字节数
total_size = 0  # 文件总大小
start_time = time.time()  # 下载开始时间
lock = threading.Lock()  # 线程锁，用于同步

def download_file_part(url, start_byte, end_byte, part_number, filename, progress_bar):
    """下载文件的分段部分"""
    global downloaded_bytes
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}  # 设置Range头实现分段下载
    response = requests.get(url, headers=headers, stream=True)  # 流式下载
    
    part_filename = f"{filename}.part{part_number}"  # 分段文件名
    with open(part_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):  # 分块写入
            if chunk:
                f.write(chunk)
                with lock:  # 加锁更新进度
                    downloaded_bytes += len(chunk)
                    progress_bar.update(len(chunk))

def merge_files(filename, num_parts):
    """合并分段下载的文件"""
    with open(filename, 'wb') as outfile:  # 创建最终文件
        for i in range(num_parts):
            part_filename = f"{filename}.part{i}"  # 分段文件名
            with open(part_filename, 'rb') as infile:  # 读取分段文件
                outfile.write(infile.read())  # 写入最终文件
            os.remove(part_filename)  # 删除临时分段文件

def main(url, num_threads=4):
    """多线程下载主函数"""
    global total_size, downloaded_bytes
    response = requests.head(url)  # 获取文件头信息
    total_size = int(response.headers['Content-Length'])  # 获取文件总大小
    
    part_size = total_size // num_threads  # 计算每个线程下载的大小
    threads = []  # 线程列表
    filename = url.split('/')[-1]  # 从URL提取文件名
    
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename)  # 创建进度条
    
    for i in range(num_threads):  # 创建并启动下载线程
        start_byte = i * part_size
        end_byte = start_byte + part_size - 1 if i < num_threads - 1 else total_size - 1
        thread = threading.Thread(target=download_file_part, args=(url, start_byte, end_byte, i, filename, progress_bar))
        threads.append(thread)
        thread.start()
    
    for thread in threads:  # 等待所有线程完成
        thread.join()
    
    progress_bar.close()  # 关闭进度条
    
    merge_files(filename, num_threads)  # 合并分段文件
    logger.info(f"文件下载成功: {filename}")  # 记录日志
    print(f"文件下载成功: {filename}")  # 打印信息
    return filename  # 返回下载的文件名

def forge_down(version):
    """下载指定版本的Forge"""
    latest = forgepy.GetLatestURL(version)  # 获取最新Forge下载URL
    file_url = latest
    fn = main(file_url, num_threads=4)  # 下载文件
    return fn  # 返回文件名

# Minecraft目录设置
minecraft_directory = os.getcwd()+"/.minecraft"  # Minecraft目录路径
options = minecraft_launcher_lib.utils.generate_test_options()  # 生成测试选项
current_max = 0  # 当前最大值(用于进度显示)

def set_status(status: str):
    """设置状态回调函数"""
    print(status)

def set_progress(progress: int):
    """设置进度回调函数"""
    if current_max != 0:
        print(f"{progress}/{current_max}")

def set_max(new_max: int):
    """设置最大值回调函数"""
    global current_max
    current_max = new_max

# 回调函数字典
callback = {
    "setStatus": set_status,
    "setProgress": set_progress,
    "setMax": set_max
}

def detect_mouse_move():
    """检测鼠标移动并记录位置"""
    with open("pos.txt","w+") as f:  # 打开位置记录文件
        try:
            while True:  # 持续检测
                x, y = pyautogui.position()  # 获取鼠标位置
                positionStr = str(x).rjust(5) + ' , ' + str(y).rjust(5)  # 格式化位置字符串
                f.write(positionStr+"\n")  # 写入文件
                print(positionStr, end='')  # 打印位置
                print('\b' * len(positionStr), end='', flush=True)  # 原地更新显示
                time.sleep(0.2)  # 短暂暂停
        except KeyboardInterrupt:  # 捕获Ctrl+C
            exit()

def show_version_list(versions):
    """显示带滚动条的版本选择窗口"""
    root = tk.Tk()
    root.title("版本列表")
    root.geometry("800x600")

    # 创建框架容器
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    # 创建滚动条
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 创建列表框
    listbox = tk.Listbox(
        frame, 
        yscrollcommand=scrollbar.set,
        font=("微软雅黑", 12),
        selectbackground="#4a6984",
        selectmode=tk.SINGLE
    )
    listbox.pack(fill=tk.BOTH, expand=True)

    # 填充数据
    for idx, version in enumerate(versions):
        listbox.insert(tk.END, f"{version['id']} ({version['type']})")

    # 配置滚动条
    scrollbar.config(command=listbox.yview)

    selected_version = [None]  # 用于存储选择结果的列表

    def on_select():
        """选择按钮回调函数"""
        try:
            selection = listbox.curselection()  # 获取当前选择
            if selection:
                selected_version[0] = versions[selection[0]]["id"]  # 存储选择的版本
            root.destroy()  # 关闭窗口
        except Exception as e:
            logger.error(f"选择版本时出错: {str(e)}")  # 记录错误

    # 添加选择按钮
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X, pady=5)

    select_btn = tk.Button(
        btn_frame, 
        text="选择",
        command=on_select,
        bg="#4a6984",
        fg="white",
        font=("微软雅黑", 12),
        width=10
    )
    select_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = tk.Button(
        btn_frame,
        text="取消",
        command=root.destroy,
        bg="#666666",
        fg="white",
        font=("微软雅黑", 12),
        width=10
    )
    cancel_btn.pack(side=tk.RIGHT, padx=10)

    root.mainloop()  # 启动主循环
    return selected_version[0]  # 返回选择的版本

def __main__():
    """主程序逻辑"""
    while True:
        try:
            logger.info("_________________________________新建实例_________________________________")
            print("正在检查文件夹...")
            if os.path.exists(minecraft_directory):  # 检查目录是否存在
                pass
            else:
                logger.warning("目录不存在")
                logger.info("首次使用")
                os.mkdir(minecraft_directory)  # 创建目录
                logger.info("目录创建成功")
                print("首次使用，正在下载正式版...")
                logger.info("正在下载正式版")
                minecraft_launcher_lib.install.install_minecraft_version(
                    minecraft_launcher_lib.utils.get_latest_version()["release"],
                    minecraft_directory,
                    callback=callback
                )  # 下载最新正式版
                logger.info("正式版下载成功")
            logger.info("文件夹检查完成")

            time.sleep(0.2)  # 短暂暂停

            while True:  # 主循环
                ins = pyautogui.confirm(text='是否安装新版本？', title='MCL启动器', buttons=['是', '取消'])
                if ins == "是":
                    logger.info("正在获取版本列表")
                    versions = minecraft_launcher_lib.utils.get_available_versions(minecraft_directory)
                    print("版本列表获取成功")
                    logger.info("版本列表获取成功")
                    
                    # 使用新版带滚动条的版本选择窗口
                    selected_version = show_version_list(versions)
                    
                    if not selected_version:  # 未选择版本
                        continue
                        
                    vs = selected_version.split()[0]  # 处理带类型说明的版本号
                    
                    avl = False
                    for v in versions:  # 检查版本是否可用
                        if v["id"] == vs:
                            avl = True

                    an = pyautogui.confirm(text='是否安装Forge？', title='Forge安装', buttons=['是', '取消'])
                    
                    if pyautogui.confirm(text='确认安装？', title='确认安装', buttons=['是', '取消']) == "是":
                        logger.info(f"正在安装Minecraft {vs}")
                        if an == "是":  # 安装Forge
                            logger.info(f"正在安装Forge {vs}")
                            filen = forge_down(vs)  # 下载Forge安装程序
                            logger.info(f"Forge {vs} 安装成功")
                            pyautogui.alert(text=f"安装程序下载成功，请运行 {filen} 完成Forge安装", title='Forge安装', button='确定')
                        minecraft_launcher_lib.install.install_minecraft_version(vs, minecraft_directory, callback=callback)  # 安装Minecraft版本
                        logger.info(f"Minecraft {vs} 安装成功")
                    
                    
                # 已安装版本显示也改为滚动条形式
                installed_versions = os.listdir(minecraft_directory + "/versions")  # 获取已安装版本
                logger.info("已安装版本获取成功")
                installed_list = [
                    v for v in installed_versions 
                    if v not in ['jre_manifest.json', 'version_manifest_v2.json']  # 排除非版本文件
                ]
                
                launchversion = show_version_list([{"id": v, "type": "已安装"} for v in installed_list])
                    
                if not launchversion:  # 未选择启动版本
                    pass
                else:        
                    launch_version = launchversion.split()[0]  # 处理带类型说明的版本号
        
                if launch_version not in ['jre_manifest.json', 'version_manifest_v2.json']:  # 检查是否为有效版本
                    if launch_version in installed_versions:  # 检查版本是否已安装
                        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(launch_version, minecraft_directory, options)  # 获取启动命令
                        logger.info("游戏命令生成成功")
                        logger.info("正在启动游戏...")
                        subprocess.run(minecraft_command)  # 启动游戏
                        logger.info("游戏进程已退出")
                os.system("cls")  # 清屏
                
                if pyautogui.confirm(text='是否退出启动器？', title='退出确认', buttons=['是', '取消']) == "是":
                    logger.info("程序退出")
                    exit(0)  # 退出程序
        except Exception as e:
            logger.error(f"发生错误：{str(e)}")  # 记录错误
            logger.error("（错误原因）程序异常退出")
            break

# 启动鼠标检测线程和主程序线程
thread3 = threading.Thread(target=detect_mouse_move)  # 鼠标检测线程
thread2 = threading.Thread(target=__main__)  # 主程序线程

thread3.start()  # 启动鼠标检测
thread2.start()  # 启动主程序
thread2.join()  # 等待主程序结束
exit()  # 退出程序