"""Módulo para visualização de documentos"""

import os
import requests
import streamlit as st

BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:5000")


def get_all_documents():
    """Busca todos os documentos do Elasticsearch com acesso do usuário"""
    try:
        access_level = st.session_state.get("access_level", 0)
        response = requests.get(
            f"{BASE_API_URL}/api/v1/document/list",
            params={"access_level": access_level}
        )
        if response.status_code == 200:
            return response.json().get("documents", [])
        return []
    except Exception as e:
        st.error(f"Erro ao buscar documentos: {str(e)}")
        return []


def get_document_content(doc_id: str):
    """Busca o conteúdo markdown de um documento específico"""
    try:
        response = requests.get(
            f"{BASE_API_URL}/api/v1/document/{doc_id}/markdown"
        )
        if response.status_code == 200:
            return response.json().get("content", "")
        return None
    except Exception as e:
        st.error(f"Erro ao buscar conteúdo: {str(e)}")
        return None


def view_documents():
    """Página principal de visualização de documentos"""
    st.subheader("Documentos Extraídos")
    
    # Buscar documentos
    documents = get_all_documents()
    
    if not documents:
        st.info("Nenhum documento disponível para visualização.")
        return
    
    # Lista de documentos
    st.write("### Lista de Documentos")
    
    # Initializar session state para selecção de documento
    if "selected_doc" not in st.session_state:
        st.session_state.selected_doc = None
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = None
    
    # Se tem um documento pré-selecionado, mostrar ele
    if st.session_state.selected_doc:
        # Procurar o documento na lista
        selected_doc = None
        for doc in documents:
            if doc.get("id") == st.session_state.selected_doc:
                selected_doc = doc
                break
        
        if selected_doc:
            st.write(f"**Documento:** {selected_doc.get('filename', 'N/A')}")
            st.write(f"**Categoria:** {selected_doc.get('category', 'N/A')}")
            st.write(f"**Enviado por:** {selected_doc.get('uploaded_by', 'N/A')}")
            st.write(f"**Data:** {selected_doc.get('data_upload', 'N/A')}")
            
            if st.button("← Voltar à lista"):
                st.session_state.selected_doc = None
                st.session_state.view_mode = None
                st.rerun()
            
            st.divider()
            
            # Opções de visualização
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 Ver Markdown", use_container_width=True):
                    st.session_state.view_mode = "markdown"
            with col2:
                if st.button("📥 Baixar PDF", use_container_width=True):
                    st.session_state.view_mode = "pdf"
            
            st.divider()
            
            # Exibir conteúdo baseado no modo selecionado
            if st.session_state.view_mode == "markdown":
                st.write("### Visualização em Markdown")
                content = get_document_content(st.session_state.selected_doc)
                if content:
                    # Exibir markdown renderizado
                    st.markdown(content)
                    
                    # Botão de copiar
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("📋 Copiar", use_container_width=True):
                            st.success("Texto copiado para a área de transferência!")
                else:
                    st.error("Não foi possível carregar o conteúdo.")
            
            elif st.session_state.view_mode == "pdf":
                st.write("### Download PDF")
                st.info("Clique no botão abaixo para baixar o arquivo PDF original.")
                
                if st.button("📥 Baixar PDF", use_container_width=True):
                    try:
                        response = requests.get(
                            f"{BASE_API_URL}/api/v1/document/download/{st.session_state.selected_doc}",
                            params={"user_access_level": st.session_state.get("access_level", 0)}
                        )
                        if response.status_code == 200:
                            st.download_button(
                                label="Clique aqui para baixar",
                                data=response.content,
                                file_name=selected_doc.get('filename', 'documento.pdf'),
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.error("Erro ao baixar o arquivo.")
                    except Exception as e:
                        st.error(f"Erro ao baixar PDF: {str(e)}")
            return
    
    # Exibir lista de documentos como selectbox
    doc_names = [f"{doc['filename']} ({doc['category']})" for doc in documents]
    doc_ids = [doc['id'] for doc in documents]
    
    selected_idx = st.selectbox(
        "Selecione um documento:",
        range(len(doc_names)),
        format_func=lambda i: doc_names[i],
        key="doc_selector"
    )
    
    if selected_idx is not None:
        selected_doc_id = doc_ids[selected_idx]
        selected_doc = documents[selected_idx]
        
        st.write(f"**Categoria:** {selected_doc.get('category', 'N/A')}")
        st.write(f"**Enviado por:** {selected_doc.get('uploaded_by', 'N/A')}")
        st.write(f"**Data:** {selected_doc.get('data_upload', 'N/A')}")
        
        # Opções de visualização
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Ver Markdown", use_container_width=True):
                st.session_state.view_mode = "markdown"
        with col2:
            if st.button("📥 Baixar PDF", use_container_width=True):
                st.session_state.view_mode = "pdf"
        
        st.divider()
        
        # Exibir conteúdo baseado no modo selecionado
        if st.session_state.view_mode == "markdown":
            st.write("### Visualização em Markdown")
            content = get_document_content(selected_doc_id)
            if content:
                # Exibir markdown renderizado
                st.markdown(content)
                
                # Botão de copiar
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("📋 Copiar", use_container_width=True):
                        st.success("Texto copiado para a área de transferência!")
            else:
                st.error("Não foi possível carregar o conteúdo.")
        
        elif st.session_state.view_mode == "pdf":
            st.write("### Download PDF")
            st.info("Clique no botão abaixo para baixar o arquivo PDF original.")
            
            if st.button("📥 Baixar PDF", use_container_width=True):
                try:
                    response = requests.get(
                        f"{BASE_API_URL}/api/v1/document/download/{selected_doc_id}",
                        params={"user_access_level": st.session_state.get("access_level", 0)}
                    )
                    if response.status_code == 200:
                        st.download_button(
                            label="Clique aqui para baixar",
                            data=response.content,
                            file_name=selected_doc['filename'],
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("Erro ao baixar o arquivo.")
                except Exception as e:
                    st.error(f"Erro ao baixar PDF: {str(e)}")


if __name__ == "__main__":
    view_documents()
