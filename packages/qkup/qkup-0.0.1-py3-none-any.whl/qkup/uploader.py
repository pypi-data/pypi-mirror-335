import ftplib
import os
import argparse
import configparser
from pathlib import Path

def upload_to_ftp(file_path, host=None, user=None, password=None, port=None, remote_dir=None):
    """将文件上传到指定的 FTP 服务器，支持自定义端口"""
    # 默认配置文件路径
    config_file = Path.home() / '.qkuprc'
    
    # 如果未提供参数，尝试从配置文件读取
    if not all([host, user, password, port, remote_dir]):
        config = configparser.ConfigParser()
        if config_file.exists():
            config.read(config_file)
            if 'FTP' in config:
                host = host or config['FTP'].get('host')
                user = user or config['FTP'].get('user')
                password = password or config['FTP'].get('password')
                port = port or config['FTP'].getint('port', 21)  # 默认端口 21
                remote_dir = remote_dir or config['FTP'].get('remote_dir')
    
    # 检查必要参数
    if not host:
        raise ValueError("必须提供 FTP 服务器地址（host）")
    
    # 检查用户和密码的逻辑
    if (user or password) and not (user and password):
        raise ValueError("必须同时提供 user 和 password，或都不提供以使用匿名登录")
    
    port = port or 21  # 默认端口 21
    
    # 检查文件是否存在
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")

    # 打印调试信息
    print(f"尝试连接: host={host}, port={port}, user={user or 'anonymous'}, remote_dir={remote_dir}")

    # 连接 FTP 服务器
    try:
        with ftplib.FTP() as ftp:
            ftp.connect(host=host, port=port)
            # 处理登录
            if user and password:
                ftp.login(user=user, passwd=password)
                print(f"成功登录: {user}")
            else:
                ftp.login()  # 匿名登录
                print("成功匿名登录")
            
            if remote_dir:
                try:
                    ftp.cwd(remote_dir)
                    print(f"切换到目录: {remote_dir}")
                except ftplib.error_perm as e:
                    print(f"警告: 无法访问目录 {remote_dir}，将上传到当前目录: {e}")
            
            # 上传文件
            with open(file_path, 'rb') as file:
                ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
            print(f"文件 {file_path} 已上传到 {host}:{port}/{remote_dir or ''}")
    
    except ftplib.all_errors as e:
        print(f"FTP 错误: {e}")
    except Exception as e:
        print(f"上传失败: {e}")

def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description="将文件上传到自定义 FTP 服务器")
    parser.add_argument("file", help="要上传的文件路径")
    parser.add_argument("--host", help="FTP 服务器地址（必填）")
    parser.add_argument("--user", help="FTP 用户名")
    parser.add_argument("--password", help="FTP 密码")
    parser.add_argument("--port", type=int, help="FTP 服务器端口（默认 21）")
    parser.add_argument("--dir", help="FTP 远程目录")
    
    args = parser.parse_args()
    
    # 调用上传函数
    upload_to_ftp(
        args.file,
        host=args.host,
        user=args.user,
        password=args.password,
        port=args.port,
        remote_dir=args.dir
    )

if __name__ == "__main__":
    main()