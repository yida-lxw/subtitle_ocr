import os
import sqlite3

from dbutils.persistent_db import PersistentDB

from config.db_config import DBConfig
from utils.logger import setup_logger
from utils.object_utils import ObjectUtils
from utils.string_utils import StringUtils

logger = setup_logger('db_pool')

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)

# 加载配置文件
db_config_path = "config/db.yml"
db_config_loaded = DBConfig.load_db_config(project_basepath, db_config_path)
db_dir = db_config_loaded.db_dir
db_dir = StringUtils.replaceBackSlash(db_dir)
db_dir = StringUtils.to_ends_with_back_slash(db_dir)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
db_name = db_config_loaded.db_name


class Pool(object):
    __pool = None
    config = {
        'database': db_dir + db_name
    }

    def __new__(cls, *args, **kwargs):
        if cls.__pool is None:
            cls.__pool = PersistentDB(sqlite3, maxusage=None, closeable=False, **cls.config)
        return cls.__pool


class Connect:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    def __enter__(self):
        self.conn = self.db_pool.connection()
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()


class SQLTemplate:
    def __init__(self):
        self.db_pool = Pool()

    def find_by_id(self, table_name: str, id_value, id_field_name: str = "id"):
        select_sql = f"select * from {table_name} where {id_field_name} = ?"
        result = {}
        try:
            with Connect(self.db_pool) as connection:
                select_sql = (select_sql.replace("'" + table_name + "'", table_name)
                              .replace("'" + id_field_name + "'", id_field_name))
                connection.cur.execute(select_sql, (id_value,))
                result = connection.cur.fetchone()
        except Exception as e:
            logger.error(
                f"As find the record with id_val:{id_value} from DB with sql: {select_sql} oocur exception: {e}")
        finally:
            return result

    def query_count(self, count_sql, args=None):
        result = {}
        try:
            with Connect(self.db_pool) as connection:
                if not args:
                    connection.cur.execute(count_sql)
                else:
                    connection.cur.execute(count_sql, args)
                result = connection.cur.fetchone()
        except Exception as e:
            logger.error(f"As query count from DB with sql: {count_sql} oocur exception: {e}")
        finally:
            if result is None:
                result = 0
            elif ObjectUtils.is_tuple(result) or ObjectUtils.is_list(result):
                result = result[0]
            elif ObjectUtils.is_str(result):
                if "." in result:
                    result = float(result)
                else:
                    result = int(result)
            elif ObjectUtils.is_int(result):
                result = result
            return result


    def find_one(self, sql, args=None):
        result = {}
        try:
            with Connect(self.db_pool) as connection:
                if not args:
                    connection.cur.execute(sql)
                else:
                    connection.cur.execute(sql, args)
                result = connection.cur.fetchone()
        except Exception as e:
            logger.error(f"As query only one record from DB with sql: {sql} oocur exception: {e}")
        finally:
            return result


    def find_many(self, sql, args=None):
        result = []
        try:
            with Connect(self.db_pool) as connection:
                if not args:
                    connection.cur.execute(sql)
                else:
                    connection.cur.execute(sql, args)
                result = connection.cur.fetchall()
        except Exception as e:
            logger.error(f"As query many records from DB with sql: {sql} oocur exception: {e}")
        finally:
            return result

    def delete_by_id(self, table_name: str, id_value, id_field_name: str = "id"):
        delete_sql = f"DELETE FROM {table_name} WHERE {id_field_name} = ?"
        effect_row = 0
        try:
            with Connect(self.db_pool) as connection:
                delete_sql = (delete_sql.replace("'" + table_name + "'", table_name)
                              .replace("'" + id_field_name + "'", id_field_name))
                connection.cur.execute(delete_sql, [id_value])
                effect_row = connection.cur.rowcount
                connection.conn.commit()
        except Exception as e:
            logger.error(
                f"As delete the record with id_val:{id_value} from DB with sql: {delete_sql} oocur exception: {e}")
            connection.conn.rollback()
        finally:
            if effect_row is None:
                effect_row = 0
            return effect_row

    def insert(self, sql, return_id: bool = False, args=None):
        effect_row = 0
        new_id = None
        try:
            with Connect(self.db_pool) as connection:
                if not args:
                    effect_row = connection.cur.execute(sql)
                else:
                    effect_row = connection.cur.execute(sql, args)
                connection.conn.commit()
                if return_id:
                    rowcount = effect_row.rowcount
                    if rowcount > 0:
                        new_id = connection.cur.lastrowid
                    else:
                        new_id = -1
        except Exception as e:
            logger.error(f"As insert record into DB with sql: {sql} oocur exception: {e}")
            connection.conn.rollback()
        finally:
            if return_id:
                return new_id
            if effect_row is None:
                effect_row = 0
                return effect_row
            if ObjectUtils.is_int(effect_row):
                return effect_row
            return effect_row.rowcount

    def batch_insert(self, sql, args=None):
        effect_row = 0
        try:
            with Connect(self.db_pool) as connection:
                if not args:
                    effect_row = connection.cur.executemany(sql)
                else:
                    effect_row = connection.cur.executemany(sql, args)
                connection.conn.commit()
        except Exception as e:
            logger.error(f"As batch insert records into DB with sql: {sql} oocur exception: {e}")
            connection.conn.rollback()
        finally:
            if effect_row is None:
                effect_row = 0
            if ObjectUtils.is_int(effect_row):
                return effect_row
            return effect_row.rowcount

    def delete(self, sql, args=None):
        return self.insert(sql, return_id=False, args=args)

    def update(self, sql, args=None):
        return self.insert(sql, return_id=False, args=args)

    def create_table(self, create_table_sql: str):
        create_result = True
        try:
            with Connect(self.db_pool) as connection:
                connection.cur.execute(create_table_sql)
                print("Tables created successfully.")
        except Exception as e:
            create_result = False
        finally:
            return create_result


if __name__ == '__main__':
    sql_template = SQLTemplate()
    table_name = "subtitle_ocr"
    id_field_name = "id"
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS subtitle_ocr (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id  TEXT NOT NULL,
            subtitle TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            file_name TEXT NOT NULL
        );
    """
    file_hash = "fgjhrtyret3456513"
    task_id = "asdfasdfasdfasdfasdfasdfasdf"

    sql_template.create_table(create_table_sql)
    batch_insert_sql = "insert or ignore into subtitle_ocr(task_id,subtitle, file_hash, file_name) values(?, ?, ?, ?)"
    insert_params = []
    for i in range(1000):
        insert_params.append([task_id, f"subtitle_{i}", f"{file_hash}_{i}", f"file_name_{i}"])
    sql_template.batch_insert(batch_insert_sql, args=insert_params)


    count_sql = "select count(*) from subtitle_ocr"
    total_count = sql_template.query_count(count_sql, args=None)
    print(f"total_count --> {total_count}")


