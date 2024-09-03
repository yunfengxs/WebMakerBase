import re

class SQLFileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sql_statements = []

    def _read_file(self):
        """Reads the content of the SQL file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"An error occurred while reading the file: {e}")

    def _parse_sql(self, sql_content):
        """Parses the SQL content and extracts CREATE TABLE statements."""
        # Split SQL content into statements based on the delimiter
        sql_statements = re.split(r';\s*(?=\bCREATE\s+TABLE\b)', sql_content, flags=re.IGNORECASE)

        # Remove any extra whitespace and add back the semicolon to the end of each statement
        sql_statements = [stmt.strip() + ';' for stmt in sql_statements if stmt.strip()]

        return sql_statements

    def get_sql_statements(self):
        """Gets the list of SQL statements."""
        sql_content = self._read_file()
        self.sql_statements = self._parse_sql(sql_content)
        return self.sql_statements

# 示例用法
if __name__ == "__main__":
    file_path = 'your_sql_file.sql'  # 替换为你的文件路径
    reader = SQLFileReader(file_path)
    try:
        sql_statements = reader.get_sql_statements()
        for idx, statement in enumerate(sql_statements):
            print(f"Statement {idx + 1}:\n{statement}\n")
    except Exception as e:
        print(e)