import os
import sys
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import paramiko
import threading
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from scp import SCPClient, SCPException
import re
from mdbq.config import config
import time
import datetime
import argparse
import ast
from functools import wraps


__version__ = '1.1.2'


dir_path = os.path.expanduser("~")
content = config.read_config(file_path=os.path.join(dir_path, 'spd.txt'))

def set_log():
    level_dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    # 设置日志等级
    log_level_name = content.get('scp_log_level', 'CRITICAL').upper()
    log_level = level_dict.get(log_level_name, level_dict['CRITICAL'])

    # 日志文件路径
    log_file_name = content.get('scp_log_file', 'spd.txt')
    log_file = os.path.join(dir_path, 'logfile', log_file_name)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=3*1024*1024,
        backupCount=10,
        encoding='utf-8'  # 明确指定编码（避免Windows乱码）
    )
    stream_handler = logging.StreamHandler()  # 终端输出Handler
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    file_handler.setLevel(log_level)
    stream_handler.setLevel(log_level)

    # 获取根日志记录器并添加Handler
    logger = logging.getLogger()
    for handler in logger.handlers[:]:  # 移除根日志记录器的所有现有处理器
        logger.removeHandler(handler)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)  # 设置根日志级别

    # 屏蔽INFO级SSH日志
    ssh_logger = logging.getLogger("paramiko.transport")
    ssh_logger.setLevel(logging.WARNING)
    return logger


logger = set_log()


