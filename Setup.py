# 打包为exe
# pyinstaller -F --uac-admi Setup.py --noconsole

import os ,json ,winreg

class Setup():
    def __init__(self):
        # 构造config.json文件的绝对路径
        config_path = os.getcwd() + '\\config.json'
        # 将config.json文件路径写入环境变量
        self.set_system_env_var('FileToZip', config_path)

        # 获取当前环境
        with open(config_path, 'r' ,encoding='utf-8') as f:
            info = json.load(f)
        if info['当前环境'] == 'py':
            self.run_bat_path = f"{os.path.abspath(os.getcwd())}\\run_py.bat"
        elif info['当前环境'] == 'exe':
            self.run_bat_path = f"{os.path.abspath(os.getcwd())}\\run_exe.bat"

        self.addFileMenu()
        self.addFolderMenu()


    # 添加环境变量
    def set_system_env_var(self ,var_name, var_value):
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
            winreg.SetValueEx(key, var_name, 0, winreg.REG_EXPAND_SZ, var_value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


    # 添加文件菜单
    def addFileMenu(self):
        # 打开 "文件" 类型的注册表键
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "*", 0, winreg.KEY_ALL_ACCESS) as key:
            try:

                # 创建一个新的子键
                with winreg.CreateKey(key, "shell\\compress") as subkey:
                    # 设置默认字符串值
                    winreg.SetValue(subkey, None, winreg.REG_SZ, "压缩文件")

                    # 设置命令值
                    command_key = winreg.CreateKey(subkey, "command")
                    # 运行脚本，参数1为自定义参数，参数2为文件路径
                    winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, f"\"{self.run_bat_path}\" \"1\" \"%V\"")

                # 创建一个新的子键
                with winreg.CreateKey(key, "shell\\decompress") as subkey:
                    # 设置默认字符串值
                    winreg.SetValue(subkey, None, winreg.REG_SZ, "解压文件")

                    # 设置命令值
                    command_key = winreg.CreateKey(subkey, "command")
                    # 运行脚本，参数1为自定义参数，参数2为文件路径
                    winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, f"\"{self.run_bat_path}\" \"0\" \"%V\"")

            except Exception as e:
                print(f"Error: {e}")


    # 添加文件夹菜单
    def addFolderMenu(self):
        # 打开 "文件夹" 类型的注册表键
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Directory", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                # 创建一个新的子键
                with winreg.CreateKey(key, "shell\\compress") as subkey:
                    # 设置默认字符串值
                    winreg.SetValue(subkey, None, winreg.REG_SZ, "压缩文件")

                    # 设置命令值
                    command_key = winreg.CreateKey(subkey, "command")
                    # 运行脚本，参数1为自定义参数，参数2为文件路径
                    winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, f"\"{self.run_bat_path}\" \"1\" \"%V\"")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    Setup()


