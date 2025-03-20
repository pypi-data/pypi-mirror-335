# 批量查询IP地址的归属地
import re
from pathlib import Path
import ipaddress
import pandas
from ip2Region import Ip2Region
from ipv6 import get_ip_info


def is_valid_ipv4(ip):
    try:
        # 尝试将字符串转换为IPv4地址
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        # 如果转换失败，则不是有效的IPv4地址
        return False


def is_valid_ipv6(ip):
    try:
        # 尝试将字符串转换为IPv6地址
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        # 如果转换失败，则不是有效的IPv6地址
        return False


def ip_area_search(ip_list):
    db_file_path = Path(__file__).parent.joinpath('db', 'ip2region.db')
    algorithm = "binary"
    searcher = Ip2Region(db_file_path)
    ip_area_result_list = []
    ipv6_list = []
    for ip in ip_list:
        ip = str(ip).strip()
        # 检查IP是否是有效IP
        if not is_valid_ipv4(ip):
            if is_valid_ipv6(ip):
                ipv6_list.append(ip)
                continue
            else:
                print(ip, "不是一个规范的IP地址")
                continue
        if algorithm == "binary":
            data = searcher.binarySearch(ip)
        elif algorithm == "memory":
            data = searcher.memorySearch(ip)
        else:
            data = searcher.btreeSearch(ip)
        result = data["region"].decode('utf-8')
        result_list = result.split("|")
        # ip数据段固定格式：_城市Id | 国家 | 区域 | 省份 | 城市 | ISP_
        # 如果是国内的IP就显示到城市，如果是国外的IP则显示国家和城市
        country = result_list[0]
        province = result_list[2]
        city = result_list[3]
        isp = result_list[4]
        ip_area_result_list.append({"ip": ip, "country": country, "province": province, "city": city, "isp": isp})
        # if country == "中国":
        #     ip_area_list = filter(None, [province, city, isp])  # 清除列表中的空元素：False，0，None，空字符串等
        #     ip_area_result_list.append({"ip": ip, "country": country, "province": province, "city": city, "isp": isp})
        # else:
        #     ip_area_list = filter(None, [country, province, city, isp])
        #     ip_area_result_list.append({"ip": ip, "isp": re.sub('\s*0', '', " ".join(ip_area_list))})
    searcher.close()
    ipv6_df = pandas.DataFrame()
    ipv4_df = pandas.DataFrame()
    if ipv6_list:
        ipv6_df = get_ip_info(ipv6_list)
    if ip_area_result_list:
        ipv4_df = pandas.DataFrame(ip_area_result_list)
        ipv4_df = ipv4_df.replace("0", "")
    return pandas.concat([ipv6_df, ipv4_df], ignore_index=True)


def get_ip_area(df, ip_column, res_column_prefix=None):
    """
    获取IP地址的归属地
    :param res_column_prefix: 结果列中显示的前缀
    :param df: DataFrame
    :param ip_column: IP地址列名
    :return: DataFrame
    """
    if not res_column_prefix:
        res_column_prefix = ip_column
    ip_list = df[ip_column].unique().tolist()
    result = ip_area_search(ip_list)
    rename_columns = {
        "country": f"{res_column_prefix}国家",
        "province": f"{res_column_prefix}省份",
        "city": f"{res_column_prefix}地市",
        "county": f"{res_column_prefix}区县",
        "isp": f"{res_column_prefix}运营商"
    }
    df = df.merge(result, how='left', left_on=ip_column, right_on='ip').rename(columns=rename_columns)
    if ip_column != 'ip':
        df.drop(columns=["ip"], inplace=True)
    df.fillna('', inplace=True)
    return df


if __name__ == '__main__':
    test_df = pandas.DataFrame({"ip": ["182.239.93.16", "2408:864e:b201::", '2409:8a34:9646:44b1:c828:c973:6d49:0b17', "2409:8934:9e00:5c7d:1562:0e69:a2e9:5660", "2409:8a4c:b212:83c0:90ea:f964:25fa:b51f"]})

    result = get_ip_area(test_df, "ip")
    print(result)
