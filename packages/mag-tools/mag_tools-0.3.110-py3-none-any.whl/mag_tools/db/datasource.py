import mysql.connector

from mag_tools.db.datasource_info import DatasourceInfo
from model.db_type import DbType


class Datasource:
    def __init__(self, datasource_info: DatasourceInfo):
        self.__ds_info = datasource_info
        self.connection = None

    def connect(self):
        try:
            if self.__ds_info.db_type == DbType.MYSQL:
                self.connection = mysql.connector.connect(
                    host=self.__ds_info.host,
                    port=self.__ds_info.port,
                    user=self.__ds_info.username,
                    password=self.__ds_info.password,
                    database=self.__ds_info.db_name
                )
            elif self.__ds_info.db_type == DbType.POSTGRE_SQL:
                self.connection = None
                    # psycopg2.connect(
                    # host=self.__datasource_info.server_addr,
                    # user=self.__datasource_info.username,
                    # password=self.__datasource_info.password,
                    # dbname=self.__datasource_info.db_name
                    # )
            elif self.__ds_info.db_type == DbType.SQL_SERVER:
                self.connection = None
                # pyodbc.connect(
                #     f"DRIVER={{SQL Server}};SERVER={self.__datasource_info.server_addr};"
                #     f"DATABASE={self.__datasource_info.db_name};UID={self.__datasource_info.username};"
                #     f"PWD={self.__datasource_info.password}"
                # )
            else:
                print(f"不支持的数据库类型: {self.__ds_info.db_type}")
                return

            print("数据库连接成功！")
        except Exception as err:
            print(f"数据库连接失败: {err}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("数据库连接已关闭。")

if __name__ == "__main__":
    # 示例用法
    data_source_info = DatasourceInfo(
        host="192.168.0.110",
        port=3306,
        username="developer",
        password="Magnetitech*1212",
    )

    db_connector = Datasource(data_source_info)
    db_connector.connect()
    # 执行数据库操作
    db_connector.close()
