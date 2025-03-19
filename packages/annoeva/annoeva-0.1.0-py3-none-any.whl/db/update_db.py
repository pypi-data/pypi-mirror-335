import os
import sys
from pathlib import Path
from typing import Optional
from pandas import read_sql, Series, DataFrame
from annoeva.db import SQLiteDB, project
from annoeva._utils import format_cell

DB_PATH = str(Path.home() / '.annoeva' / 'projects.db')  # 数据库路径常量

def update_projects_status() -> None:
    """Update the status of all running or pending projects.
    
    This function checks and updates the directory status, info file status,
    data status, auto-configuration status, and work status for each project.
    
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        tbj = SQLiteDB(dbpath=DB_PATH)
        query = '''
            SELECT * FROM projects 
            WHERE pstat IN ('run', '-')
        '''
        projects = read_sql(query, con=tbj.conn)
        
        for i, row in projects.iterrows():
            try:
                pro = project.from_series(row)
                pro.check_dirstat(tbj)
                pro.check_info(tbj)
                pro.check_data(tbj)
                pro.autoconf_exe(tbj)
                pro.at_sh(tbj)
                pro.check_work_stat(tbj)
            except Exception as e:
                print(f"Error processing project {row['proid']}: {str(e)}")
                continue
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        tbj.close_db()

def cron(mode: int) -> None:
    """Run periodic tasks based on the specified mode.
    
    Args:
        mode (int): Operation mode (1: update status, 2: clean old projects)
        
    Raises:
        ValueError: If invalid mode is provided
    """
    if mode == 1:
        try:
            update_projects_status()
        except Exception as e:
            print(f"Failed to update project status: {e}")
            sys.exit(1)
    elif mode == 2:
        # TODO: Implement cleanup of old projects
        pass
    else:
        print("mode should be 1 or 2")
        sys.exit(1)

def addproject(projectid: str, pipetype: str, workdir: str) -> None:
    """Add a new project to the database.
    
    Args:
        projectid (str): Unique project identifier
        pipetype (str): Type of pipeline
        workdir (str): Working directory path
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        tbj = SQLiteDB(dbpath=DB_PATH)
        tbj.insert_tb_sql(projectid, pipetype, workdir)
    except sqlite3.Error as e:
        print(f"Failed to add project: {e}")
        raise
    finally:
        tbj.close_db()

def dele(projectid: str) -> None:
    """Delete a project from the database.
    
    Args:
        projectid (str): Unique project identifier to delete
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        tbj = SQLiteDB(dbpath=DB_PATH)
        tbj.delete_project(projectid)
    except sqlite3.Error as e:
        print(f"Failed to delete project: {e}")
        raise
    finally:
        tbj.close_db()

def rerun(projectid: str) -> None:
    """Reset a project's status to allow rerunning.
    
    Args:
        projectid (str): Unique project identifier to rerun
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        tbj = SQLiteDB(dbpath=DB_PATH)
        tbj.update_tb_value_sql(projectid, 'pstat', '-')
        tbj.update_tb_value_sql(projectid, 'run_num', 2)
    except sqlite3.Error as e:
        print(f"Failed to reset project status: {e}")
        raise
    finally:
        tbj.close_db()

def stat(projectid: Optional[str] = None) -> None:
    """Display project status information.
    
    Args:
        projectid (Optional[str]): Specific project ID to show details for.
            If None, shows summary status for all projects.
            
    Raises:
        ValueError: If projectid is invalid
        sqlite3.Error: If database operation fails
    """
    try:
        tbj = SQLiteDB(dbpath=DB_PATH)
        
        if projectid:
            if not isinstance(projectid, str) or len(projectid) == 0:
                raise ValueError("Invalid project ID format")
                
            query = "SELECT * FROM projects WHERE proid = ?"
            df = read_sql(query, con=tbj.conn, params=(projectid,))
            status = df.iloc[0].to_dict()
            status_str = f"{status['proid']} {status['ptype']}\n{status['worksh']}\nAutoconfig stderr: {status['conf_stde']}\npid: {status['pid']}\nwork.sh stderr: {status['worksh']}.e"
            print(status_str)
        else:
            df = read_sql("SELECT * FROM projects", con=tbj.conn)
            df = df[['proid', 'ptype', 'dirstat', 'info', 'data', 'autoconf', 'stime', 'etime', 'pstat']]
            
            import pandas as pd
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_colwidth', 20)
            pd.set_option('display.expand_frame_repr', False)

            for col in df.columns:
                max_width = max(df[col].astype(str).apply(len).max(), len(col))
                pd.set_option(f'display.max_colwidth', max_width)

            formatted_df = df.applymap(format_cell)
            print("\n", formatted_df.to_string(index=False, justify='left'))
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        tbj.close_db()
