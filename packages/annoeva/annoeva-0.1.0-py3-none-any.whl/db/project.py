from dataclasses import dataclass
from pandas import Series
import os
import subprocess
from annoeva._utils import _get_yaml_data, generate_shell, decorate_shell
from annoeva.db import SQLiteDB
import datetime
import psutil

@dataclass
class project:
    """
    A class representing a project and its status in the system.
    
    Attributes:
        user (str): The user who owns the project
        proid (str): Unique project identifier
        ptype (str): Project type
        workdir (str): Working directory path
        dirstat (str): Directory status [Y|N]
        info (str): Info file status [Y|N]
        data (str): Data status [Y|N|err]
        autoconf (str): Auto-config status [Y|N|err]
        worksh (str): Work shell script path
        pid (str): Process ID of running job
        p_args (str): Process arguments
        stime (str): Start time of process
        etime (str): End time of process
        pstat (str): Process status [run|done|err|-]
        run_num (str): Number of times the project has been run
    """
    user: str
    proid: str
    ptype: str
    workdir: str
    dirstat: str
    info: str
    data: str
    autoconf: str
    worksh: str
    pid: str
    p_args: str
    stime: str
    etime: str
    pstat: str
    run_num: str

    @classmethod
    def from_series(cls, series: Series) -> 'project':
        """Create a project instance from a pandas Series.
        
        Args:
            series (Series): Pandas Series containing project data
            
        Returns:
            project: A new project instance
        """
        return cls(
            user=series['user'],
            proid=series['proid'],
            ptype=series['ptype'],
            workdir=series['workdir'],
            dirstat=series['dirstat'],
            info=series['info'],
            data=series['data'],
            autoconf=series['autoconf'],
            work_sh=series['work_sh'],
            pid=series['pid'],
            p_args=series['p_args'],
            stime=series['stime'],
            etime=series['etime'],
            pstat=series['pstat'],
            run_num=series['run_num'],
        )

    def check_dirstat(self, sqldb: SQLiteDB) -> None:
        """Check and update directory status.
        
        Args:
            sqldb (SQLiteDB): Database connection object
        """
        if self.dirstat == 'Y':
            return
        if os.path.isdir(f'{self.workdir}/info') and os.path.isdir(f'{self.workdir}/Filter') and os.path.isdir(f'{self.workdir}/Analysis'):
            self.dirstat = 'Y'
            sqldb.update_tb_value_sql(self.proid, 'dirstat', 'Y')
            sqldb.conn.commit()


    def check_info(self, sqldb: SQLiteDB, infofile: str = 'info/info.xlsx') -> None:
        """Check and update info file status.
        
        Args:
            sqldb (SQLiteDB): Database connection object
            infofile (str, optional): Path to info file. Defaults to 'info/info.xlsx'.
        """
        if self.info == 'Y':
            return
        if os.path.isfile(f'{self.workdir}/{infofile}'):
            self.info = 'Y'
            sqldb.update_tb_value_sql(self.proid, 'info', 'Y')
            sqldb.conn.commit()

    def check_data(self, sqldb: SQLiteDB, datasign: str = "Filter/GO.sign") -> None:
        """Check and update data status.
        
        Args:
            sqldb (SQLiteDB): Database connection object
            datasign (str, optional): Data signature file path. Defaults to "Filter/GO.sign".
        """
        if self.data == 'Y':
            return
        if os.path.isfile(f'{self.workdir}/{datasign}'):
            self.data = 'Y'
        else:
            if os.path.isfile(f'{self.workdir}/{datasign}'):
                self.data = 'Y'
        sqldb.update_tb_value_sql(self.proid, 'data', self.data)
        sqldb.conn.commit()

    def autoconf_exe(self, sqldb: SQLiteDB, analysis_dir: str = 'Analysis') -> None:
        """Execute auto-configuration for the project.
        
        Args:
            sqldb (SQLiteDB): Database connection object
            analysis_dir (str, optional): Analysis directory name. Defaults to 'Analysis'.
        """
        if self.autoconf == 'Y' or self.autoconf == 'err':
            return
        if self.info == "Y" and self.data == 'Y':
            conf = _get_yaml_data('~/.annoeva/cmd.yaml')
            aufoconf_programe = conf["autoconf"][self.ptype]

            shell = f'{self.workdir}/{analysis_dir}/autoconf.sh'
            content = f'{aufoconf_programe} -in {self.workdir}/{analysis_dir} -t {self.ptype}'

            try:
                generate_shell(shell, content)
                #self.autoconf == 'Y'
            except Exception as e:
                #with open(f'{shell}.e', "w") as f:
                #    f.write(e)
                self.autoconf = 'err'
                self.conf_stde = e
                sqldb.update_tb_value_sql(self.proid, 'autoconf', 'err')
                sqldb.update_tb_value_sql(self.proid, 'conf_stde', e)
                sqldb.conn.commit()
                return

        tss = subprocess.Popen(f"sh {shell}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdo, stde = tss.communicate()
        autoconf_stdout, autoconf_stderr = str(stdo,'utf-8'), str(stde,'utf-8')
        prosper = autoconf_stderr.split('\n')
        if len(prosper) >= 2:
            prosper = prosper[-2]
        else:
            prosper = '-'

        if prosper == "Live_long_and_prosper":
            if self.run_num == 0:
                worksh = f'{self.workdir}/{analysis_dir}/work.sh'
                decorate_shell(worksh)
            self.autoconf = 'Y'
        else:
            self.autoconf = 'err'
            self.conf_stde = autoconf_stderr

        sqldb.update_tb_value_sql(self.proid, 'autoconf', self.autoconf)
        sqldb.update_tb_value_sql(self.proid, 'conf_stde', self.conf_stde)
        sqldb.conn.commit()

    def at_sh(self, sqldb: SQLiteDB, analysis_dir: str = 'Analysis') -> None:
        """Execute the work shell script for the project.
        
        Args:
            sqldb (SQLiteDB): Database connection object
            analysis_dir (str, optional): Analysis directory name. Defaults to 'Analysis'.
        """
        if self.autoconf != 'Y':
            return
        if self.pstat != '-':
            return

        shell = f'{self.workdir}/{analysis_dir}/work.sh'
        if os.path.isfile(shell):
            work_stdout = f'{shell}.o'
            work_stderr = f'{shell}.e'
            stdo = open(work_stdout, "w")
            stde = open(work_stderr, "w")

            os.chdir(f'{self.workdir}/{analysis_dir}')
            qsub_proc = subprocess.Popen(f'/bin/sh {shell}', shell=True, stdout=stdo, stderr=stde)
            self.pid = qsub_proc.pid
            self.p_args = qsub_proc.args
            self.stime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.pstat = 'run'
        else:  
            self.pstat = 'err'
            with open(f'{shell}.e', "w") as f:
                f.write('work.sh not found!') 
        
        sqldb.update_tb_value_sql(self.proid, 'pid', self.pid)
        sqldb.update_tb_value_sql(self.proid, 'p_args', self.p_args)
        sqldb.update_tb_value_sql(self.proid, 'stime', self.stime)
        sqldb.update_tb_value_sql(self.proid, 'pstat', self.pstat)
        sqldb.conn.commit()

    def check_work_stat(self, sqldb: SQLiteDB, analysis_dir: str = 'Analysis') -> None:
        """Check and update the work status of the project.
        
        Args:
            sqldb (SQLiteDB): Database connection object
            analysis_dir (str, optional): Analysis directory name. Defaults to 'Analysis'.
        """
        if self.pstat in ["done", "err"]:
            return

        need_check = False
        if self.pid in psutil.pids():
            p = psutil.Process(self.pid)
            if len(p.cmdline()) > 0 and p.cmdline() == self.p_args.split():
                return
            else:
                need_check = True
        else:
            need_check = True

        if need_check == False:
            return

        shell = f'{self.workdir}/{analysis_dir}/work.sh'
        if os.path.isfile(f'{shell}.sign'):
            self.pstat = 'done'
        else:
            self.pstat = 'err'

        self.etime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sqldb.update_tb_value_sql(self.proid, 'pstat', self.pstat)
        sqldb.update_tb_value_sql(self.proid, 'etime', self.etime)  # 项目结束时间   
        sqldb.conn.commit()
