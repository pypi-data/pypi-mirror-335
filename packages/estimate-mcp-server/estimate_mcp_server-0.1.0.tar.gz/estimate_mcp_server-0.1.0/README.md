# 견적서 MCP 서버

견적서 분석 및 관리를 위한 MCP (Multi-Model Communication Protocol) 서버입니다.

## 기능

- 견적서 분석 및 통계
- 공정별 비용 분석
- 버전 관리 및 비교
- Firebase 연동

## 설치

```bash
pip install estimate-mcp-server
```

## 사용 방법

### 직접 실행

```bash
# 명령행으로 실행
estimate-mcp-server

# 파이썬 코드로 실행
from estimate_mcp_server.main import start
start()
```

### Claude Desktop과 함께 사용

이 서버는 Claude Desktop과 함께 사용하여 견적서 분석 기능을 제공합니다.

Claude Desktop 설정 파일(`claude_desktop_config.json`)에 다음 설정을 추가합니다:

```json
{
  "mcpServers": {
    "estimate": {
      "command": "estimate-mcp-server"
    }
  }
}
```

## 개발자를 위한 정보

### 환경 설정

개발 환경을 설정하려면 다음 명령을 실행하세요:

```bash
# 저장소 복제
git clone https://github.com/yourusername/estimate-mcp-server.git
cd estimate-mcp-server

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -e .
```

### 구조

```
estimate_mcp_server/
  ├── __init__.py
  ├── main.py            # 메인 앱 및 API 정의
  ├── utils/             # 유틸리티 모듈
  │   ├── __init__.py
  │   └── firebase_client.py
  └── tools/             # 견적서 분석 도구
      ├── __init__.py
      ├── estimate_tools.py
      ├── process_tools.py
      └── version_tools.py
```

## 라이선스

MIT 라이선스 