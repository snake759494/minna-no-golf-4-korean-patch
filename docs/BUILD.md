# 제작 및 재빌드

일반 사용자는 릴리즈의 xdelta를 적용하면 됩니다. 이 저장소는 제작 자료 공개용이며, 추출 게임 파일과 배경 합성 자산이 없어 단독으로 전체 빌드를 재현할 수는 없습니다.

기존 작업 폴더 구조에서는 `tools/`의 파일을 `work/`에 두고, 원본 ISO 및 폰트를 그 상위 폴더에 둡니다.
Python 3.13과 requirements.txt의 라이브러리를 사용했습니다.
원본에서 추출한 BIN, GFFONT, textures, 문자열 목록, ISO 목록, resource_catalog.json, audit/mti/index.json, audit/planes/index.json, audit/mti_layout_fixed.json 및 코드가 참조하는 배경 자산이 별도로 필요합니다.

```powershell
python -X utf8 work/texture_words.py
python -X utf8 work/verify_fix2.py
python -X utf8 work/pack_textures.py
python -X utf8 work/build.py
```

`texture_patch.py`는 원본 팔레트를 유지하며 글자를 합성하고 밉맵을 갱신합니다.
`texture_fix2.py`는 종료 화면 UV, 성적표, 이름 입력 도움말, TAI 7프레임을 보정합니다.
`compact_ko.py`는 경기 및 이름 입력용 고정 글자판과 문구를 처리합니다.
`fix_mti_layout.py`는 이번 수정 대상 MTI 84종의 내부 이미지와 밉맵 배치를 교정합니다.
`build.py`는 한글 글꼴·문자열·압축 묶음을 삽입하고 확장 파일의 ISO 및 게임 내부 주소를 갱신합니다.
검증 기록에 명시된 전체 플레이 미검증 범위를 확인하세요.

릴리즈 준비 시 tools/prepare_widescreen_release.py에 --notes (릴리즈 노트 경로)와 --assets (첨부 파일 폴더)를 지정합니다. CRC 호환성을 확인한 후 xdelta와 pnach를 모두 업로드합니다. 세부 규칙은 AGENTS.md를 따릅니다.
