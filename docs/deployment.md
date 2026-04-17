# 배포 / 자동화 가이드

## 1. MCP 클라이언트 등록

이 프로젝트는 [uv](https://docs.astral.sh/uv/) 를 통해 의존성과 실행을 자동 관리합니다.

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) 또는
`%APPDATA%\Claude\claude_desktop_config.json` (Windows) 에 다음을 추가:

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

등록 확인:

```bash
claude mcp list
```

---

## 2. 매일 아침 자동 리포트 (선택)

`watch_complexes` 결과를 매일 정해진 시간에 자동 수신하고 싶다면 다음 두 가지 방법 중 선택할 수 있습니다.

### 방법 A: crontab + 외부 알림

`watch_complexes` 를 직접 호출하는 헬퍼 스크립트(`scripts/daily_report.py`)를 만들고
원하는 채널(Discord 웹훅, Slack 웹훅, 이메일 등)로 결과를 전송한 뒤 crontab 에 등록합니다.

```bash
# crontab -e
0 8 * * * cd /ABSOLUTE/PATH/TO/naver-land-mcp && uv run scripts/daily_report.py
```

> Discord 웹훅을 사용하려면 [Discord Webhook 생성 가이드](https://support.discord.com/hc/en-us/articles/228383668) 를
> 참고하세요. 발급받은 webhook URL은 환경변수로 보관하고 절대 커밋하지 마세요.

### 방법 B: MCP 클라이언트의 스케줄링 기능

Claude Code 의 cron / 자동화 기능 또는 호스팅형 MCP 매니저가 있다면 그쪽의 스케줄러로
직접 `watch_complexes` 를 호출할 수도 있습니다. 자세한 사용법은 각 도구의 공식 문서를 참고하세요.

---

## 3. Rate Limiting 주의

- `config.py` 의 `REQUEST_DELAY_SEC`(기본 0.5초)를 임의로 줄이지 마세요.
- 자동화 호출은 **하루 1~2회** 정도가 적절합니다.
- 429 응답이 반복되면 잠시 호출을 중단하고 헤더를 점검하세요.
