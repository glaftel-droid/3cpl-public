# 3냉연 근무·수리 일정 — GitHub Pages

정적 공개 화면입니다. **교대근무표, 3CPL 근무 예외, 공장 수리일정만** 싣고 연락처는 가져오지 않습니다.

- `index.html`: 표시 화면과 근무주기 계산
- `data.json`: 마지막 자료 스냅샷
- `scripts/refresh_snapshot.py`: CT103 읽기 API에서 일정만 읽어 스냅샷 생성
- `.github/workflows/refresh-snapshot.yml`: 매일 09:20 KST에 스냅샷을 갱신하고 변경분을 저장소에 반영
- 화면을 열어 둔 상태에서는 15분마다 스냅샷을 다시 확인

GitHub 자동 일정은 지정 시각보다 늦게 시작될 수 있습니다. 자료가 바뀌지 않아도 갱신 시각은 매일 새로 기록됩니다.

## 올리는 방법

1. GitHub에서 공개 저장소를 하나 만듭니다 (예: `3cpl-public`). 이 사이트와 `data.json`은 공개됩니다.
2. 이 묶음의 **내용물 전체**를 저장소 최상위(root)에 올립니다. `.github/workflows/refresh-snapshot.yml`과 `scripts/refresh_snapshot.py`의 폴더 구조를 유지하세요. GitHub Desktop으로 폴더째 올리는 방법이 가장 간단합니다.
3. 저장소 **Settings → Pages → Build and deployment**에서 `Deploy from a branch`를 선택하고, 기본 브랜치(보통 `main`)와 `/(root)`를 지정합니다.
4. **Actions** 탭에서 `Refresh 3냉연 snapshot`을 한 번 실행해 결과가 성공하는지 확인합니다. 그 뒤 매일 자동 실행됩니다.
5. 주소는 `https://<GitHub 사용자명>.github.io/<저장소명>/` 형식입니다.

## 주의

- GitHub Pages는 PHP를 실행하지 않습니다. 이 묶음은 별도 HTML/CSS/JavaScript와 정적 JSON으로 변환한 것입니다.
- 수리일정/3CPL 예외 자료는 매일 GitHub Actions 서버가 CT103의 공개 읽기 API에서 가져옵니다. GitHub Actions가 외부에서 `yuharui.duckdns.org:888`에 연결할 수 있어야 합니다.
- API 연결이 실패하면 갱신 작업은 실패 처리되고, 기존 `data.json`은 덮어쓰지 않습니다. Actions 탭의 로그에서 원인을 확인할 수 있습니다.
- 현재 API 연결은 HTTP입니다. 스냅샷에 연락처는 포함하지 않지만, 전송 무결성을 강화하려면 CT103 HTTPS를 먼저 구성해야 합니다.
- 저장소 기록에는 매일의 `data.json` 변경 이력이 남습니다. 게시를 중단하더라도 과거 커밋의 데이터를 저장소 기록에서 제거해야 할 수 있습니다.
- 수리일정 관리, 연락처, 서버 캡쳐 저장, 다른 화면 링크는 이 정적 사이트에 포함하지 않습니다.
