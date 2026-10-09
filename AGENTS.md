# 릴리즈 규칙

- 모든 새 한글패치 릴리즈에는 xdelta와 해당 빌드에 대응하는 PCSX2 와이드 pnach를 함께 첨부한다. 사용자의 지속적인 지시다.
- 새 빌드의 실행 파일 CRC를 확인한다. CRC가 바뀌면 이전 pnach를 이름만 바꾸지 말고 주소와 실행 호환성을 재검증한다.
- 릴리즈 노트에 docs/WIDESCREEN.md의 상세 사용법과 검증 한계를 포함한다.
- release_manifest.json에 와이드 파일 이름·CRC·크기·SHA-256을 기록한다.
- 업로드 후 GitHub 자산의 크기와 digest를 확인한다. 원본 ISO 및 한글판 ISO는 업로드하지 않는다.
