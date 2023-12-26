# 打包为exe
# pyinstaller -F --uac-admi FileToZip.py --noconsole

import sys ,os ,shutil ,json ,zipfile

class FileToZip():

    def __init__(self):

        # 在exe环境运行时，config_path设置为获取已经设置的环境变量
        self.config_path = os.environ.get('FileToZip')
        # 在py环境运行时，config_path设置为config.json文件的绝对路径，打包时注释掉
        # self.config_path = r'E:\project\Python\FileToZip\config.json'

        self.get_info()


    #  获取信息
    def get_info(self):
        if sys.argv[1] == '1':
            self.compress(sys.argv[2])
        elif sys.argv[1] == '0':
            self.decompress(sys.argv[2])


    # 压缩文件
    def compress(self ,file_path):

        # 不压缩zip文件
        if '.zip' in file_path:
            return

        with open(self.config_path, 'r' ,encoding='utf-8') as f:
            info = json.load(f)
        volume_size = info['分卷大小'] * 1024 * 1024

        zip_name = self.extractFileName(file_path)

        # 是否为文件夹
        if os.path.isdir(file_path):
            file_size = self.get_directory_size(file_path)
            if file_size <= volume_size:
                # 压缩为单个文件
                with zipfile.ZipFile(f'{zip_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                    self.zip_directory(file_path, zipf, file_path)
            else:
                # 压缩为单个文件
                with zipfile.ZipFile(f'{zip_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                    self.zip_directory(file_path, zipf, file_path)

                # 分卷压缩
                self.zip_part_compress(zip_name ,volume_size)

        else:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size <= volume_size:
                # 压缩为单个文件
                with zipfile.ZipFile(f'{zip_name}.zip', 'w') as zipf:
                    zipf.write(file_path, os.path.basename(file_path))
            else:
                # 压缩为单个文件
                with zipfile.ZipFile(f'{zip_name}.zip', 'w') as zipf:
                    zipf.write(file_path, os.path.basename(file_path))

                # 分卷压缩
                self.zip_part_compress(zip_name ,volume_size)


    # 解压文件
    def decompress(self ,zip_path):

        # 只解压ZIP文件
        if '.zip' not in zip_path:
            return

        file_list = self.is_part_zip(zip_path)
        if file_list:
            dirname = os.path.dirname(zip_path)
            temp_zip = f'{os.path.dirname(zip_path)}\\temp.zip'
            with open(temp_zip, 'ab') as output_zip:
                # 逐个打开分卷文件并写入合并文件
                for file_name in file_list:
                    with open(f'{dirname}\\{file_name}', 'rb') as part_zip:
                        shutil.copyfileobj(part_zip, output_zip)

            # 解压合并后的zip文件
            with zipfile.ZipFile(temp_zip, 'r') as full_zip:
                full_zip.extractall()

            # 删除合并的zip文件
            os.remove(temp_zip)

        else:
            # 直接解压ZIP文件
            with zipfile.ZipFile(zip_path, 'r') as full_zip:
                full_zip.extractall()


    # 分卷压缩
    def zip_part_compress(self ,zip_name ,volume_size):
        # 读取文件内容
        with open(f'{zip_name}.zip', 'rb') as f:
            data = f.read()

        # 计算分卷数量
        total_size = len(data)
        num_volumes = (total_size + volume_size - 1) // volume_size

        # 逐个写入分卷文件
        for i in range(num_volumes):
            # 计算分卷文件长度
            start = i * volume_size
            end = min(start + volume_size, total_size)

            # 写入分卷文件
            volume_data = data[start:end]
            volume_filename = f"{zip_name}_part{i+1}.zip"
            with open(volume_filename, 'wb') as vf:
                vf.write(volume_data)

        # 删除原压缩文件，只保留分卷文件
        os.remove(f'{zip_name}.zip')


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


    # 提取文件名，不要后缀名
    def extractFileName(self ,file_path):
        base_name = os.path.basename(file_path)
        file_name = os.path.splitext(base_name)[0]
        return file_name


    # 判断是否为分卷ZIP文件
    def is_part_zip(self ,zip_path):
        base_name = os.path.basename(zip_path)
        if 'part' not in base_name:
            return False

        # 同名前缀
        homonymPrefix = os.path.splitext(base_name)[0][0:-1]
        file_list = []
        # 获取文件夹名
        dir_name = os.path.dirname(zip_path)
        # 遍历文件夹，获取同名前缀分卷文件
        n = 1
        for file_name in os.listdir(dir_name):
            if homonymPrefix in file_name:
                file_list.append(f'{homonymPrefix}{n}.zip')
                n += 1
        return file_list


    # 计算指定目录中所有文件的总大小（以bytes为单位）。
    def get_directory_size(self ,path):
        total_size = 0

        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)

        return total_size


if __name__ == "__main__":
    FileToZip()


