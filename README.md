# MaxKB Toolstore

MaxKB 工具商店 - 强大易用的开源企业级智能体平台工具集合

## 📖 项目简介

MaxKB Toolstore 是 MaxKB 智能体平台的官方工具商店，提供各类工具工具来扩展 MaxKB 的功能。通过这些工具，您可以轻松地为 MaxKB 添加联网搜索、数据库查询等能力。

## 🚀 现有工具

### 联网搜索类
- **秘塔AI搜索** - 强大的AI驱动搜索引擎，提供准确的联网搜索能力

### 数据库查询类  
- **MongoDB 查询** - 支持 MongoDB 4.x 以上版本的数据库查询操作

## 📁 项目结构

```
MaxKB-toolstore/
├── README.md             # 项目说明文档
├── tools/                # 工具目录
│   ├── data.yaml         # 工具商店配置
│   ├── logo.png          # 商店图标
│   ├── metaso/           # 秘塔AI搜索工具
│   │   ├── data.yaml     # 工具配置
│   │   ├── logo.png      # 工具图标
│   │   ├── README.md     # 工具说明
│   │   └── 1.0.0/        # 版本目录
│   └── mongo/            # MongoDB查询工具
│       ├── data.yaml     # 工具配置
│       ├── logo.png      # 工具图标
│       ├── README.md     # 工具说明
│       └── 1.0.0/        # 版本目录
```

## 🔧 如何使用

1. 在 MaxKB 平台中访问工具商店
2. 浏览并选择所需的工具
3. 点击安装并按照说明进行配置
4. 开始使用扩展功能

## 🤝 贡献指南

如果您想为 MaxKB Toolstore 贡献新的工具，请参考：
[如何提交自己想要的工具](./如何提交工具.md)

### 工具开发规范

- 每个工具需要包含 `data.yaml` 配置文件
- 提供清晰的工具说明文档
- 包含适当的图标和版本管理
- 遵循 MaxKB 平台的开发规范


## 📞 联系我们

- 项目地址：https://github.com/1panel-dev/MaxKB-toolstore
- 问题反馈：请在 GitHub Issues 中提交
- 文档支持：参考 MaxKB 官方文档

