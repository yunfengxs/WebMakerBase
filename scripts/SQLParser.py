import re
from typing import List, Dict, Tuple


class SQLParser:
    def __init__(self, sql: str):
        self.sql = sql
        self.tokens = self.tokenize(sql)
        self.index = 0

    # 词法分析器
    def tokenize(self, sql: str) -> List[Tuple[str, str]]:
        token_patterns = [
            (r'\bCREATE\b', 'CREATE'),
            (r'\bTABLE\b', 'TABLE'),
            (r'\bIF\b', 'IF'),
            (r'\bNOT\b', 'NOT'),
            (r'\bEXISTS\b', 'EXISTS'),
            (r'\bPRIMARY\b', 'PRIMARY'),
            (r'\bKEY\b', 'KEY'),
            (r'\bDEFAULT\b', 'DEFAULT'),
            (r'\bNULL\b', 'NULL'),
            (r'\bNOT\sNULL\b', 'NOT_NULL'),
            (r'\bAUTO_INCREMENT\b', 'AUTO_INCREMENT'),
            (r'\bUNIQUE\b', 'UNIQUE'),
            (r'\bCHECK\b', 'CHECK'),
            (r'\bCOMMENT\b', 'COMMENT'),
            (r'\bBOOLEAN\b', 'BOOLEAN'),
            (r'\bINTEGER\b', 'INTEGER'),
            (r'\bINT\b', 'INT'),
            (r'\bVARCHAR\b', 'VARCHAR'),
            (r'\bTEXT\b', 'TEXT'),
            (r'\bREAL\b', 'REAL'),
            (r'\bENUM\b', 'ENUM'),
            (r'\bTIMESTAMP\b', 'TIMESTAMP'),
            (r'\d+\.\d+', 'REAL_LITERAL'),
            (r'\d+', 'INTEGER_LITERAL'),
            (r'\(\d+\)', 'VARCHAR_LENGTH'),
            (r'\s+', None),
            (r'\(', 'LPAREN'),
            (r'\)', 'RPAREN'),
            (r',', 'COMMA'),
            (r';', 'SEMICOLON'),
            (r'\'[^\']*\'', 'STRING_LITERAL'),
            (r'\bCURRENT_TIMESTAMP\b', 'CURRENT_TIMESTAMP'),
            (r'\b\w+\b', 'IDENTIFIER'),
        ]

        token_regex = '|'.join(f'(?P<{pair[1]}>{pair[0]})' for pair in token_patterns)
        tokens = []

        for match in re.finditer(token_regex, sql, re.IGNORECASE):
            for group_name, value in match.groupdict().items():
                if group_name and value is not None and group_name != 'None':
                    tokens.append((group_name, value))

        return tokens

        # 处理 ENUM 类型

    def handle_enum(self, index: int) -> Tuple[List[str], int]:
        enum_values = []
        if index < len(self.tokens) and self.tokens[index][0] == 'LPAREN':
            index += 1
            while index < len(self.tokens) and self.tokens[index][0] != 'RPAREN':
                token_type, token_value = self.tokens[index]
                if token_type == 'STRING_LITERAL':
                    enum_values.append(token_value.strip("'"))
                elif token_type == 'COMMA':
                    index += 1
                    continue
                index += 1
            if index < len(self.tokens) and self.tokens[index][0] == 'RPAREN':
                index += 1
            else:
                return {'error': 'Unmatched parentheses in ENUM definition'}, index
        return enum_values, index - 1

        # 处理 IF NOT EXISTS

    def handle_if_not_exists(self, index: int) -> Tuple[Dict, int]:
        table_info = {}
        if index + 4 > len(self.tokens):
            return {'error': 'Incomplete IF NOT EXISTS statement'}, index
        if self.tokens[index][0] + self.tokens[index + 1][0] + self.tokens[index + 2][0] == 'IFNOTEXISTS':
            index += 3
        if index < len(self.tokens) and self.tokens[index][0] == 'IDENTIFIER':
            table_info['table_name'] = self.tokens[index][1]
            index += 1
        else:
            return {'error': 'Expected table name after TABLE'}, index

        return table_info, index

        # 解析字段定义

    def parse_field_definitions(self, index: int) -> Tuple[Dict, int]:
        table_info = {}
        current_field = None
        paren_stack = []

        while index < len(self.tokens):
            token_type, token_value = self.tokens[index]

            if token_type == 'LPAREN':
                paren_stack.append(index)

            elif token_type == 'RPAREN':
                if paren_stack:
                    paren_stack.pop()
                else:
                    return {'error': 'Unmatched closing parenthesis'}, index

            if not paren_stack and current_field:
                break

            if token_type == 'IDENTIFIER':
                if not current_field:
                    current_field = {'name': token_value}
                else:
                    current_field['name'] = token_value

            elif token_type == 'VARCHAR_LENGTH':
                if current_field and 'type' in current_field and current_field['type'] == 'VARCHAR':
                    current_field['length'] = token_value.strip('()')

            elif token_type in ['INTEGER', 'INT', 'VARCHAR', 'REAL', 'TIMESTAMP', 'TEXT', 'BOOLEAN']:
                if current_field:
                    current_field['type'] = token_value

            elif token_type == 'ENUM':
                enum_values, index = self.handle_enum(index + 1)
                if isinstance(enum_values, dict) and 'error' in enum_values:
                    return enum_values, index
                if current_field:
                    current_field['type'] = 'enum'
                    current_field['enum_value'] = enum_values

            elif token_type == 'REAL_LITERAL':
                if current_field:
                    current_field['default'] = token_value

            elif token_type == 'INTEGER_LITERAL':
                if current_field:
                    current_field['default'] = token_value

            elif token_type == 'CURRENT_TIMESTAMP':
                if current_field:
                    current_field['default'] = 'CURRENT_TIMESTAMP'

            elif token_type == 'DEFAULT':
                index += 1
                if index < len(self.tokens):
                    token_type, token_value = self.tokens[index]
                    if token_type in ['STRING_LITERAL', 'REAL_LITERAL', 'INTEGER_LITERAL', 'CURRENT_TIMESTAMP']:
                        current_field['default'] = token_value.strip("'")

            elif token_type == 'NOT_NULL':
                continue

            elif token_type == 'AUTO_INCREMENT':
                if current_field:
                    current_field['AUTO_INCREMENT'] = 'AUTO_INCREMENT'

            elif token_type == 'COMMENT':
                index += 1
                if index < len(self.tokens):
                    token_type, token_value = self.tokens[index]
                    if token_type == 'STRING_LITERAL':
                        current_field['comment'] = token_value.strip("'")

            elif token_type == 'COMMA':
                if current_field:
                    if 'name' in current_field and 'type' in current_field:
                        current_field = {k: v for k, v in current_field.items() if v is not None}
                        table_info.setdefault('fields', []).append(current_field)
                        current_field = None
            index += 1

        if paren_stack:
            return {'error': 'Unmatched opening parenthesis'}, index

        if current_field:
            current_field = {k: v for k, v in current_field.items() if v is not None}
            table_info.setdefault('fields', []).append(current_field)

        return table_info, index

    # 语法分析器
    def parse(self) -> Dict:
        table_info = {}
        self.index = 0

        while self.index < len(self.tokens):
            token_type, token_value = self.tokens[self.index]

            if token_type == 'CREATE':
                self.index += 1
                if self.index < len(self.tokens) and self.tokens[self.index][0] == 'TABLE':
                    self.index += 1
                    table_info, self.index = self.handle_if_not_exists(self.index)
                    if 'error' in table_info:
                        return table_info
                    if self.index < len(self.tokens) and self.tokens[self.index][0] == 'LPAREN':
                        field_info, self.index = self.parse_field_definitions(self.index)
                        if 'error' in field_info:
                            return field_info
                        table_info.update(field_info)

            self.index += 1

        return table_info