import pandas as pd
import json

def pd_to_level_1_dict(df):
    for (level_1), df_l1_grouped in df.groupby(["level_1"]):
        yield {
            "level_1_name": level_1,
            "level_2": list(pd_to_level_2_dict(df_l1_grouped))
        }

def pd_to_level_2_dict(df_l1_grouped):
    for row in df_l1_grouped.itertuples():
        yield {
            "level_2_name": row.level_2,
            "symptoms": keyword_parser(row.keywords)
        }

def keyword_parser(df_kw):
    return [w.strip() for w in df_kw.split(";")]


def main():
    df = pd.read_csv('disorders.csv')
    result_list = list(pd_to_level_1_dict(df))
    result_dict = {}
    for sub_dict in result_list:
        result_dict.update(sub_dict)
    print((json.dumps(result_list, ensure_ascii=False, indent=4).encode('utf-8')).decode())
    
if __name__ == '__main__':
    main()