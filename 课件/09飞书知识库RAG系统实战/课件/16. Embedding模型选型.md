# Embedding模型选型

以下为常见系列的代表型号，规格核对日期：2026-10-19。点击模型名称可查看官方资料；表格不代表效果排名。

| 模型 | 参数量 | 上下文窗口 | 多模态支持 | 向量维度 | 语言支持 |
| ---- | ------ | ---------- | ---------- | -------- | -------- |
| [Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | 0.6B | 32K tokens | 否，仅文本 | 最大 1024，可缩减 | 100+ 种，含中文、英文 |
| [Qwen3-Embedding-4B](https://huggingface.co/Qwen/Qwen3-Embedding-4B) | 4B | 32K tokens | 否，仅文本 | 最大 2560，可缩减 | 100+ 种，含中文、英文 |
| [Qwen3-Embedding-8B](https://huggingface.co/Qwen/Qwen3-Embedding-8B) | 8B | 32K tokens | 否，仅文本 | 最大 4096，可缩减 | 100+ 种，含中文、英文 |
| [BGE-M3](https://huggingface.co/BAAI/bge-m3) | 约 0.57B | 8192 tokens | 否，仅文本 | 1024 | 100+ 种，含中文、英文 |
| [multilingual-e5-large](https://huggingface.co/intfloat/multilingual-e5-large) | 约 0.56B | 512 tokens | 否，仅文本 | 1024 | 100 种，含中文、英文 |
| [text-embedding-3-small](https://developers.openai.com/api/docs/models/text-embedding-3-small) | 未公开 | 8192 tokens | 否，仅文本 | 默认 1536，可缩减 | 多语言，含中文、英文 |
| [text-embedding-3-large](https://developers.openai.com/api/docs/models/text-embedding-3-large) | 未公开 | 8192 tokens | 否，仅文本 | 默认 3072，可缩减 | 多语言，含中文、英文 |
| [voyage-4](https://docs.voyageai.com/docs/embeddings) | 未公开 | 32,000 tokens | 否，仅文本 | 256 / 512 / 1024（默认）/ 2048 | 多语言 |
| [Cohere embed-v4.0](https://docs.cohere.com/v2/docs/cohere-embed) | 未公开 | 128K tokens | 是，文本、图片及图文混合 | 256 / 512 / 1024 / 1536（默认） | 100+ 种，含中文、英文 |
| [Qwen3-VL-Embedding-2B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) | 2B | 32K tokens | 是，文本、图片、视频及混合输入 | 最大 2048，可缩减 | 30+ 种，含中文、英文 |
| [Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B) | 8B | 32K tokens | 是，文本、图片、视频及混合输入 | 最大 4096，可缩减 | 30+ 种，含中文、英文 |

## 选型维度

**延迟**：越低越好

**成本**：越低越好

**检索质量**：越高越好

**多模态支持**：结合索引管线考量



**最佳实践**

完成RAG系统开发后，使用少量数据结合评估数据集，切换不同的模型验证检索质量、延迟、成本，找到平衡点
