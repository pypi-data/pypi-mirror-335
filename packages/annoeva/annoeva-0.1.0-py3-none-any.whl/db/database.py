import os
import sqlite3
from dataclasses import dataclass, field
from typing import Optional
from pandas import read_sql, Series, DataFrame

@dataclass
class SQLiteDB:
    """
    A class to manage SQLite database operations for project tracking.
    
    Attributes:
        dbpath (str): Path to the SQLite database file
        conn (sqlite3.Connection): Database connection object
        cur (sqlite3.Cursor): Database cursor object
    """

    dbpath: str
    conn: sqlite3.Connection = field(init=False)
    cur: sqlite3.Cursor = field(init=False)

    def __post_init__(self):
        self.conn = sqlite3.connect(self.dbpath)
        self.cur = self.conn.cursor()

    def crt_tb_sql(self) -> None:
        """Create the projects table in the database if it doesn't exist.
        
        The table contains the following columns:
        id: primary key
        user: user name
        proid: subproject id, unique not null
        ptype: project product type
        workdir: workdir path
        dirstat: workdir status [Y|N]
        info: info.xlsx file status [Y|N]
        data: data status [Y|N|err]
        autoconf: auto config status [Y|N|err]
        conf_stde: auto config stderr
        worksh: work_qsubsge.sh file path
        pid: worksh run pid
        p_args: worksh run command args
        stime: worksh execute start time
        etime: worksh execute end time
        pstat: project status [run|done|err|-]
        run_num: project re-run number
        """
        id: primary key
        user: user name
        proid: subproject id, unique not null
        ptype: project product type, which product type's autoconf.py program in commander.yml needs to be invoked
        workdir: workdir path
        dirstat: workdir status [Y|N], default: N
        info: info.xlsx file status [Y|N], default: N
        data: data status [Y|N|err], default: N
        autoconf: auto config status [Y|N|err], default: N
        conf_stde: auto config stderr
        worksh: work_qsubsge.sh file path
        pid: worksh run pid
        p_args: worksh run command args
        stime: worksh execute start time
        etime: worksh execute end time
        pstat: project status, qsubsge_work.sh execute status [run|done|err|-], default: -
        run_num: project re-run number
        """
        crt_tb_sql_c = """
        create table if not exists projects(
        id integer primary key autoincrement unique not null,
        user text,
        proid text unique not null,
        ptype text,
        workdir text,
        dirstat text,
        info text,
        data text,
        autoconf text,
        conf_stde text,
        worksh text,
        pid text,
        p_args text,
        stime text,
        etime text,
        pstat text,
        run_num integer
        );"""

        self.cur.execute(crt_tb_sql_c)
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def insert_tb_sql(self, proid: str, ptype: str, workdir: str) -> None:
        """Insert a new project record into the database.
        
        Args:
            proid (str): Project ID
            ptype (str): Project type
            workdir (str): Working directory path
        """
        import getpass
        username = getpass.getuser()

        insert_sql = "insert into projects (user, proid, ptype, workdir, dirstat, info, data, autoconf, pstat, run_num) values (?,?,?,?,?,?,?,?,?,?)"
        self.cur.execute(insert_sql, (username, proid, ptype, workdir, 'N', 'N', 'N', 'N', '-', 0))
        self.conn.commit()

    def update_tb_value_sql(self, proid: str, name: str, value: str) -> None:
        """Update a specific field value for a project record.
        
        Args:
            proid (str): Project ID to update
            name (str): Field name to update
            value (str): New value to set
        """
        update_sql = f"update projects set \'{name}\'=\'{value}\' where proid=\'{proid}\'"
        self.cur.execute(update_sql)
        self.conn.commit()

    def query_record(self, key: str, value: str) -> DataFrame:
        """Query project records matching the given key-value pair.
        
        Args:
            key (str): Column name to query
            value (str): Value to match
            
        Returns:
            DataFrame: Pandas DataFrame containing matching records
            
        Raises:
            ValueError: If key is not a valid column name
        """
        valid_columns = ['id', 'user', 'proid', 'ptype', 'workdir', 'dirstat', 
                        'info', 'data', 'autoconf', 'conf_stde', 'worksh', 
                        'pid', 'p_args', 'stime', 'etime', 'pstat', 'run_num']
                        
        if key not in valid_columns:
            raise ValueError(f"Invalid column name: {key}")
            
        query = "SELECT * FROM projects WHERE ? = ?"
        df = read_sql(query, con=self.conn, params=(key, value))
        return df
    
    def delete_project(self, projectid: str) -> None:
        """Delete a project record and stop any running processes.
        
        Args:
            projectid (str): Project ID to delete
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            query = "SELECT * FROM projects WHERE proid = ?"
            df = read_sql(query, con=self.conn, params=(projectid,))
            df.reset_index(drop=True, inplace=True)
            
            if df.shape[0] == 0:
                print(f"project {projectid} not found")
                return
                
            self.cur.execute("DELETE FROM projects WHERE proid = ?", (projectid,))
            
            pid = df.loc[0, "pid"]
            if df.loc[0, "pstat"] == 'run' and pid:
                try:
                    os.kill(int(pid), 9)
                except (ProcessLookupError, ValueError):
                    print(f"Process {pid} not found or invalid")
                    
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            raise

    def close_db(self) -> None:
        """Close the database connection and cursor."""
        self.cur.close()
        self.conn.close()
