# 官方资料核实

访问日期：2026-10-20。只使用官方文档支持数据库能力事实；本项目适配性与复杂度结论另列为推断。当前项目服务器目标仍为 MongoDB 7.0，读取 current 文档不意味着批准升级。

| 标识 | 官方资料 | 在本研究中的用途与限制 |
| --- | --- | --- |
| M1 | [MongoDB 7.0 数据建模](https://www.mongodb.com/docs/v7.0/data-modeling/) | 嵌套对象/数组与访问模式；灵活结构不取消业务校验 |
| M2 | [MongoDB 7.0 多键索引](https://www.mongodb.com/docs/v7.0/core/indexes/index-types/index-multikey/) | 数组可索引；复合索引不能任意组合两个独立数组字段 |
| M3 | [MongoDB 7.0 $all](https://www.mongodb.com/docs/v7.0/reference/operator/query/all/) / [$elemMatch](https://www.mongodb.com/docs/v7.0/reference/operator/query/elemmatch/) | 多标签与同元素条件，避免跨数组元素误匹配；空 all 不是无筛选 |
| M4 | [MongoDB 单文档原子性](https://www.mongodb.com/docs/v7.0/core/write-operations-atomicity/) | 带预期值的条件更新；多文档原子性不是自动获得 |
| M5 | [文档版本保留](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/document-versioning/) / [结构版本](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/schema-versioning/) | 版本模式是应用设计；历史不是 MongoDB 自动保存，混合结构会增加查询/索引负担 |
| M6 | [避免无界数组](https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/unbounded-arrays/) | 历史版本/无限收藏不能一股脑塞进同一个文档 |
| M7 | [MongoDB explain](https://www.mongodb.com/docs/manual/reference/explain-results/) | 执行计划与扫描量证据；不能由索引定义推断所有查询都命中 |
| M8 | [MongoDB 7.0 Change Streams](https://www.mongodb.com/docs/v7.0/changestreams/) | 部署前提；本项目普通 Compose 不能被假定具备流式变更能力 |
| S1 | [MySQL 8.4 JSON](https://dev.mysql.com/doc/refman/8.4/en/json.html) | 原生 JSON、嵌套访问、生成列及数组多值索引，纠正 SQL 无法处理文档的说法 |
| S2 | [MySQL 8.4 JSON_TABLE](https://dev.mysql.com/doc/refman/8.4/en/json-table-functions.html) | JSON 数组可展开为关系结果，是等价对照之一 |
| S3 | [MySQL 8.4 EXPLAIN](https://dev.mysql.com/doc/refman/8.4/en/explain.html) | SQL 对照执行计划/实际执行分析，不只测 MongoDB |
| S4 | [MySQL ngram 全文解析](https://dev.mysql.com/doc/refman/8.4/en/fulltext-search-ngram.html) | MySQL 具备中文全文检索方案，不能把中文搜索自动归为 MongoDB 优势 |
| N1 | [Neo4j 变长路径](https://neo4j.com/docs/cypher-manual/current/patterns/variable-length-paths/) | 图查询适配关系遍历；现有浅层标签关系未证明有此负载 |
| N2 | [Elasticsearch 高亮](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/highlighting) | 搜索专用能力；这是搜索引擎候选，是否满足课程 NoSQL 定义须另核实，不能顺手新增服务 |
| D1 | [Motor 生命周期](https://motor.readthedocs.io/en/stable/) / [迁移至 PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/) | 两份官方文档确认弃用日期为 2026-05-14，Motor 文档列关键修复至 2027-05-14；迁移文档也提醒特定负载可能变慢。现有 Motor 仍在代码里，新增实验核实 PyMongo Async 兼容性，不能把驱动差异算成数据库优势 |

不同数据库的行为以目标版本实际执行为准。避免使用仅 Atlas/云服务提供的能力为本地 Community 7.0 背书；本任务不要求 Atlas Search、分片或副本集。
