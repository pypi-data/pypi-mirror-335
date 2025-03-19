import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from annoeva.db.database import SQLiteDB

tbj = SQLiteDB(dbpath='cmd.projects.db')
tbj.crt_tb_sql()
