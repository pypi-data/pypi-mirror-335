import sqlite3
from pathlib import Path
import ipaddress
import pandas


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_ip_info(ip_list):
    import sqlite3
    import pandas
    from pathlib import Path
    import ipaddress
    # 去重并确保所有 IP 是合法的
    ip_list = set(ip_list)
    ip_data = []
    for ip in ip_list:
        ip_obj = ipaddress.ip_address(ip)
        xip = ''.join(ip_obj.exploded.split(':'))  # 转为无冒号的十六进制格式
        xip_bytes = bytes.fromhex(xip)  # 获取字节表示
        ip_data.append((str(ip), xip_bytes))

    # 数据库路径
    sqlite3_db_path = Path(__file__).parent.joinpath("db", "ipdata.db")

    # 创建数据库连接
    con = sqlite3.connect(sqlite3_db_path, timeout=5)
    con.row_factory = sqlite3.Row
    con.row_factory = dict_factory
    cur = con.cursor()
    # 创建临时表存储 IP 数据
    cur.execute("CREATE TEMP TABLE ip_query (ip TEXT, xip BLOB)")
    cur.executemany("INSERT INTO ip_query (ip, xip) VALUES (?, ?)", ip_data)

    result_df = pandas.DataFrame(cur.execute("select * from ip_query"))

    # 查询 IP 范围信息
    sql = f"""
        SELECT ip, country, province, city, area AS county, location AS isp FROM ip_query 
        LEFT JOIN ipv6_range_info ON xip 
        BETWEEN ip_start_num AND ip_end_num
        """
    cur.execute(sql)
    # 将结果转为 DataFrame
    result_df = pandas.DataFrame(cur)
    # 清理数据库连接
    con.close()
    return result_df




if __name__ == '__main__':
    ip_list = (['2409:8a34:9646:44b1:c828:c973:6d49:0b17', "2409:8934:9e00:5c7d:1562:0e69:a2e9:5660", "2409:8a4c:b212:83c0:90ea:f964:25fa:b51f"])
    res_df = get_ip_info(ip_list)
    print(res_df)
