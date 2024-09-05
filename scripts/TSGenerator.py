class TypeScriptClassGenerator:
    def __init__(self, tables, inheritance_file):
        self.tables = tables
        self.inheritance = self.read_inheritance_file(inheritance_file)
        self.table_to_enums = {}  # 用于记录每个表使用的枚举

    def read_inheritance_file(self, filename):
        inheritance = {}
        with open(filename, 'r') as file:
            lines = file.readlines()
        for line in lines:
            parts = line.strip().split(' extends ')
            if len(parts) == 2:
                child, parent = parts
                inheritance[child] = parent
        return inheritance

    def scan_for_enums(self):
        # 扫描字段，记录每个表使用的枚举类型
        for table in self.tables:
            table_name = table['table_name']
            enums = {field['type_name'] for field in table['fields'] if field['type'] == 'enum'}
            if enums:
                self.table_to_enums[table_name] = enums

    def translate_type(self, field):
        type_mapping = {
            'VARCHAR': 'string',
            'INTEGER': 'number',
            'REAL': 'number',
            'INT': 'number'
        }
        if field['type'] == 'enum':
            return field['type_name']
        return type_mapping.get(field['type'], 'any')

    def gen_enums_import(self, enums):
        if not enums:
            return ""
        enum_imports = ["import {"]
        for enum in enums:
            enum_imports.append(f"  {enum},")
        enum_imports.append("} from \"./enums\";")
        return "\n".join(enum_imports)

    def gen_constructor_params(self, parent_fields, child_fields):
        params = []
        if parent_fields:
            for field in parent_fields:
                field_name = field['name']
                ts_type = self.translate_type(field)
                params.append(f"{field_name}: {ts_type}")
        if child_fields:
            for field in child_fields:
                field_name = field['name']
                ts_type = self.translate_type(field)
                params.append(f"{field_name}: {ts_type}")
        return ", ".join(params)

    def gen_super_call(self, parent_fields):
        if parent_fields:
            parent_param_names = ", ".join([field['name'] for field in parent_fields])
            return f"    super({parent_param_names});\n"
        return ""

    def gen_field_assignments(self, child_fields):
        assignments = []
        for field in child_fields:
            field_name = field['name']
            assignments.append(f"    this.{field_name} = {field_name};")
        return "\n".join(assignments)

    def gen_constructor(self, parent_fields, child_fields, parent_class=None):
        params = self.gen_constructor_params(parent_fields, child_fields)
        super_call = self.gen_super_call(parent_fields)
        field_assignments = self.gen_field_assignments(child_fields)

        # 默认构造函数定义
        constructor = f"  constructor({params}) {{\n"

        # 如果有父类，则添加 super 调用
        if parent_class:
            constructor += super_call

        # 添加字段赋值
        constructor += field_assignments + "\n  }"

        return constructor

    def to_typescript_definition(self, table_name, fields, parent_class=None, enums=None):
        imports = []
        if enums:
            imports.append(self.gen_enums_import(enums))
        if parent_class:
            imports.append(f"import {{ {parent_class} }} from './{parent_class}';")

        ts_definitions = []
        if imports:
            ts_definitions.append("\n".join(imports))
        ts_definitions.append(f"export class {table_name} {f'extends {parent_class}' if parent_class else ''} {{")
        for field in fields:
            ts_type = self.translate_type(field)
            comment = field.get('comment', '')
            ts_definitions.append(f"  {field['name']}: {ts_type};  // {comment}")

        # 构造函数应在字段定义之后生成
        if parent_class:
            parent_fields = self.get_table_fields(parent_class.lower())
            ts_definitions.append(self.gen_constructor(parent_fields, fields, parent_class))
        else:
            ts_definitions.append(self.gen_constructor([], fields))

        # 添加 getMetadata 方法
        ts_definitions.append(self.gen_get_metadata_method(table_name))

        ts_definitions.append("}")
        return "\n".join(ts_definitions)

    def gen_get_metadata_method(self, table_name):
        """生成 getMetadata 方法的 TypeScript 代码"""
        metadata_lines = []
        for field in self.get_table_fields(table_name.lower()):
            field_name = field['name']
            ts_type = self.translate_type(field)
            increase = field.get('AUTO_INCREMENT')

            default_value = field.get('default', 'undefined')
            if (field['type'] == 'enum'):
                if default_value == 'default':
                    default_value = field['type_name'] + "." + default_value.upper()
                else:
                    default_value = field['type_name'] + "." + field['enum_value'][0].upper()
            if ts_type == 'string':
                default_value = "\"" + default_value + "\""
            if field['type'] == 'TIMESTAMP':
                default_value = '"now"'

            comment = field.get('comment', '')
            if increase:
                metadata_lines.append(
                    f"        {{ 'name': '{field_name}',"
                    f" 'type': '{ts_type}',"
                    f" 'default': {default_value},"
                    f" 'comment': '{comment}',"
                    f" 'auto_increase': '{increase}'"
                    f" }},"  # 注意这里添加逗号
                )
            else:
                metadata_lines.append(
                    f"        {{ 'name': '{field_name}',"
                    f" 'type': '{ts_type}',"
                    f" 'default': {default_value},"
                    f" 'comment': '{comment}',"
                    f" }},"  # 注意这里添加逗号
                )
        return (
                "  static getMetadata(): object {\n"
                + "    return {\n"
                + "       'class_name':'"+ table_name +"',\n"
                + "       'fields': [\n"
                + "\n".join(metadata_lines) + "\n"
                + "    ]};\n"
                + "  }"
        )

    def get_table_fields(self, table_name):
        for table in self.tables:
            if table['table_name'] == table_name:
                return table['fields']
        return []

    def write_to_file(self, filename, content):
        with open(filename, 'w', encoding="UTF-8") as file:
            file.write(content)

    def generate_files(self, filepath):
        self.scan_for_enums()

        # 生成父类文件
        parent_tables = set(self.inheritance.values())
        generated_files = set()

        for table in self.tables:
            table_name = table['table_name'].capitalize()
            if table_name not in generated_files:
                enums = self.table_to_enums.get(table['table_name'], set())
                fields = self.get_table_fields(table['table_name'])
                if fields:
                    ts_definition = self.to_typescript_definition(table_name, fields, enums=enums)
                    self.write_to_file(f"{filepath}{table_name}.ts", ts_definition)
                    generated_files.add(table_name)

        # 生成子类文件
        for child, parent in self.inheritance.items():
            child_name = child.capitalize()
            parent_name = parent.capitalize()

            parent_fields = self.get_table_fields(parent)
            child_fields = self.get_table_fields(child)

            if not parent_fields:
                print(f"无法找到父表 '{parent}' 的字段信息。")
                continue

            if not child_fields:
                print(f"无法找到子表 '{child}' 的字段信息。")
                continue

            child_field_names = {field['name'] for field in child_fields}
            parent_field_names = {field['name'] for field in parent_fields}
            unique_child_fields = [field for field in child_fields if field['name'] not in parent_field_names]

            if unique_child_fields:
                child_enums = self.table_to_enums.get(child, set())
                child_ts_definition = self.to_typescript_definition(child_name, unique_child_fields,
                                                                    parent_class=parent_name, enums=child_enums)
                self.write_to_file(f"{filepath}{child_name}.ts", child_ts_definition)

