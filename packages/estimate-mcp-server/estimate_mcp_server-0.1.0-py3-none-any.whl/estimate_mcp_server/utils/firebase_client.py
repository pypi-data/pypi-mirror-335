import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any, Optional

# Firebase 클라이언트 인스턴스
db: Optional[firestore.Client] = None

def initialize_firebase() -> None:
    """
    Firebase를 초기화하고 Firestore 클라이언트를 설정합니다.
    """
    global db
    
    if not firebase_admin._apps:
        # 서비스 계정 키 파일 경로 (패키지 구조에 맞게 업데이트)
        cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'firebase_config.json')
        
        # Firebase 초기화
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    # Firestore 클라이언트 설정
    db = firestore.client()

def get_firestore() -> firestore.Client:
    """
    Firestore 클라이언트를 반환합니다.
    """
    if db is None:
        initialize_firebase()
    return db

def get_document(collection: str, doc_id: str) -> Dict[str, Any]:
    """
    Firestore에서 문서를 조회합니다.
    """
    doc_ref = get_firestore().collection(collection).document(doc_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise ValueError(f"Document {doc_id} not found in collection {collection}")
    
    return doc.to_dict()

def update_document(collection: str, doc_id: str, data: Dict[str, Any]) -> None:
    """
    Firestore 문서를 업데이트합니다.
    """
    doc_ref = get_firestore().collection(collection).document(doc_id)
    doc_ref.update(data)

def create_document(collection: str, doc_id: str, data: Dict[str, Any]) -> None:
    """
    Firestore에 새 문서를 생성합니다.
    """
    doc_ref = get_firestore().collection(collection).document(doc_id)
    doc_ref.set(data) 