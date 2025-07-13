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
import minecraft_launcher_lib
import subprocess
import tkinter as tk
import forgepy
import os
import sys
import requests
import threading
import time
import logzero
import pyautogui
import threading
from tqdm import tqdm
from logzero import logger

# 配置日志系统
logzero.logfile("./latest.log")
logzero.loglevel(logzero.INFO)

# 全局变量用于跟踪下载进度
downloaded_bytes = 0
total_size = 0
start_time = time.time()
lock = threading.Lock()

def download_file_part(url, start_byte, end_byte, part_number, filename, progress_bar):
    global downloaded_bytes
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)
    
    part_filename = f"{filename}.part{part_number}"
    with open(part_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                with lock:
                    downloaded_bytes += len(chunk)
                    progress_bar.update(len(chunk))

def merge_files(filename, num_parts):
    with open(filename, 'wb') as outfile:
        for i in range(num_parts):
            part_filename = f"{filename}.part{i}"
            with open(part_filename, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(part_filename)

def main(url, num_threads=4):
    global total_size, downloaded_bytes
    response = requests.head(url)
    total_size = int(response.headers['Content-Length'])
    
    part_size = total_size // num_threads
    threads = []
    filename = url.split('/')[-1]
    
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename)
    
    for i in range(num_threads):
        start_byte = i * part_size
        end_byte = start_byte + part_size - 1 if i < num_threads - 1 else total_size - 1
        thread = threading.Thread(target=download_file_part, args=(url, start_byte, end_byte, i, filename, progress_bar))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    progress_bar.close()
    
    merge_files(filename, num_threads)
    logger.info(f"文件下载成功: {filename}")
    print(f"文件下载成功: {filename}")
    return filename

def forge_down(version):
    latest = forgepy.GetLatestURL(version)
    file_url = latest
    fn = main(file_url, num_threads=4)
    return fn

minecraft_directory = os.getcwd()+"/.minecraft"
options = minecraft_launcher_lib.utils.generate_test_options()
current_max = 0

def set_status(status: str):
    print(status)

def set_progress(progress: int):
    if current_max != 0:
        print(f"{progress}/{current_max}")

def set_max(new_max: int):
    global current_max
    current_max = new_max

callback = {
    "setStatus": set_status,
    "setProgress": set_progress,
    "setMax": set_max
}

def detect_mouse_move():
    with open("pos.txt","w+") as f:
        try:
            while True:
                x, y = pyautogui.position()
                positionStr = str(x).rjust(5) + ' , ' + str(y).rjust(5)
                f.write(positionStr+"\n")
                print(positionStr, end='')
                print('\b' * len(positionStr), end='', flush=True)
                time.sleep(0.2)
        except KeyboardInterrupt:
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
        try:
            selection = listbox.curselection()
            if selection:
                selected_version[0] = versions[selection[0]]["id"]
            root.destroy()
        except Exception as e:
            logger.error(f"选择版本时出错: {str(e)}")

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

    root.mainloop()
    return selected_version[0]

def __main__():
    while True:
        try:
            logger.info("_________________________________新建实例_________________________________")
            print("正在检查文件夹...")
            if os.path.exists(minecraft_directory):
                pass
            else:
                logger.warning("目录不存在")
                logger.info("首次使用")
                os.mkdir(minecraft_directory)
                logger.info("目录创建成功")
                print("首次使用，正在下载正式版...")
                logger.info("正在下载正式版")
                minecraft_launcher_lib.install.install_minecraft_version(
                    minecraft_launcher_lib.utils.get_latest_version()["release"],
                    minecraft_directory,
                    callback=callback
                )
                logger.info("正式版下载成功")
            logger.info("文件夹检查完成")

            time.sleep(0.2)

            while True:
                ins = pyautogui.confirm(text='是否安装新版本？', title='MCL启动器', buttons=['是', '取消'])
                if ins == "是":
                    logger.info("正在获取版本列表")
                    versions = minecraft_launcher_lib.utils.get_available_versions(minecraft_directory)
                    print("版本列表获取成功")
                    logger.info("版本列表获取成功")
                    
                    # 使用新版带滚动条的版本选择窗口
                    selected_version = show_version_list(versions)
                    
                    if not selected_version:
                        continue
                        
                    vs = selected_version.split()[0]  # 处理带类型说明的版本号
                    
                    avl = False
                    for v in versions:
                        if v["id"] == vs:
                            avl = True

                    an = pyautogui.confirm(text='是否安装Forge？', title='Forge安装', buttons=['是', '取消'])
                    
                    if pyautogui.confirm(text='确认安装？', title='确认安装', buttons=['是', '取消']) == "是":
                        logger.info(f"正在安装Minecraft {vs}")
                        if an == "是":
                            logger.info(f"正在安装Forge {vs}")
                            filen = forge_down(vs)
                            logger.info(f"Forge {vs} 安装成功")
                            pyautogui.alert(text=f"安装程序下载成功，请运行 {filen} 完成Forge安装", title='Forge安装', button='确定')
                        minecraft_launcher_lib.install.install_minecraft_version(vs, minecraft_directory, callback=callback)
                        logger.info(f"Minecraft {vs} 安装成功")
                    
                    
                # 已安装版本显示也改为滚动条形式
                installed_versions = os.listdir(minecraft_directory + "/versions")
                logger.info("已安装版本获取成功")
                installed_list = [
                    v for v in installed_versions 
                    if v not in ['jre_manifest.json', 'version_manifest_v2.json']
                ]
                
                launchversion = show_version_list([{"id": v, "type": "已安装"} for v in installed_list])
                    
                if not launchversion:
                    pass
                else:        
                    launch_version = launchversion.split()[0]  # 处理带类型说明的版本号
        
                if launch_version not in ['jre_manifest.json', 'version_manifest_v2.json']:
                    if launch_version in installed_versions:
                        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(launch_version, minecraft_directory, options)
                        logger.info("游戏命令生成成功")
                        logger.info("正在启动游戏...")
                        subprocess.run(minecraft_command)
                        logger.info("游戏进程已退出")
                os.system("cls")
                
                if pyautogui.confirm(text='是否退出启动器？', title='退出确认', buttons=['是', '取消']) == "是":
                    logger.info("程序退出")
                    exit(0)
        except Exception as e:
            logger.error(f"发生错误：{str(e)}")
            logger.error("（错误原因）程序异常退出")
            break

# 启动鼠标检测线程和主程序线程
thread3 = threading.Thread(target=detect_mouse_move)
thread2 = threading.Thread(target=__main__)

thread3.start()
thread2.start()
thread2.join()
exit()