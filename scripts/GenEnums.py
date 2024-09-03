from collections import defaultdict
import json


class EnumGenerator:
    def __init__(self, data_list):
        """
        初始化 EnumGenerator 实例，接收字典数组作为输入。
        :param data_list: 字典数组，每个字典代表一个表及其字段。
        """
        self.data_list = data_list

    def extract_enums(self):
        """从数据字典中提取枚举类型字段并合并相同值的枚举。"""
        enum_map = {}
        for data in self.data_list:
            for field in data.get('fields', []):
                if field['type'] == 'enum':
                    enum_name = field['name']
                    enum_values = field['enum_value']
                    enum_tuple = tuple(sorted(enum_values))
                    if enum_tuple not in enum_map:
                        enum_map[enum_tuple] = enum_name
        return enum_map

    def generate_typescript_enum(self, enum_name, enum_values):
        """生成 TypeScript 枚举字符串。"""
        enum_name = enum_name.upper()
        enum_str = f'export enum {enum_name} {{\n'
        for value in enum_values:
            enum_str += f'    {value.upper().replace(" ", "_")} = "{value}",\n'
        enum_str += '}'
        return enum_str

    def generate_enum_file(self, filename='enums.ts'):
        """生成包含所有枚举的 TypeScript 文件。
        :param filename: 输出的 TypeScript 文件路径。
        """
        enums = self.extract_enums()

        # 合并枚举定义
        merged_enums = defaultdict(list)
        for values, name in enums.items():
            merged_enums[name].extend(values)

        ts_enums = []
        for enum_name, enum_values in merged_enums.items():
            # 去重并排序
            enum_values = list(sorted(set(enum_values)))
            ts_enums.append(self.generate_typescript_enum(enum_name, enum_values))

        ts_content = '\n\n'.join(ts_enums)

        with open(filename, 'w', encoding="UTF-8") as f:
            f.write(ts_content)

        print(f"TypeScript enums have been generated and saved to {filename}")

    def convert_enum_to_class(self):
        """将字典数组中的 'enum' 类型字段转换为实际的枚举类名称。"""
        for data in self.data_list:
            for field in data.get('fields', []):
                if field['type'] == 'enum':
                    enum_name = field['name'].upper()
                    field['type_name'] = enum_name

    def get_updated_dict(self):
        """返回更新后的字典数组，其中 'enum' 类型字段已被转换为类名。"""
        self.convert_enum_to_class()
        return self.data_list