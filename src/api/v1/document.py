"""Módulo para upload, download e busca de documentos PDF"""

import os
from datetime import datetime

from bson.objectid import ObjectId
from fastapi import File, Form, HTTPException, UploadFile, Query
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from pymupdf4llm import to_markdown

from src.elastic.client import ElasticsearchConnection
from src.mongo.client import MongoDBClient

document_router = APIRouter()

DB_NAME = "healthcom"
ES_HOST = "http://localhost:9200"

mongo_client = MongoDBClient()

es = ElasticsearchConnection().es


@document_router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    category: str = Form(...),
    access_level: int = Form(...),
    user_id: str = Form(...),
):
    fs = mongo_client.fs

    if not file.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas PDFs são permitidos")

    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(temp_path, "wb") as temp_file:
        temp_file.write(await file.read())

    try:
        result = to_markdown(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

    try:
        with open(temp_path, "rb") as file_stream:
            file_id = fs.put(
                file_stream,
                filename=file.filename,
                metadata={
                    "category": category,
                    "access_level": access_level,
                    "uploaded_by": user_id,
                    "data_upload": datetime.now(),
                },
            )
    finally:
        os.remove(temp_path)

    try:
        es.index(
            index="healthcom_docs",
            id=str(file_id),
            body={
                "filename": file.filename,
                "content": result,
                "category": category,
                "access_level": access_level,
                "uploaded_by": user_id,
                "data_upload": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        fs.delete(file_id)
        raise HTTPException(
            status_code=500, detail=f"Erro ao indexar no Elasticsearch: {str(e)}"
        )

    return {"message": "PDF salvo e indexado com sucesso", "file_id": str(file_id)}


@document_router.get("/download/{file_id}")
async def download_pdf(file_id: str, user_access_level: int):
    try:
        fs = mongo_client.fs

        file = fs.find_one({"_id": ObjectId(file_id)})
        if not file or not file.metadata:
            raise HTTPException(
                status_code=404, detail="Arquivo não encontrado ou inválido"
            )
        if file.metadata["access_level"] > user_access_level:
            raise HTTPException(status_code=403, detail="Acesso negado")

        return StreamingResponse(
            file,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={file.filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar PDF: {str(e)}")


@document_router.get("/search")
async def search_documents(
    query: str = Query(...),
    category: str | None = Query(None),
    access_level: int = Query(0)
):
    es_query = {
        "query": {
            "bool": {
                "must": [{"match": {"content": query}}],
                "filter": [{"range": {"access_level": {"lte": access_level}}}],
            }
        }
    }
    if category:
        es_query["query"]["bool"]["filter"].append({"term": {"category": category}})

    try:
        result = es.search(index="healthcom_docs", body=es_query)
        hits = result["hits"]["hits"]
        response = [
            {
                "id": hit["_id"],
                "filename": hit["_source"].get("filename", "Sem nome"),
                "content": hit["_source"]["content"],
                "category": hit["_source"].get("category", "N/A"),
                "uploaded_by": hit["_source"].get("uploaded_by", "N/A")
            }
            for hit in hits
        ]
        return {"result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


@document_router.get("/list")
async def list_documents(access_level: int = Query(0)):
    """Lista todos os documentos que o usuário tem acesso"""
    try:
        es_query = {
            "query": {
                "range": {
                    "access_level": {"lte": access_level}
                }
            },
            "size": 1000
        }
        result = es.search(index="healthcom_docs", body=es_query)
        hits = result["hits"]["hits"]
        documents = [
            {
                "id": hit["_id"],
                "filename": hit["_source"].get("filename", ""),
                "content": hit["_source"].get("content", ""),
                "category": hit["_source"].get("category", ""),
                "access_level": hit["_source"].get("access_level", 0),
                "uploaded_by": hit["_source"].get("uploaded_by", ""),
                "data_upload": hit["_source"].get("data_upload", ""),
            }
            for hit in hits
        ]
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")


@document_router.get("/{doc_id}/markdown")
async def get_document_markdown(doc_id: str):
    """Retorna o conteúdo markdown de um documento"""
    try:
        result = es.get(index="healthcom_docs", id=doc_id)
        if not result:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        return {
            "content": result["_source"].get("content", ""),
            "filename": result["_source"].get("filename", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar markdown: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(document_router, host="0.0.0.0", port=8000)
