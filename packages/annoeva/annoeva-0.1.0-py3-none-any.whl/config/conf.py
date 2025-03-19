import socket
from dataclasses import dataclass
from annoeva._utils import _get_yaml_data
import subprocess
import importlib.resources
from pathlib import Path
import os
from typing import Optional

def personal_config():
    """Initialize personal configuration for annoeva.
    
    Creates the ~/.annoeva directory and initializes the projects database
    if they don't already exist.
    """
    dbpath = os.path.expanduser('~/.annoeva/projects.db')
    if not os.path.isfile(dbpath):
        os.makedirs(os.path.expanduser('~/.annoeva'), exist_ok=True)
        tbj = SQLiteDB(dbpath=dbpath)
        tbj.crt_tb_sql()
    
@dataclass
class cronlist(object):
    """Manage cron jobs for annoeva.
    
    Attributes:
        confpath (str): Path to configuration file
        confdir (str): Directory containing configuration file
        commanderpath (str): Path to annoeva executable
    
    Methods:
        add_cron(): Add cron jobs for periodic project monitoring and cleanup
    """
    confpath: str
    confdir: str = None
    commanderpath: str = None
    def __post_init__(self):
        self.confdir = os.path.dirname(self.confpath)
        if not os.path.exists(self.confdir):
            os.makedirs(self.confdir, exist_ok=True)
        if not os.path.exists(self.confpath):
            with open(self.confpath, 'w') as f:
                f.write(f'cronnode: {socket.gethostname()}\nwebhook:\n  url:\nautoconf:\n  product_type: ')
        else:
            conf = _get_yaml_data(self.confpath)
            if 'cronnode' not in conf:
                with open(self.confpath, 'a') as f:
                    f.write(f'cronnode: {socket.gethostname()}\nwebhook:\n  url:\nautoconf:\n  product_type: ')
            else:
                cronnode = conf["cronnode"]
                if cronnode != socket.gethostname():
                    sys.stderr.write(f"Please run annoeva on {cronnode}\nYou can change the default node by modified {self.confpath}\n")
                    sys.exit(1)

    def add_cron(self):
        p = subprocess.Popen('crontab -l', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutput,erroutput = p.communicate()
        crontable = str(stdoutput,'utf-8').split('\n')
        need_addcron = 1
        for line in crontable:
            if line.find(f'{os.path.basename(self.program)} cron'.format()) > 0:
                needcron=0
        if need_addcron == 1:
            #run cron project per 2 hours
            line = f'*/18 * * * * {self.commanderpath} cron -m 1'
            crontable.append(line)
            #run rm finished projects in per 1 months
            line = f'0 0 1 * * {self.commanderpath} cron -m 2'
            crontable.append(line)

            pipe = os.popen('crontab', 'w')
            for line in crontable:
                if line == '':
                    continue
                pipe.write(line+'\n')
            pipe.flush()
            pipe.close()

def get_config_autoconf(ptype: str = '10XGenomics') -> Path:
    """Get autoconfiguration path for specified product type.
    
    Args:
        ptype (str): Product type identifier (default: '10XGenomics')
    
    Returns:
        Path: Path to autoconfiguration file
    
    The function checks for configuration in this order:
    1. User custom configuration (~/.annoeva/conf.yaml)
    2. Default package configuration (cmd.yaml)
    """
    # 优先级1：用户自定义配置文件（如 ~/.annoeva/conf.yaml）
    user_config = os.path.expanduser('~/.annoeva/conf.yaml')
    if os.path.isfile(user_config):
        conf = _get_yaml_data(user_config)
        if 'autoconf' in conf:
            if ptype in conf['autoconf']:
                return conf['autoconf'][ptype]
    
    # 优先级2：包内默认配置文件
    try:
        with importlib.resources.path("annoeva.config", "cmd.yaml") as default_config:=
            conf = _get_yaml_data(user_config)
            if 'autoconf' in conf:
                if ptype in conf['autoconf']:
                    return conf['autoconf'][ptype]
    except FileNotFoundError:
        print("Default cmd.yaml not found in package!")
