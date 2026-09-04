import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
data_path = BASE_DIR.parent / "knowledge_base"
faiss_index_path = BASE_DIR.parent / "faiss_index"

print("Loading text files...")

text_loader = DirectoryLoader(
    str(data_path),
    glob="**/*.txt",
    recursive=True,
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
)
text_doc = text_loader.load()

pdf_loader = DirectoryLoader(
    str(data_path),
    glob="**/*.pdf",
    recursive=True,
    loader_cls=PyPDFLoader,
)
pdf_doc = pdf_loader.load()

docs = text_doc + pdf_doc
print(f"Loaded {len(text_doc)} text docs and {len(pdf_doc)} pdf docs.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""],
)


def cpp_chunks(source: str, chunk_size: int = 1000) -> list[str]:
    try:
        from tree_sitter_languages import get_parser
    except ImportError:
        return RecursiveCharacterTextSplitter.from_language(
            Language.CPP, chunk_size=chunk_size, chunk_overlap=150
        ).split_text(source)

    parser = get_parser("cpp")
    tree = parser.parse(source.encode("utf-8"))
    fallback = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=0,
        separators=["\n\n", "\n", " ", ""],
    )
    symbol_types = {
        "class_specifier", "struct_specifier", "namespace_definition",
        "function_definition", "template_declaration", "enum_specifier",
    }

    def node_text(node):
        return source[node.start_byte:node.end_byte].strip()

    def walk(node, path=()):
        text = node_text(node)
        current = path
        if node.type in symbol_types:
            header = text.split("{", 1)[0].strip()
            if header:
                current = (*path, header[:240])
        children = [child for child in node.named_children if child.type != "comment"]
        if text and len(text) <= chunk_size and node.type in symbol_types:
            return [(current, text)]
        if not children:
            return [(current, chunk) for chunk in fallback.split_text(text)] if text else []
        chunks = []
        for child in children:
            chunks.extend(walk(child, current))
        return chunks

    chunks = []
    for path, text in walk(tree.root_node):
        context = " > ".join(path)
        chunks.append(f"// symbol: {context}\n{text}" if context else text)
    return chunks


split_docs = text_splitter.split_documents(docs)
print(f"Split into {len(split_docs)} chunks.")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = FAISS.from_documents(split_docs, embeddings)
db.save_local(str(faiss_index_path))

print(f"FAISS index created successfully at {faiss_index_path}")