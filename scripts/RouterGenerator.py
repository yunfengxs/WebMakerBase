import os

class TypeScriptRouterGenerator:
    def __init__(self, table_info):
        self.table_info = table_info
        self.table_name = table_info['table_name']
        self.fields = table_info['fields']
        self.valid_fields = []
        self.auto_increment_fields = set()
        self.timestamp_fields = set()

        self._process_fields()

    def _process_fields(self):
        """处理表字段，分类为有效字段、自动增长字段、时间戳字段"""
        for field in self.fields:
            name = field['name']
            field_type = field['type']
            length = field.get('length')
            default_value = field.get('default')
            enum_value = field.get('enum_value')
            increase = field.get('AUTO_INCREMENT')

            if increase:  # 自动增长字段
                self.auto_increment_fields.add(name)
                continue  # 不需要包含在 INSERT 和 UPDATE 语句中

            if field_type == 'TIMESTAMP' and default_value == 'CURRENT_TIMESTAMP':
                self.timestamp_fields.add(name)  # 默认值为 CURRENT_TIMESTAMP 的时间字段
                continue  # 时间字段不需要包含在 INSERT 和 UPDATE 语句中

            self.valid_fields.append((name, field_type, length, default_value, enum_value))

    def generate_router_code(self):
        """生成 TypeScript 路由代码"""
        insert_fields = [field[0] for field in self.valid_fields]
        insert_placeholders = ', '.join(['?' for _ in insert_fields])
        update_fields = [f'{field[0]} = ?' for field in self.valid_fields]
        update_placeholders = ', '.join(update_fields)

        router_template = f"""
import express, {{ Request, Response }} from 'express';
import pool from '../db';

const router = express.Router();

// 创建类型保护函数
function isError(error: unknown): error is Error {{
  return error instanceof Error;
}}

// 创建{self.table_name}（C）
router.post('/', async (req: Request, res: Response) => {{
  const {{ {', '.join(insert_fields)} }} = req.body;

  let values = [{', '.join([f"req.body.{field[0]}" for field in self.valid_fields])}];

  let query = `INSERT INTO {self.table_name} ({', '.join(insert_fields)}) VALUES ({insert_placeholders})`;

  try {{
    const [result] = await pool.query(query, values);
    res.status(201).json({{
      id: (result as any).insertId,
      {', '.join([field[0] for field in self.valid_fields if field[0] not in self.auto_increment_fields])},
    }});
  }} catch (error) {{
    if (isError(error)) {{
      res.status(500).json({{ error: error.message }});
    }} else {{
      res.status(500).json({{ error: 'Unknown error' }});
    }}
  }}
}});

// 获取所有{self.table_name}（R）
router.get('/', async (req: Request, res: Response) => {{
  try {{
    const [rows] = await pool.query('SELECT * FROM {self.table_name}');
    res.json(rows);
  }} catch (error) {{
    if (isError(error)) {{
      res.status(500).json({{ error: error.message }});
    }} else {{
      res.status(500).json({{ error: 'Unknown error' }});
    }}
  }}
}});

// 获取单个{self.table_name}（R）
router.get('/:id', async (req: Request, res: Response) => {{
  const {{ id }} = req.params;
  try {{
    const [rows] = await pool.query('SELECT * FROM {self.table_name} WHERE id = ?', [id]);
    if ((rows as any[]).length > 0) {{
      res.json((rows as any)[0]);
    }} else {{
      res.status(404).json({{ message: '{self.table_name} not found' }});
    }}
  }} catch (error) {{
    if (isError(error)) {{
      res.status(500).json({{ error: error.message }});
    }} else {{
      res.status(500).json({{ error: 'Unknown error' }});
    }}
  }}
}});

// 更新{self.table_name}（U）
router.put('/:id', async (req: Request, res: Response) => {{
  const {{ id }} = req.params;
  const {{ {', '.join([field[0] for field in self.valid_fields])} }} = req.body;

  let values = [{', '.join([f"req.body.{field[0]}" for field in self.valid_fields])}, id];

  let query = `UPDATE {self.table_name} SET {update_placeholders} WHERE id = ?`;

  try {{
    const [result] = await pool.query(query, values);
    if ((result as any).affectedRows > 0) {{
      res.json({{ id, {', '.join([field[0] for field in self.valid_fields])} }});
    }} else {{
      res.status(404).json({{ message: '{self.table_name} not found' }});
    }}
  }} catch (error) {{
    if (isError(error)) {{
      res.status(500).json({{ error: error.message }});
    }} else {{
      res.status(500).json({{ error: 'Unknown error' }});
    }}
  }}
}});

// 删除{self.table_name}（D）
router.delete('/:id', async (req: Request, res: Response) => {{
  const {{ id }} = req.params;
  try {{
    const [result] = await pool.query('DELETE FROM {self.table_name} WHERE id = ?', [id]);
    if ((result as any).affectedRows > 0) {{
      res.status(204).send();
    }} else {{
      res.status(404).json({{ message: '{self.table_name} not found' }});
    }}
  }} catch (error) {{
    if (isError(error)) {{
      res.status(500).json({{ error: error.message }});
    }} else {{
      res.status(500).json({{ error: 'Unknown error' }});
    }}
  }}
}});

export default router;
"""
        return router_template

    def save_to_file(self, output_path):
        """将生成的 TypeScript 路由代码保存到文件"""
        code = self.generate_router_code()
        with open(output_path, 'w', encoding="UTF-8") as file:
            file.write(code)


class RouterFileGenerator:
    def __init__(self, table_infos, output_directory):
        self.table_infos = table_infos
        self.output_directory = output_directory

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    def generate_ts_routers(self):
        """根据输入的表信息数组生成 TypeScript 路由文件"""
        for table_info in self.table_infos:
            table_name = table_info['table_name']
            generator = TypeScriptRouterGenerator(table_info)
            output_path = os.path.join(self.output_directory, f'{table_name}_router.ts')
            generator.save_to_file(output_path)

# 使用示例
table_infos = [
    {
        'table_name': 'users',
        'fields': [
            {'name': 'id', 'type': 'INT', 'AUTO_INCREMENT': 'AUTO_INCREMENT'},
            {'name': 'name', 'type': 'VARCHAR', 'length': '100'},
            {'name': 'email', 'type': 'VARCHAR', 'length': '100'},
            {'name': 'age', 'type': 'INT'},
            {'name': 'status', 'type': 'enum', 'enum_value': ['active', 'inactive'], 'default': 'active', 'type_name': 'STATUS'},
            {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}
        ]
    },
    {
        'table_name': 'users_mul',
        'fields': [
            {'name': 'id', 'type': 'INT', 'AUTO_INCREMENT': 'AUTO_INCREMENT'},
            {'name': 'name', 'type': 'VARCHAR', 'length': '100'},
            {'name': 'email', 'type': 'VARCHAR', 'length': '100'},
            {'name': 'age', 'type': 'INT'},
            {'name': 'age1', 'type': 'INT'},
            {'name': 'status', 'type': 'enum', 'enum_value': ['active', 'inactive'], 'default': 'active', 'type_name': 'STATUS'},
            {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}
        ]
    }
]