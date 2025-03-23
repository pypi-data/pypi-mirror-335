from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import json
import sys
import socket
import time
import os
from contextlib import asynccontextmanager

# 패키지 구조에 맞게 import 경로 수정
from estimate_mcp_server.utils.firebase_client import initialize_firebase as init_firebase, get_document as get_estimate_data, update_document as update_estimate_data
from estimate_mcp_server.tools.estimate_tools import analyze_estimate
from estimate_mcp_server.tools.process_tools import analyze_processes
from estimate_mcp_server.tools.version_tools import get_versions, create_version, compare_versions

# 싱글톤 패턴을 위한 락 파일 경로
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.lock')

# 이미 실행 중인 서버가 있는지 확인
def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# 락 파일 확인
def check_lock_file() -> bool:
    if os.path.exists(LOCK_FILE):
        # 락 파일이 존재하면 프로세스가 실행 중인지 확인
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            # 프로세스가 실행 중인지 확인 (Windows)
            import ctypes
            kernel32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x00100000
            process = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
            if process:
                kernel32.CloseHandle(process)
                return True
            else:
                # 프로세스가 종료되었으므로 락 파일 제거
                os.remove(LOCK_FILE)
                return False
        except Exception:
            # 오류 발생 시 락 파일 제거
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
            return False
    return False

# 락 파일 생성
def create_lock_file():
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 시 실행되는 이벤트"""
    try:
        init_firebase()
        print(json.dumps({"status": "success", "message": "Firebase initialized successfully"}), file=sys.stderr)
    except Exception as e:
        error_msg = {"status": "error", "message": f"Firebase initialization error: {str(e)}"}
        print(json.dumps(error_msg), file=sys.stderr)
        raise e
    yield

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EstimateRequest(BaseModel):
    address: str
    
class VersionRequest(BaseModel):
    address: str
    version_name: str
    data: Dict[str, Any]

class CompareRequest(BaseModel):
    address: str
    version1: str
    version2: str

@app.get("/")
async def root():
    """루트 경로"""
    return {
        "message": "견적 분석 서버가 실행 중입니다",
        "endpoints": {
            "GET /": "이 메시지를 표시합니다",
            "GET /status": "서버 상태를 확인합니다",
            "GET /health": "서버 상태를 확인합니다",
            "POST /analyze": "견적서를 분석합니다",
            "POST /versions": "새 버전을 생성합니다",
            "POST /compare": "두 버전을 비교합니다"
        }
    }

@app.get("/status")
async def get_status():
    """서버 상태 확인"""
    return {"status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_estimate_data(request: EstimateRequest):
    """견적서 분석"""
    try:
        # 견적서 데이터 조회
        estimate_data = get_estimate_data(request.address)
        if not estimate_data:
            raise HTTPException(status_code=404, detail="견적서를 찾을 수 없습니다.")

        # 견적서 분석
        analysis_results = analyze_estimate(estimate_data)
        if "error" in analysis_results:
            raise HTTPException(status_code=500, detail=analysis_results["error"])
        
        # 공정 분석
        process_analysis = analyze_processes(estimate_data)
        if "error" in process_analysis:
            raise HTTPException(status_code=500, detail=process_analysis["error"])
        
        # 버전 정보 조회
        versions = get_versions(request.address)

        # 분석 결과 종합
        response = {
            "estimate_analysis": analysis_results,
            "process_analysis": process_analysis,
            "versions": versions,
            "suggestions": [
                *analysis_results.get("suggestions", []),
                *process_analysis.get("suggestions", []),
                "공정별 단가를 최적화하여 원가를 절감할 수 있습니다.",
                "자주 사용되는 항목들을 템플릿으로 저장하면 효율적입니다.",
                "공정 순서를 조정하여 작업 효율을 높일 수 있습니다."
            ]
        }

        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/versions")
async def create_new_version(request: VersionRequest):
    """새 버전 생성"""
    try:
        version_data = {
            "name": request.version_name,
            "total_amount": request.data.get("total_amount", 0)
        }
        success = create_version(request.address, version_data)
        if not success:
            raise HTTPException(status_code=500, detail="버전 생성에 실패했습니다")
        return {"status": "success", "message": "버전이 생성되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
async def compare_two_versions(request: CompareRequest):
    """버전 비교"""
    try:
        comparison = compare_versions(request.address, request.version1, request.version2)
        if "error" in comparison:
            raise HTTPException(status_code=500, detail=comparison["error"])
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start():
    """
    콘솔 스크립트 진입점 함수
    """
    port = 8001
    
    # 포트가 이미 사용 중인지 확인
    if is_port_in_use(port):
        print(json.dumps({
            "status": "info", 
            "message": f"서버가 이미 실행 중입니다: http://localhost:{port}"
        }), file=sys.stderr)
        sys.exit(0)
    
    # 다른 프로세스가 이미 실행 중인지 락 파일로 확인
    if check_lock_file():
        print(json.dumps({
            "status": "info", 
            "message": "서버가 이미 다른 프로세스에서 실행 중입니다"
        }), file=sys.stderr)
        sys.exit(0)
    
    # 락 파일 생성
    create_lock_file()
    
    try:
        # 종료 시 락 파일 삭제를 위한 이벤트 핸들러 등록
        import atexit
        atexit.register(lambda: os.path.exists(LOCK_FILE) and os.remove(LOCK_FILE))
        
        # 서버 실행
        print(json.dumps({
            "status": "info", 
            "message": f"서버를 시작합니다: http://0.0.0.0:{port}"
        }), file=sys.stderr)
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        # 오류 발생 시 락 파일 삭제
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        
        # 오류 출력
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        raise

if __name__ == "__main__":
    start() 