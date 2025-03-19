from mag_tools.model.base_enum import BaseEnum

class DbType(BaseEnum):
    MYSQL = (1, "mysql", "jdbc:mysql://%s:%s/%s?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai", 3306, "com.mysql.cj.jdbc.Driver", "MySQL")
    ORACLE = (2, "oracle", "jdbc:oracle:thin:@%s:%s%s", 1521, "oracle.jdbc.driver.OracleDriver", "Oracle")
    SQL_SERVER = (3, "sqlserver", "jdbc:sqlserver://%s:%s;DatabaseName=%s;encrypt=false", 1433, "com.microsoft.sqlserver.jdbc.SQLServerDriver", "SQL Server")
    POSTGRE_SQL = (4, "postgresql", "jdbc:postgresql://%s:%s/%s", 5432, "org.postgresql.Driver", "PostgreSQL")
    DM = (5, "dm", "jdbc:dm://%s:%s/%s", 5236, "dm.jdbc.driver.DmDriver", "DM")
    DB2 = (6, "db2", "jdbc:db2://%s:%s/%s", 5000, "com.ibm.db2.jcc.DB2Driver", "DB2")

    def __init__(self, code, value, url, port, driver_class_name, desc):
        super().__init__(code, desc)
        self._value = value
        self._url = url
        self._port = port
        self._driver_class_name = driver_class_name

    @property
    def value(self):
        return self._value

    @property
    def url(self):
        return self._url

    @property
    def port(self):
        return self._port

    @property
    def driver_class_name(self):
        return self._driver_class_name

    @staticmethod
    def of(code_or_value):
        for db_type in DbType:
            if isinstance(code_or_value, int) and db_type.code == code_or_value:
                return db_type
            elif isinstance(code_or_value, str) and db_type.value == code_or_value:
                return db_type
        return None

if __name__ == '__main__':
    # 示例用法
    _db_type = DbType.of("mysql")
    print(f"Code: {_db_type.code}, Desc: {_db_type.desc}, URL: {_db_type.url}, Port: {_db_type.port}, Driver: {_db_type.driver_class_name}, Display Name: {_db_type.desc}")
