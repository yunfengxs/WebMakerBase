
import json
from typing import List, Dict, Tuple
from FileReader import SQLFileReader
from SQLParser import SQLParser
from GenEnums import EnumGenerator
from TSGenerator import TypeScriptClassGenerator

def convert_sql_to_dict(sql: str) -> Dict:
    parser = SQLParser(sql)
    return parser.parse()

# 示例用法
if __name__ == "__main__":
    file_path = 'tables.sql'  # 替换为你的文件路径
    reader = SQLFileReader(file_path)
    sql_statements = []
    sql_dicts = []
    try:
        sql_statements = reader.get_sql_statements()
        # for idx, statement in enumerate(sql_statements):
        #     print(f"Statement {idx + 1}:\n{statement}\n")
    except Exception as e:
        print(e)
    for onesql in sql_statements:
        sql_dicts.append(convert_sql_to_dict(onesql))
    generator = EnumGenerator(sql_dicts)
    generator.generate_enum_file('../out/enums.ts')  # 指定输出文件路径
    updated_dict = generator.get_updated_dict()

    generator = TypeScriptClassGenerator(updated_dict, 'inheritance.txt')
    generator.generate_files('../out/')