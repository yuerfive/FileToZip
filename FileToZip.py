# 打包为exe
# pyinstaller -F --uac-admi FileToZip.py --noconsole

import sys ,os ,shutil ,json ,zipfile

class FileToZip():

    def __init__(self):

        # 在exe环境运行时，config_path设置为获取已经设置的环境变量
        # self.config_path = os.environ.get('FileToZip')

        # 在py环境运行时，config_path设置为config.json文件的绝对路径，打包时注释掉
        self.config_path = r'E:\project\Python\FileToZip\config.json'

        with open(self.config_path, 'r' ,encoding='utf-8') as f:
            info = json.load(f)
        self.volume_size = info['分卷大小'] * 1024 * 1024


        # print(f'以下为调试输出：\n选中的文件路径：{sys.argv[2]}\n状态标志：{sys.argv[1]}')

        # 执行功能判断
        self.executiveFunctionJudgment()


    #  执行功能判断
    def executiveFunctionJudgment(self):
        # 以接收的参数的值来判断执行的功能是压缩还是解压
        if sys.argv[1] == '1':
            self.compress(sys.argv[2])
        elif sys.argv[1] == '0':
            self.decompress(sys.argv[2])


#   --------------------------------------------------压缩文件-------------------------------------------------

    # 压缩文件
    def compress(self ,file_path):

        # 不压缩zip文件
        if '.zip' in file_path:
            return

        # 获取文件名
        zip_name = self.get_file_name(file_path)

        # 获取文件或目录的大小
        if os.path.isdir(file_path):
            file_size = self.get_directory_size(file_path)  # 获取目录大小
        else:
            file_size = os.path.getsize(file_path)  # 获取文件大小

        # 压缩为单个zip文件
        if file_size <= self.volume_size or self.volume_size == 0:
            # 如果文件或目录大小不超过指定的卷大小，直接压缩为一个文件
            with zipfile.ZipFile(f'{zip_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(file_path):
                    # 如果是目录，将目录及其内容压缩到 zip 文件中
                    self.zip_directory(file_path, zipf, file_path)
                else:
                    # 如果是文件，直接将文件添加到 zip 文件中
                    zipf.write(file_path, os.path.basename(file_path))

        # 分卷压缩
        else:
            # 如果文件或目录大小超过指定的卷大小，先压缩为一个文件，然后进行分卷压缩
            with zipfile.ZipFile(f'{zip_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(file_path):
                    self.zip_directory(file_path, zipf, file_path)
                else:
                    zipf.write(file_path, os.path.basename(file_path))

            # 分卷压缩逻辑
            self.zip_part_compress(zip_name, self.volume_size)



    # 文件夹压缩
    def zip_directory(self ,file_path ,zipf ,base_path=""):
        for root, dirs, files in os.walk(file_path):
            # 计算当前文件夹在 ZIP 中的相对路径
            relative_path = os.path.relpath(root, base_path)

            # 忽略根目录
            if relative_path!= ".":
                # 添加当前文件夹到 ZIP 文件中
                zipf.write(root, arcname=relative_path)

            # 添加当前文件夹中的所有文件到 ZIP 文件中
            for file in files:
                file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(file_path, base_path)
                zipf.write(file_path, arcname=relative_file_path)


    # 分卷压缩
    def zip_part_compress(self ,zip_name):
        # 读取文件内容
        with open(f'{zip_name}.zip', 'rb') as f:
            data = f.read()

        # 计算分卷数量
        total_size = len(data)
        num_volumes = (total_size + self.volume_size - 1) // self.volume_size

        # 逐个写入分卷文件
        for i in range(num_volumes):
            # 计算分卷文件长度
            start = i * self.volume_size
            end = min(start + self.volume_size, total_size)

            # 写入分卷文件
            volume_data = data[start:end]
            volume_filename = f"{zip_name}_part{i+1}.zip"
            with open(volume_filename, 'wb') as vf:
                vf.write(volume_data)

        # 删除原压缩文件，只保留分卷文件
        os.remove(f'{zip_name}.zip')


    # 提取文件名，如果是文件夹，则返回文件夹名
    def get_file_name(self ,path):
        # 是否是文件夹
        if os.path.isdir(path):
            return os.path.basename(path)
        base_name = os.path.basename(path)
        return os.path.splitext(base_name)[0]


    # 计算指定目录中所有文件的总大小（以bytes为单位）。
    def get_directory_size(self ,path):
        total_size = 0

        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)

        return total_size



#   --------------------------------------------------解压文件-------------------------------------------------

    # 解压文件
    def decompress(self ,zip_path):

        # 只解压ZIP文件
        if '.zip' not in zip_path:
            return

        # 根据压缩文件名和路径，创建文件夹
        folder_path = self.createFolders(zip_path)
        # 判断是否为分卷压缩，返回分卷文件路径列表
        file_list = self.is_part_zip(zip_path)
        if file_list:
            # 构建临时zip文件路径
            temp_zip = f'{os.path.dirname(zip_path)}\\temp.zip'
            with open(temp_zip, 'ab') as output_zip:
                # 逐个打开分卷文件并写入临时zip文件
                for file_path in file_list:
                    with open(file_path, 'rb') as part_zip:
                        shutil.copyfileobj(part_zip, output_zip)

            # 解压合并后的zip文件到folder_path
            with zipfile.ZipFile(temp_zip, 'r') as full_zip:
                full_zip.extractall(folder_path)

            # 删除合并的zip文件
            os.remove(temp_zip)

        else:
            # 直接解压ZIP文件到folder_path
            with zipfile.ZipFile(zip_path, 'r') as full_zip:
                full_zip.extractall(folder_path)


    # 判断是否为分卷ZIP文件
    def is_part_zip(self ,zip_path):
        base_name = os.path.basename(zip_path)
        if 'part' not in base_name:
            return False

        # 同名前缀，[test_part1.zip]，前缀为[test_part]
        homonymPrefix = os.path.splitext(base_name)[0][0:-1]
        file_list = []
        # 获取路径中的目录
        dir_name = os.path.dirname(zip_path)
        # 遍历文件夹，获取同名前缀分卷文件
        n = 1
        for file_name in os.listdir(dir_name):
            if homonymPrefix in file_name:
                file_list.append(f'{dir_name}\\{homonymPrefix}{n}.zip')
                n += 1
        return file_list


    # 根据压缩文件名和路径，创建文件夹
    def createFolders(self ,zip_path):
        path = os.path.dirname(zip_path)
        if '_part' in zip_path:
            folder_name = os.path.basename(zip_path).split('_part')[0]
        else:
            folder_name = os.path.basename(zip_path).split('.zip')[0]

        os.mkdir(path + '\\' + folder_name)
        return path + '\\' + folder_name


if __name__ == "__main__":
    FileToZip()


