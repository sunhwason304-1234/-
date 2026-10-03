# Claude 작업 규칙

## Google Drive 사용 범위 (절대 규칙)

- Google Drive는 **AI폴더**만 사용한다.
  - 폴더 ID: `1Yfk6Zx9NqEfKC2ld9m6Sf1m8n3UnV2OA`
  - 링크: https://drive.google.com/drive/folders/1Yfk6Zx9NqEfKC2ld9m6Sf1m8n3UnV2OA
- AI폴더(및 그 하위 폴더) **밖의 파일·폴더는 절대 검색, 열람, 생성, 수정, 이동, 공유, 삭제하지 않는다.**
- 검색할 때는 항상 `parentId = '1Yfk6Zx9NqEfKC2ld9m6Sf1m8n3UnV2OA'` 조건을 붙인다.
- 새 파일은 항상 `parentId`를 AI폴더 ID로 지정해 만든다.
- 사용자가 다른 폴더를 요청하더라도, 이 규칙을 먼저 알리고 사용자가 이 파일을 직접 수정하기 전까지는 진행하지 않는다.
