# 반도체 Infra AI Agent

Claude.AI와 같은 웹 기반 AI Agent로, 반도체 공정의 센서 데이터를 조회하고 시각화하는 서비스입니다.

## 주요 기능

- **AI 대화**: OpenAI 호환 API를 통한 자연어 대화
- **센서 데이터 조회**: 온도, 압력, 진공도, 가스 유량, RF Power 등
- **그래프 시각화**: MCP + ECharts를 이용한 실시간 차트 생성
- **대화 기록**: MySQL에 대화 히스토리 저장 및 컨텍스트 유지
- **사용자 인증**: JWT 기반 로그인/회원가입

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | React, Vite, TypeScript, Tailwind CSS, ECharts |
| Backend | FastAPI, SQLAlchemy, JWT |
| MCP Server | FastMCP |
| Database | MySQL (대화/사용자), PostgreSQL (센서 데이터) |

## 프로젝트 구조

```
infra-ai-agent/
├── frontend/          # React 프론트엔드
├── backend/           # FastAPI 백엔드
├── mcp-server/        # FastMCP 센서 데이터 서버
├── docker/            # Docker 설정
└── scripts/           # DB 초기화 스크립트
```

## 빠른 시작

### 1. 환경 변수 설정

```bash
# docker/.env 파일 생성
cp docker/.env.example docker/.env

# LLM API 키 설정 (필수)
# docker/.env 파일에서 LLM_API_KEY 수정
```

### 2. Docker Compose로 실행

```bash
cd docker

# 모든 서비스 시작
docker compose up -d

# 로그 확인
docker compose logs -f
```

### 3. 접속

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 개발 환경

### Backend

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 서버 실행
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### MCP Server

```bash
cd mcp-server

# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env

# 서버 실행
python -m src.server
```

## API 엔드포인트

### 인증

- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/refresh` - 토큰 갱신
- `GET /api/v1/auth/me` - 현재 사용자 조회

### 대화

- `GET /api/v1/conversations` - 대화 목록
- `GET /api/v1/conversations/{id}` - 대화 상세
- `POST /api/v1/conversations` - 새 대화 생성
- `DELETE /api/v1/conversations/{id}` - 대화 삭제

### 채팅

- `GET /api/v1/chat/stream` - SSE 스트리밍 채팅
- `POST /api/v1/chat/send` - 비스트리밍 채팅

## MCP 도구

| 도구 | 설명 |
|------|------|
| `get_sensor_data` | 센서 데이터 조회 |
| `get_sensor_statistics` | 센서 통계 (평균, 최소, 최대, 표준편차) |
| `list_equipment` | 장비 목록 조회 |
| `generate_sensor_chart` | 센서 그래프 생성 |

## 사용 예시

```
사용자: 온도 센서 그래프 보여줘
AI: [온도 센서 데이터를 조회하고 라인 차트를 생성합니다]

사용자: 최근 24시간 압력 통계 알려줘
AI: 최근 24시간 압력 데이터 통계입니다:
    - 평균: 498.52 mTorr
    - 최소: 489.12 mTorr
    - 최대: 509.87 mTorr
    ...
```

## 라이선스

MIT License
