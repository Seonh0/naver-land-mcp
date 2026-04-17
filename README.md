# naver-land-mcp

네이버 부동산 데이터를 활용해 전국 아파트 매물·시세·실거래가를 조회하는 MCP(Model Context Protocol) 서버.
Claude Desktop / Claude Code 등 MCP 클라이언트에서 자연어로 부동산 정보를 검색할 수 있습니다.

> *An MCP server for searching Korean apartment listings, market prices, and recent transactions via Naver Real Estate.*

---

## ⚠️ 사전 고지

- 본 서버는 네이버 부동산의 **비공식 내부 API**를 사용합니다. 네이버가 공식 제공·보장하는 인터페이스가 아니며, 응답 구조·차단 정책이 사전 통보 없이 변경될 수 있습니다.
- 비공식 API 사용은 네이버 이용약관과 충돌할 가능성이 있으니, 네이버가 차단·중단·시정을 요청할 경우 사용을 중단해주세요.
- 동일한 사유 또는 기타 사유로 **본 저장소 자체도 예고 없이 비공개 전환되거나 삭제될 수 있습니다.**
- 상업적 이용은 이용약관·저작권·부정경쟁방지법 위반 위험이 있어 **권장하지 않습니다**. 개인 학습·조회 용도로 사용해주세요.
- API 호출은 **요청 간 최소 0.5초 딜레이**를 두고 수행합니다 (`config.REQUEST_DELAY_SEC`). 과도한 호출은 IP 차단의 원인이 되므로 줄이지 마세요.
- 코드는 MIT 라이선스로 자유롭게 사용할 수 있으나, 사용에 따른 법적·기술적 책임은 사용자 본인에게 있습니다.

---

## 🛠 제공 도구 (6개)

| 도구 | 설명 |
|---|---|
| `search_apartments` | 동/구/군 + 가격 범위로 매물 검색 (매매/전세/월세) |
| `watch_complexes` | 관심 단지 매물 + 시세 + 실거래가를 한 번에 조회, 이전 스냅샷 대비 변동 감지 |
| `get_complex_info` | 단지 상세 정보 (세대수, 준공일, 평형, 좌표 등) |
| `get_complex_price_info` | 단지 평형별 시세(네이버) + 최근 실거래가 |
| `resolve_district` | 지역명 → 네이버 cortarNo 조회 |
| `list_districts` | 전국 시/도 17개 목록 |

---

## 📦 설치

[uv](https://docs.astral.sh/uv/) 가 설치돼 있어야 합니다.

```bash
# uv 가 없다면
curl -LsSf https://astral.sh/uv/install.sh | sh
```

저장소 클론:

```bash
git clone https://github.com/<YOUR_USERNAME>/naver-land-mcp.git
cd naver-land-mcp
```

의존성은 `uv run` 이 자동으로 설치하므로 별도 설치 단계가 없습니다.

---

## 🔌 MCP 클라이언트 등록

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) 또는
`%APPDATA%\Claude\claude_desktop_config.json` (Windows) 에 추가:

```json
{
  "mcpServers": {
    "naver-land": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/naver-land-mcp",
        "server.py"
      ]
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add-json --scope user naver-land \
  '{"command":"uv","args":["run","--directory","/ABSOLUTE/PATH/TO/naver-land-mcp","server.py"]}'
```

> `/ABSOLUTE/PATH/TO/naver-land-mcp` 는 클론한 저장소의 절대경로로 바꿔주세요.

---

## 💬 사용 예시

MCP 클라이언트에서 자연어로 호출하면 됩니다.

```
강남구 6억~7.9억 아파트 매매 매물 찾아줘
관평동 매매 매물 정리해줘
래미안강남 단지 정보 알려줘
가천대역두산위브의 평형별 시세와 최근 실거래가 보여줘
```

---

## 📁 프로젝트 구조

```
naver-land-mcp/
├── server.py        # MCP 서버 엔트리 (FastMCP 도구 6개)
├── naver_land.py    # 네이버 부동산 API 클라이언트
├── filter.py        # 매물 필터링 + 정렬
├── report.py        # 마크다운 리포트 포맷터
├── snapshot.py      # 매물 변동 감지 (신규/삭제/가격변동)
├── config.py        # 설정 (헤더, 가격 기본값, 규제지역 LTV)
├── pyproject.toml
├── docs/            # 상세 문서 (API 레퍼런스, 도구 스펙 등)
└── README.md
```

---

## 📚 문서

- [`docs/api-reference.md`](docs/api-reference.md) — 네이버 부동산 API 엔드포인트와 헤더 정보
- [`docs/mcp-tools.md`](docs/mcp-tools.md) — MCP 도구 상세 스펙
- [`docs/module-guide.md`](docs/module-guide.md) — 모듈별 구현 가이드
- [`docs/testing.md`](docs/testing.md) — 테스트 체크리스트
- [`docs/deployment.md`](docs/deployment.md) — 배포 / 자동화 가이드

---

## 📄 라이선스

MIT License. [`LICENSE`](LICENSE) 참고.
