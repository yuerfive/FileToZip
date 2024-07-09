# 打包为exe
# pyinstaller -F --uac-admi FileToZip.py --noconsole

import sys ,os ,re ,shutil ,json ,zipfile ,rarfile, tempfile
from multiprocessing import Pool, Manager, Process

import Constant


class FileToZip():

    def __init__(self):

        # 运行环境
        if Constant.ENVIRONMENT == 'py':
            rarfile.UNRAR_TOOL = r'E:\project\Python\FileToZip\UnRAR.exe'
            self.config_path = r'E:\project\Python\FileToZip\config.json'
        elif Constant.ENVIRONMENT == 'exe':
            rarfile.UNRAR_TOOL = os.environ.get('UnRAR')
            self.config_path = os.environ.get('FileToZip')

        # print(f'以下为调试输出：\n选中的文件路径：{sys.argv[2]}\n状态标志：{sys.argv[1]}')

        with open(self.config_path, 'r' ,encoding='utf-8') as f:
            info = json.load(f)
        self.volume_size = info['分卷大小'] * 1024 * 1024
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

        # 获取文件名，或文件夹名
        zip_name = self.get_file_name(file_path)

        with Manager() as manager:
            file_queue = manager.Queue()
            merge_queue = manager.Queue()
            chunk_queue = manager.Queue()
            pool = Pool()

            # 压缩为单个zip文件
            if os.path.isdir(file_path):
                # 如果是目录，将目录及其内容压缩到 zip 文件中
                with zipfile.ZipFile(f'{zip_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                    self.zip_directory(file_path, zipf, file_queue, file_path)
            else:
                # 如果是文件，直接将文件添加到 zip 文件中
                with zipfile.ZipFile(f'{zip_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(file_path, os.path.basename(file_path))

            # 文件压缩合并进程
            merger = Process(target=self.directory_merge_worker, args=(merge_queue, f'{zip_name}.zip'))
            merger.start()

            # 文件夹压缩多进程分块
            for _ in range(pool._processes):
                pool.apply_async(self.directory_worker, (file_queue, merge_queue))

            file_queue.put(None)  # 结束信号放多次，因为每个进程都要接收
            for _ in range(pool._processes):
                file_queue.put(None)

            pool.close()
            pool.join()

            merge_queue.put(None)  # 结束信号给合并进程
            merger.join()

            # 分卷压缩
            file_size = os.path.getsize(f'{zip_name}.zip')
            if file_size > self.volume_size and self.volume_size != 0:
                self.zip_part_compress(zip_name)


    # 文件夹压缩
    def zip_directory(self, file_path, zipf, file_queue, base_path=""):
        for root, dirs, files in os.walk(file_path):
            # 计算当前文件夹在 ZIP 中的相对路径
            relative_path = os.path.relpath(root, base_path)
            # 忽略根目录
            if relative_path!= ".":
                # 添加当前文件夹到 ZIP 文件中
                zipf.write(root, arcname=relative_path)

            for file in files:
                file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(file_path, base_path)
                file_queue.put((file_path, relative_file_path))

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

    # 文件夹压缩多进程分块
    def directory_worker(self, file_queue, merge_queue):
        while True:
            task = file_queue.get()
            if task is None:
                break
            file_path, arcname = task
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_name = temp_file.name
            with zipfile.ZipFile(temp_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, arcname=arcname)
            merge_queue.put(temp_file_name)

    # 文件夹压缩合并进程
    def directory_merge_worker(self, merge_queue, final_zip_file):
        with zipfile.ZipFile(final_zip_file, 'a', zipfile.ZIP_DEFLATED) as zipf:
            while True:
                temp_zip_file = merge_queue.get()
                if temp_zip_file is None:
                    break
                with zipfile.ZipFile(temp_zip_file, 'r') as temp_zip:
                    for file_info in temp_zip.infolist():
                        with temp_zip.open(file_info) as file:
                            zipf.writestr(file_info, file.read())
                os.remove(temp_zip_file)  # 删除临时文件

    # 提取文件名，如果是文件夹，则返回文件夹名
    def get_file_name(self ,path):
        # 是否是文件夹
        if os.path.isdir(path):
            return os.path.basename(path)
        base_name = os.path.basename(path)
        return os.path.splitext(base_name)[0]


#   --------------------------------------------------解压文件-------------------------------------------------

    # 解压文件
    def decompress(self ,path):

        # 只解压ZIP文件
        if '.zip' in path:
            self.decompress_zip(path)
        elif '.rar' in path:
            self.decompress_rar(path)

    # 解压zip文件
    def decompress_zip(self ,zip_path):

        # 根据压缩文件名和路径，创建文件夹
        folder_path = self.createFolders(zip_path)
        # 判断是否为分卷压缩，返回分卷文件路径列表
        file_list = self.is_part_file(zip_path)
        if file_list:
            # 构建临时zip文件路径
            temp_zip = f'{os.path.dirname(zip_path)}\\temp.zip'
            with open(temp_zip, 'ab') as output_zip:
                # 逐个打开分卷文件并写入临时zip文件
                for file_path in file_list:
                    with open(file_path, 'rb') as part_zip:
                        shutil.copyfileobj(part_zip, output_zip)

            # 解压合并后的zip文件到folder_path
            # 解码器优先级 判断是否为[utf-8] 否则使用[metadata_encoding] 未配置则使用[None = cp437]
            with zipfile.ZipFile(temp_zip ,'r' ,metadata_encoding="gbk") as full_zip:
                full_zip.extractall(folder_path)

            # 删除合并的zip文件
            os.remove(temp_zip)

        else:
            # 直接解压ZIP文件到folder_path
            # 解码器优先级 判断是否为[utf-8] 否则使用[metadata_encoding] 未配置则使用[None = cp437]
            with zipfile.ZipFile(zip_path ,'r' ,metadata_encoding="gbk") as full_zip:
                full_zip.extractall(folder_path)


    # 解压rar文件
    def decompress_rar(self ,rar_path):
        # 根据压缩文件名和路径，创建文件夹
        folder_path = self.createFolders(rar_path)
        # 判断是否为分卷压缩，返回分卷文件路径列表
        file_list = self.is_part_file(rar_path)

        if file_list:
            with rarfile.RarFile(file_list[0] ,'r') as full_rar:
                full_rar.extractall(folder_path)
        else:
            with rarfile.RarFile(rar_path ,'r') as full_rar:
                full_rar.extractall(folder_path)



    # 判断是否为分卷文件
    def is_part_file(self ,path):
        # 获取路径中的文件名部分
        base_name = os.path.basename(path)
        if 'part' not in base_name:
            return False

        # 获取后缀名
        if '.zip' in base_name:
            suffix = '.zip'
        elif '.rar' in base_name:
            suffix = '.rar'
        else:
            return False

        # 去除末尾编号，获取同名前缀，[test_part1.zip]，前缀为[test_part]
        prefix = os.path.splitext(base_name)[0].rstrip('0123456789')
        # 获取路径中的目录
        dir_name = os.path.dirname(path)

        # 文件数量
        file_count = 0
        # 最小编号长度
        min_number_length = 10

        # 获取同名前缀文件数量，及最小编号长度
        for file_name in os.listdir(dir_name):
            if prefix in file_name:
                min_number_length = min(len(re.search(r'\d+$', os.path.splitext(base_name)[0]).group()) ,min_number_length)
                file_count += 1

        # 创建分卷文件完整路径列表
        file_list = []
        for i in range(file_count):
            fill = '0' * (min_number_length - len(str(i+1)))
            file_list.append(f'{dir_name}\\{prefix}{fill}{i+1}{suffix}')

        return file_list

    # 根据压缩文件名和路径，创建文件夹
    def createFolders(self ,path):
        # 获取路径中的路径部分
        dirname = os.path.dirname(path)

        suffixes = ['_part', '.part', '.zip', '.rar']
        for suffix in suffixes:
            if suffix in path:
                folder_name = os.path.basename(path).split(suffix)[0]
                break

        # 如果文件夹已经存在，删除该文件夹
        if os.path.exists(dirname + '\\' + folder_name):
            shutil.rmtree(dirname + '\\' + folder_name)

        # 创建文件夹
        os.mkdir(dirname + '\\' + folder_name)
        return dirname + '\\' + folder_name


if __name__ == "__main__":
    FileToZip()