def time_cost(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        def format_duration(seconds):
            hours = int(seconds // 3600)
            remainder = seconds % 3600
            minutes = int(remainder // 60)
            seconds_remaining = remainder % 60
            seconds_remaining = round(seconds_remaining, 2)

            parts = []
            if hours > 0:
                parts.append(f"{hours}小时")
            if minutes > 0 or (hours > 0 and seconds_remaining > 0):
                parts.append(f"{minutes}分")
            if seconds_remaining < 10 and (hours == 0 and minutes == 0):
                parts.append(f"{seconds_remaining}秒")
            elif seconds_remaining < 10 and (hours != 0 or minutes != 0):
                parts.append(f"0{int(seconds_remaining)}秒")
            else:
                parts.append(f"{int(seconds_remaining)}秒")
            return ''.join(parts)

        before = time.time()
        result = func(*args, **kwargs)
        after = time.time()
        duration = after - before
        formatted_time = format_duration(duration)
        logger.info(f'用时：{formatted_time}')
        return result

    return wrapper


class SCPCloud:
    def __init__(self, host, port, user, password, max_workers=5, log_file='cloud.log'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.max_workers = max_workers
        self.ssh_lock = threading.Lock()
        self.pbar_lock = threading.Lock()
        self.pbars = {}
        self.skip = ['.DS_Store']
        self.next_bar_pos = 0
        self.position_map = {}
        self.download_skip = []  # 下载跳过列表
        self.path_sep = '/'  # 统一使用Linux路径分隔符

    def _normalize_path(self, path, is_remote=False):
        """统一路径格式处理"""
        # 转换路径分隔符
        path = path.replace('\\', '/') if not is_remote else path

        # 处理Windows盘符
        if re.match(r'^[A-Za-z]:', path):
            path = path.replace(':', '').replace('\\', '/')

        # 标准化路径
        path = os.path.normpath(path).replace('\\', '/') if not is_remote else path
        return path.rstrip('/')

    def _create_ssh_connection(self):
        """为每个线程创建独立的SSH连接"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            look_for_keys=False
        )
        return ssh

    def upload(self, local_path, remote_path):
        ssh = self._create_ssh_connection()
        try:
            local_path = self.check_home_path(local_path, is_remoto=False, ssh=ssh)
            remote_path = self.check_home_path(remote_path, is_remoto=True, ssh=ssh)
            if os.path.isfile(local_path):
                scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._progress_bar)
                self._upload_file(local_path=local_path, remote_path=remote_path, ssh=ssh, scp=scp)
            elif os.path.isdir(local_path):
                self._upload_folder(local_dir=local_path, remote_dir=remote_path)
            else:
                logger.info(f'不存在的本地路径: "{local_path}", 请检查路径, 建议输入完整绝对路径')
        finally:
            ssh.close()

    def _upload_folder(self, local_dir, remote_dir):
        remote_dir = remote_dir.rstrip('/') + '/'
        local_dir = local_dir.rstrip('/') + '/'

        create_dir_list = []
        upload_list = []
        for root, _, files in os.walk(local_dir):
            ls_dir = re.sub(f'^{local_dir}', '', root)
            create_dir_list.append(os.path.join(remote_dir, ls_dir))
            for file in files:
                local_file = os.path.join(root, file)
                if self._skip_file(file):
                    continue
                ls_file = re.sub(f'^{local_dir}', '', f'{local_file}')
                remote_file = os.path.join(remote_dir, ls_file)
                upload_list.append({local_file: remote_file})

        logger.info(f'预检目录(不存在将创建) {create_dir_list}')
        # 预创建远程目录
        with ThreadPoolExecutor(self.max_workers) as pool:
            pool.map(self._mkdir_remote, create_dir_list)

        # 使用独立连接上传文件
        with ThreadPoolExecutor(self.max_workers) as pool:
            pool.map(self._upload_file_thread, upload_list)

    def _upload_file_thread(self, _args):
        """上传方法"""
        for local_path, remote_path in _args.items():
            ssh = self._create_ssh_connection()
            scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._progress_bar)
            try:
                self._upload_file(local_path, remote_path, ssh, scp)
            finally:
                scp.close()
                ssh.close()

    def _upload_file(self, local_path, remote_path, ssh, scp):
        """使用传入的SSH和SCP实例上传"""
        # 标准化路径处理
        local_path = self._normalize_path(local_path)
        remote_path = self._normalize_path(remote_path, is_remote=True)

        # 自动处理目录情况
        if self._remote_is_dir(ssh, remote_path):
            remote_path = f"{remote_path}/{os.path.basename(local_path)}"

        # 确保远程路径是文件
        remote_path = remote_path.rstrip('/')

        remote_dir = os.path.dirname(remote_path)
        self._mkdir_remote(remote_dir)  # 确保目录存在

        if self._remote_is_dir(ssh, remote_path):
            remote_path = os.path.join(remote_path, os.path.basename(local_path))

        if not self._should_upload(ssh, local_path, remote_path):
            logger.info(f"文件已存在rm {remote_path}")
            return

        logger.info(f'{local_path} -> {remote_path}')
        scp.put(local_path, remote_path, preserve_times=True)
        logger.debug(f'上传完成: {local_path} -> {remote_path}')
        if not self._verify_download(ssh=ssh, local_path=local_path, remote_path=remote_path):
            logger.error(f"MD5校验失败 -> lc: {local_path} -> rm: {remote_path}")


    def _should_upload(self, ssh, local_path, remote_path):
        """使用传入的SSH连接进行检查"""
        # 确保远程路径是文件
        remote_path = self._normalize_path(remote_path, is_remote=True)

        if not self._remote_is_file(ssh, remote_path):
            return True

        if not self._remote_exists(ssh, remote_path):
            return True
        local_md5 = self._get_local_md5(local_path)
        remote_md5 = self._get_remote_md5(ssh, remote_path)
        return local_md5 != remote_md5

    def _get_local_md5(self, path):
        """计算本地MD5"""
        if not os.path.isfile(path):
            return None
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_remote_md5(self, ssh, path):
        """使用指定的SSH连接执行命令"""
        # if not self._remote_is_file(ssh, path):
        #     return None
        # stdin, stdout, stderr = ssh.exec_command(f'md5sum "{path}"')
        # output = stdout.read().decode().strip()
        # return output.split()[0] if output else None

        # 统一路径格式
        path = self._normalize_path(path, is_remote=True)
        # 使用通用命令获取MD5
        cmd = f' (test -f "{path}" && (openssl md5 -r "{path}" 2>/dev/null || md5sum "{path}")) || echo "NOT_FILE"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode().strip()

        if output == "NOT_FILE" or not output:
            return None
        return output.split()[0]

    def _remote_exists(self, ssh, path):
        stdin, stdout, stderr = ssh.exec_command(f'[ -e "{path}" ] && echo exists')
        return stdout.read().decode().strip() == 'exists'

    def _mkdir_remote(self, path):
        """线程安全的目录创建"""
        with self.ssh_lock:  # 全局锁保护
            ssh = self._create_ssh_connection()
            ssh.exec_command(f'mkdir -p "{path}"')
            ssh.close()

    def _skip_file(self, file_path):
        """ 跳过指定的文件 """
        if self.skip:
            for skip in self.skip:
                if skip in file_path:
                    return True

    def _progress_bar(self, filename, size, sent):
        """线程安全的进度条"""
        try:
            filename_str = filename.decode('utf-8', errors='replace')
        except Exception as e:
            filename_str = filename

        with self.pbar_lock:  # 获取资源锁
            if filename_str not in self.pbars:
                display_size = max(size, 1)
                new_pbar = tqdm(
                    total=display_size,
                    unit='B',
                    unit_scale=True,
                    desc=f'上传 {os.path.basename(filename_str)}',
                    position=self.next_bar_pos,  # 固定位置分配
                    leave=True,  # 完成后保留进度条显示
                    miniters=1,
                    dynamic_ncols=True,
                    lock_args=None  # 使用全局锁
                )
                self.pbars[filename_str] = new_pbar
                self.position_map[filename_str] = self.next_bar_pos
                self.next_bar_pos += 1  # 位置计数器递增
                if size == 0:  # 空文件特殊处理
                    with self.pbar_lock:  # 将回收操作纳入锁保护范围
                        new_pbar.update(1)
                        new_pbar.close()
                        del self.pbars[filename_str]
                        self.next_bar_pos -= 1  # 回收位置
                        return
            # 获取目标进度条及位置信息
            target_pbar = self.pbars.get(filename_str)
            if not target_pbar:
                return
            # target_pbar.clear()  # 先清除旧内容
            current = target_pbar.n
            safe_total = target_pbar.total
            increment = max(0, min(sent, safe_total) - current)
            if increment > 0:
                target_pbar.update(increment)
                target_pbar.refresh()  # 立即刷新显示
            if target_pbar.n >= target_pbar.total and filename_str in self.pbars:
                target_pbar.close()
                del self.pbars[filename_str]
                self.next_bar_pos -= 1  # 回收位置计数器

    def download(self, remote_path, local_path):
        """下载入口"""
        ssh = self._create_ssh_connection()
        try:
            local_path = self.check_home_path(local_path, is_remoto=False, ssh=ssh)
            remote_path = self.check_home_path(remote_path, is_remoto=True, ssh=ssh)
            if self._remote_is_dir(ssh, remote_path):
                self._download_folder(remote_dir=remote_path, local_dir=local_path, ssh=ssh)
            elif self._remote_is_file(ssh, remote_path):
                self._download_file(remote_path=remote_path, local_path=local_path, ssh=ssh)
            else:
                logger.info(f'不存在的远程路径: "{remote_path}", 请检查路径, 建议输入完整绝对路径')
        finally:
            ssh.close()

    def _remote_is_file(self, ssh, path):
        """检查远程路径是否为文件"""
        # stdin, stdout, stderr = ssh.exec_command(f'[ -f "{path}" ] && echo file')
        # return stdout.read().decode().strip() == 'file'

        path = self._normalize_path(path, is_remote=True)
        stdin, stdout, stderr = ssh.exec_command(f'[ -f "{path}" ] && echo file')
        return stdout.read().decode().strip() == 'file'

    def _remote_is_dir(self, ssh, path):
        """判断远程路径是否为目录"""
        path = path.rstrip('/')
        stdin, stdout, stderr = ssh.exec_command(f'[ -d "{path}" ] && echo directory')
        return stdout.read().decode().strip() == 'directory'

    def _download_folder(self, remote_dir, local_dir, ssh):
        """下载文件夹核心逻辑"""
        remote_dir = remote_dir.rstrip('/') + '/'
        local_dir = local_dir.rstrip('/') + '/'

        # 获取远程文件树
        file_tree = self._get_remote_tree(ssh, remote_dir)

        # 创建本地目录结构
        dirs_to_create = [os.path.join(local_dir, d.replace(remote_dir, '', 1)) for d in file_tree['dirs']]
        for d in dirs_to_create:
            os.makedirs(d, exist_ok=True)

        # 准备下载列表
        download_list = []
        for remote_file in file_tree['files']:
            local_file = os.path.join(local_dir, remote_file.replace(remote_dir, '', 1))
            # if self._should_skip_download(remote_file):
            #     continue
            if self._skip_file(remote_file):
                logger.info(f'跳过文件: {remote_file}')
                continue
            download_list.append({remote_file: local_file})

        # 多线程下载
        with ThreadPoolExecutor(self.max_workers) as pool:
            pool.map(self._download_file_thread, download_list)

    def _get_remote_tree(self, ssh, root_dir):
        """递归获取远程目录结构"""
        tree = {'dirs': [], 'files': []}
        stdin, stdout, stderr = ssh.exec_command(f'find "{root_dir}" -type d')
        for line in stdout:
            tree['dirs'].append(line.strip())

        stdin, stdout, stderr = ssh.exec_command(f'find "{root_dir}" -type f')
        for line in stdout:
            tree['files'].append(line.strip())
        return tree

    def _download_file_thread(self, _args):
        """多线程下载文件"""
        for rm_path, lc_path in _args.items():
            ssh = self._create_ssh_connection()
            scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._download_progress)
            try:
                self._download_file(rm_path, lc_path, ssh, scp)
            finally:
                scp.close()
                ssh.close()

    def _download_file(self, remote_path, local_path, ssh, scp=None):
        """下载单个文件"""
        # 标准化路径
        remote_path = self._normalize_path(remote_path, is_remote=True)
        local_path = self._normalize_path(local_path)

        # 自动处理本地目录情况
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))

        if scp is None:
            scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._download_progress)

        if not self._should_download(ssh, remote_path, local_path):
            logger.info(f"文件已存在lc {local_path}")
            return

        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))

        try:
            logger.info(f'{remote_path} -> {local_path}')
            scp.get(remote_path, local_path=local_path, preserve_times=True)
            logger.debug(f'下载完成: {remote_path} -> {local_path}')
        except Exception as e:
            logger.error(f"Error details: {e.__class__.__name__}, {e.args}")

        if not self._verify_download(ssh=ssh, remote_path=remote_path, local_path=local_path):
            logger.error(f"MD5校验失败 -> rm: {remote_path} -> lc: {local_path}")

    def _should_download(self, ssh, remote_path, local_path):
        """判断是否需要下载"""
        if not os.path.exists(local_path):
            return True
        remote_md5 = self._get_remote_md5(ssh, remote_path)
        local_md5 = self._get_local_md5(local_path)
        return remote_md5 != local_md5

    def _verify_download(self, ssh, remote_path, local_path):
        """验证下载文件完整性"""
        return self._get_remote_md5(ssh, remote_path) == self._get_local_md5(local_path)

    def _should_skip_download(self, remote_path):
        """跳过指定文件"""
        filename = os.path.basename(remote_path)
        return any(skip in filename for skip in self.download_skip)

    def _download_progress(self, filename, size, sent):
        """下载进度回调"""
        try:
            filename_str = filename.decode('utf-8', errors='replace')
        except Exception as e:
            filename_str = filename
        with self.pbar_lock:
            if filename_str not in self.pbars:
                new_pbar = tqdm(
                    total=size,
                    unit='B',
                    unit_scale=True,
                    desc=f'下载 {os.path.basename(filename_str)}',
                    position=self.next_bar_pos,
                    leave=True,
                    dynamic_ncols=True
                )
                self.pbars[filename_str] = new_pbar
                self.position_map[filename_str] = self.next_bar_pos
                self.next_bar_pos += 1

            target_pbar = self.pbars.get(filename_str)
            if not target_pbar:
                return

            current = target_pbar.n
            increment = max(0, min(sent, size) - current)
            if increment > 0:
                target_pbar.update(increment)

            if target_pbar.n >= target_pbar.total and filename_str in self.pbars:
                target_pbar.close()
                del self.pbars[filename_str]
                self.next_bar_pos -= 1

    def check_home_path(self, path, is_remoto=False, ssh=None):
        """将路径中的~解析为home目录"""
        if not path:
            return
        # 路径标准化处理
        path = self._normalize_path(path, is_remote=is_remoto)
        if str(path).startswith('~'):
            if is_remoto:
                if not ssh:
                    logger.info(f'ssh 不能为 none')
                    return
                stdin, stdout, stderr = ssh.exec_command("echo $HOME")
                home_path = stdout.read().decode().strip()
            else:
                home_path = os.path.expanduser("~")
            # return str(path).strip().replace('~', home_path)
            return self._normalize_path(path, is_remote=is_remoto)
        else:
            return path



@time_cost
def main(debug=False):
    """
    通过命令行运行, debug=False
    """
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description='上传下载')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='')
    parser.add_argument('-u', '--upload', nargs=2, help='')
    parser.add_argument('-d', '--download', nargs=2, help='')
    args = parser.parse_args()

    cloud = SCPCloud(
        host=content['scp_host'],
        port=int(content['scp_port']),
        user=content['scp_user'],
        password=content['scp_password'],
        max_workers=int(content['scp_max_workers']),
        log_file=content['scp_log_file']
    )
    cloud.skip = ast.literal_eval(content['scp_skip'])

    if debug:
        args.download = ['logfile', '~/downloads/']

    if args.upload:
        local_path, remoto_path = args.upload[0], args.upload[1]
        cloud.upload(local_path=local_path, remote_path=remoto_path)
    elif args.download:
        remoto_path, local_path = args.download[0], args.download[1]
        cloud.download(remote_path=remoto_path, local_path=local_path)


if __name__ == "__main__":
    main(debug=False)
