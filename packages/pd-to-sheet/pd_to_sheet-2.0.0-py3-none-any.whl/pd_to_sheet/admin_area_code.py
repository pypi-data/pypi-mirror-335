import re

import pandas
from pathlib import Path
from sqlalchemy import create_engine
from datetime import datetime

nationalities = [
    "壮族", "满族", "回族", "苗族", "维吾尔族", "土家族", "彝族",
    "蒙古族", "藏族", "布依族", "侗族", "瑶族", "朝鲜族", "白族", "哈尼族",
    "哈萨克族", "傣族", "黎族", "傈僳族", "佤族", "畲族", "高山族", "拉祜族",
    "水族", "东乡族", "纳西族", "景颇族", "柯尔克孜族", "达斡尔族", "仫佬族",
    "羌族", "布朗族", "撒拉族", "毛南族", "仡佬族", "锡伯族", "阿昌族", "普米族",
    "塔吉克族", "怒族", "乌孜别克族", "俄罗斯族", "鄂温克族", "德昂族", "保安族",
    "裕固族", "京族", "塔塔尔族", "独龙族", "鄂伦春族", "赫哲族", "门巴族", "珞巴族"
]


# 定义一个函数来计算年龄
def calculate_age(id_number):
    try:
        birth_date = datetime.strptime(id_number[6:14], '%Y%m%d')
    except:
        return None
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def replace_nationality(address):
    pattern = '.+自治|'.join(re.escape(nation) for nation in nationalities)
    return address.replace(pattern, '', regex=True)


def admin_code_search(id_card_num_list):
    current_dir_path = Path(__file__).parent
    case_db_file_path = current_dir_path.joinpath('db', 'admin_area_code.db')
    print(case_db_file_path)
    print(case_db_file_path.exists())
    current_sql_engine = create_engine(f'sqlite:///{case_db_file_path}')
    with current_sql_engine.connect() as current_con:
        if not id_card_num_list:
            return pandas.DataFrame()
        if isinstance(id_card_num_list, (list, tuple, set)):
            all_admin_code_list = []
            for id_card_num in id_card_num_list:
                if not id_card_num:
                    continue
                admin_code = id_card_num[:6]
                all_admin_code_list.append(admin_code)
            all_admin_code_tuple = tuple(set(all_admin_code_list))  # 去重行政区划代码，
            # 注意：当元组内只有一个元素时，那个元素后面会有一个逗号
            if len(all_admin_code_tuple) == 1:
                sql = f"SELECT code as `行政区划代码`,province as `省份`,city as `地市`,county as `区县` FROM AdminCode where code = '{all_admin_code_tuple[0]}'"
            else:
                sql = f"SELECT code as `行政区划代码`,province as `省份`,city as `地市`,county as `区县` FROM AdminCode where code in {all_admin_code_tuple}"
            df = pandas.read_sql(sql, current_sql_engine)
            df = df.apply(replace_nationality, axis=1)  # 去掉行政区划代码中的民族自治表述
            return df
        else:
            return pandas.DataFrame()


def get_admin_area(df, admin_column, res_column_prefix=None):
    if not res_column_prefix:
        res_column_prefix = admin_column
    current_dir_path = Path(__file__).parent
    case_db_file_path = current_dir_path.joinpath('db', 'admin_area_code.db')
    current_sql_engine = create_engine(f'sqlite:///{case_db_file_path}')
    df['行政区划代码'] = df[admin_column].apply(lambda x: str(x)[0:6])
    all_admin_code_tuple = tuple(df['行政区划代码'].unique().tolist())
    # 注意：当元组内只有一个元素时，那个元素后面会有一个逗号
    if len(all_admin_code_tuple) == 1:
        sql = f"SELECT code as `行政区划代码`,province as `{res_column_prefix}省份`,city as `{res_column_prefix}地市`,county as `{res_column_prefix}区县` FROM AdminCode where code = '{all_admin_code_tuple[0]}'"
    else:
        sql = f"SELECT code as `行政区划代码`,province as `{res_column_prefix}省份`,city as `{res_column_prefix}地市`,county as `{res_column_prefix}区县` FROM AdminCode where code in {all_admin_code_tuple}"
    with current_sql_engine.connect() as con:
        admin_df = pandas.read_sql(sql, con).apply(replace_nationality, axis=1)
    res_df = pandas.merge(left=df, right=admin_df, how='left', on='行政区划代码').drop(columns=['行政区划代码'])
    res_df[f'{res_column_prefix}年龄'] = res_df[admin_column].apply(calculate_age)
    return res_df


if __name__ == '__main__':
    test_df = pandas.DataFrame({
        'id_card': ['42280233313213213213', '42080233313213213213', '42280233313213213213', '42280233313213213213'],
        'mobile': ['13812345678', '13812345678', '13812345678', '13812345678'],
        'address': ['湖北省仙桃市红山湖镇红山湖村', '湖北省仙桃市红山湖镇红山湖村', '湖北省仙桃市红山湖镇红山湖村', '湖北省仙桃市红山湖镇红山湖村'],
    })
    df = get_admin_area(test_df, 'id_card', 'id_card_')
    print(df)
