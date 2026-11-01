![索引流水线：数据源到索引](https://resource.duyiedu.com/yuanjin/20261020133923153.png)

# Milvus环境搭建

https://milvus.io/docs/zh/quickstart.md

## 向量数据库

| 数据库        | 特点                             | 适用场景                                                     |
| ------------- | -------------------------------- | ------------------------------------------------------------ |
| Milvus        | 分布式<br />高性能<br />社区活跃 | PB级数据<br />大规模数据集群<br />检索已成为需要专门建设的核心基础设施； |
| FAISS         | 高性能<br />自建                 | TB级数据<br />性能极致追求<br />自行封装功能                 |
| Chroma        | 轻量级                           | GB级数据<br />快速原型<br />个人知识库                       |
| ElasticSearch | 全文检索<br />向量检索           | 已有ElasticSearch                                            |
| pgvector      | PostgreSQL插件                   | 已有postgresql数据库，且需要和业务数据一起检索               |
| ...           | ...                              | ...                                                          |

## Mivlus安装

1. 复制`docker-compose.yml`到你的工程
2. 运行命令`docker compose up -d`
   - `milvus`：接受请求、处理数据、构建索引、执行搜索
   - `milvus-etcd`：保存元数据
   - `milvus-minio`：保存持久化数据
3. 复制`README.md`到你的工程

## [可选]安装GUI管理工具

https://github.com/zilliztech/attu/releases
