"""按流程顺序排列的单文档节点；逐个填写函数体即可。"""

from typing import Literal

from deal_pilot.graphs.feishu_doc_index.document_index.state import (
    DocumentIndexState,
)
from deal_pilot.feishu.api import DocxAPI
from deal_pilot.rag.loader.feishu_doc.feishu_doc_loader import load_feishu_doc_structre
from deal_pilot.rag.store.feishu_doc.get_store import get_store, COLLECTION_NAME
from deal_pilot.rag.structure.feishu_doc.block_node import BlockNode
from deal_pilot.rag.structure.feishu_doc.tree_builder import build_tree
from deal_pilot.rag.splitter.feishu_doc.feishu_doc_splitter import split_feishu_doc


async def fetch_document_version(state: DocumentIndexState) -> DocumentIndexState:
    """根据 node 获取文档元信息，返回 {"document": DocxDocument}。"""
    raise NotImplementedError()


async def compare_versions(state: DocumentIndexState) -> DocumentIndexState:
    """返回 indexed_revision_id（int | None）和 needs_index（bool）。"""
    raise NotImplementedError()


def route_by_version(
    state: DocumentIndexState,
) -> Literal["build_metadata", "finish_document"]:
    """根据版本对比节点写入的 needs_index 选择是否继续索引。"""
    raise NotImplementedError()


async def build_metadata(state: DocumentIndexState) -> DocumentIndexState:
    """根据 node 和 document 构建来源信息，返回 {"metadata": 字典}。"""
    raise NotImplementedError()


async def fetch_document_content(state: DocumentIndexState) -> DocumentIndexState:
    """按 document.revision_id 读取正文，返回 {"blocks": list[DocxBlock]}。"""
    raise NotImplementedError()


async def structure_document(state: DocumentIndexState) -> DocumentIndexState:
    """将 blocks 结构化，返回 {"root": 不含循环引用的树形字典}。"""
    raise NotImplementedError()


async def load_documents(state: DocumentIndexState) -> DocumentIndexState:
    """将 root 和 metadata 传给 Loader，返回 {"documents": list[Document]}。"""
    raise NotImplementedError()


async def split_documents(state: DocumentIndexState) -> DocumentIndexState:
    """将 documents 传给 Splitter，返回 {"chunks": list[Document]}。"""
    raise NotImplementedError()


async def create_new_index(state: DocumentIndexState) -> DocumentIndexState:
    """写入本次版本的全部 chunks，成功后返回 {"written_chunk_count": int}。"""
    raise NotImplementedError()


async def delete_old_index(state: DocumentIndexState) -> DocumentIndexState:
    """删除当前文档的旧版本索引，成功后返回空字典。"""
    raise NotImplementedError()


async def finish_document(state: DocumentIndexState) -> DocumentIndexState:
    """返回 {"status": "success"} 或 {"status": "skipped"}。"""
    raise NotImplementedError()
