"""Módulo para upload, download e busca de documentos PDF"""

import os
from datetime import datetime

from bson.objectid import ObjectId
from docling.document_converter import DocumentConverter
from fastapi import File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

from src.mongo.client import MongoDBClient
from src.elastic.client import ElasticsearchConnection

document_router = APIRouter()

DB_NAME = "healthcom"
ES_HOST = "http://localhost:9200"

mongo_client = MongoDBClient()

es = ElasticsearchConnection().es

converter = DocumentConverter()


@document_router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    category: str = Form(...),
    access_level: int = Form(...),
    user_id: str = Form(...),
):
    fs = mongo_client.fs

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas PDFs são permitidos")

    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(temp_path, "wb") as temp_file:
        temp_file.write(await file.read())

    try:
        result = converter.convert(temp_path)
        extracted_text = result.document.export_to_markdown()
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
                    "data_upload": datetime.utcnow(),
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
                "content": extracted_text,
                "category": category,
                "access_level": access_level,
                "uploaded_by": user_id,
                "data_upload": datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        fs.delete(file_id)
        raise HTTPException(
            status_code=500, detail=f"Erro ao indexar no Elasticsearch: {str(e)}"
        )

    return {"message": "PDF salvo e indexado com sucesso", "file_id": str(file_id)}


@document_router.get("/download/{file_id}")
async def download_pdf(
    file_id: str, user_access_level: int
):
    try:
        fs = mongo_client.fs

        file = fs.find_one({"_id": ObjectId(file_id)})
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
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
    query: str, category: str = None, user_access_level: int = 3
):
    es_query = {
        "query": {
            "bool": {
                "must": [{"match": {"content": query}}],
                "filter": [{"range": {"access_level": {"lte": user_access_level}}}],
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
                "id": hit["_id"], "content": hit["_source"]["content"]
            }
            for hit in hits
        ]
        return {"result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(document_router, host="0.0.0.0", port=8000)
