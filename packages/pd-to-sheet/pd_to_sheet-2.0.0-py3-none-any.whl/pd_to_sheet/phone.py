import pandas
from pandas import ExcelWriter
from pathlib2 import Path
from pd_to_sheet.to_excel import save_df_to_sheet
from sqlalchemy import create_engine


def get_mobile_area(df, mobile_column):
    db_file_path = Path(__file__).parent.joinpath('db', 'MobileArea.db')
    sql_engine = create_engine(f'sqlite:///{db_file_path}')
    con = sql_engine.connect()
    df['mobile_7'] = df[mobile_column].apply(lambda x: str(x)[0:7])
    mobile_list = tuple(set(df['mobile_7']))
    read_sql = f"select `号段`,`省区`,`城市`,`服务商` as `运营商` from phone where `号段` in {mobile_list}"
    mobile_df = pandas.read_sql(sql=read_sql, con=con)
    res_df = pandas.merge(left=df, right=mobile_df, how='left', left_on='mobile_7', right_on='号段')
    rename = {
        "省区": f"{mobile_column}归属省区",
        "城市": f"{mobile_column}归属城市",
        "运营商": f"{mobile_column}归属运营商"
    }
    res_df.rename(columns=rename, inplace=True)
    res_df.drop(columns=['mobile_7', '号段'], inplace=True)
    con.close()
    return res_df