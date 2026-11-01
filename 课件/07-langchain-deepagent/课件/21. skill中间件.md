# Skills 中间件

## Skills 文件结构

https://agentskills.io/specification

```
skills
└── skill-1/
      ├── SKILL.md          # 必须: metadata + instructions
      ├── scripts/          # 可选: 可执行的代码
      ├── references/       # 可选: 包含一些额外的文档，Agent可以在需要时阅读。
      ├── assets/           # 可选: 图片、schemas、...
      └── ...               # 任意其他文件
└── skill-2/
      ├── SKILL.md          # 必须: metadata + instructions
      ├── scripts/          # 可选: 可执行的代码
      ├── references/       # 可选: 包含一些额外的文档，Agent可以在需要时阅读。
      ├── assets/           # 可选: 图片、schemas、...
      └── ...               # 任意其他文件
```

## Skills 后端选型

| 存储方案 | 功能                     |
| -------- | ------------------------ |
| 沙箱     | 拥有全部功能             |
| 其他     | 除执行之外的其他所有功能 |

## SkillsMiddleware 的执行逻辑

```mermaid
flowchart TD
    A["create_deep_agent(skills=...)"] --> B["创建 SkillsMiddleware"]
    B --> C["before_agent / abefore_agent"]
    C --> D["扫描每个 source 的直接子目录"]
    D --> E["批量下载 */SKILL.md"]
    E --> F["解析 YAML Frontmatter"]
    F --> G["同名 Skill：后面的 source 覆盖前面的"]
    G --> H["写入 state.skills_metadata"]
    H --> I["每次调用模型前 wrap_model_call"]
    I --> J["将 Skill 列表注入 System Message"]
    J --> K{"模型判断 Skill 是否适用"}
    K -- 否 --> L["正常回答或调用其他工具"]
    K -- 是 --> M["调用 read_file 读取完整 SKILL.md"]
    M --> N["模型遵循 Skill 指令"]
    N --> O["读取辅助文件 / 调用工具 / 执行脚本"]
    O --> P["产生最终回答"]
```

