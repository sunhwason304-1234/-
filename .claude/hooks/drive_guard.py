#!/usr/bin/env python3
"""Google Drive 접근을 AI폴더(와 하위 항목)로만 제한하는 훅.

PreToolUse: AI폴더 밖을 건드릴 수 있는 Drive 호출을 차단한다.
PostToolUse: AI폴더 안에서 찾거나 만든 파일 ID를 허용 목록에 기록한다.
파일 ID로 동작하는 도구(읽기, 수정, 공유, 삭제 등)는 허용 목록에 있는 ID만 쓸 수 있다.
"""
import json
import os
import re
import sys

AI_FOLDER_ID = "1Yfk6Zx9NqEfKC2ld9m6Sf1m8n3UnV2OA"
PREFIX = "mcp__Google_Drive__"
PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
ALLOWLIST = os.path.join(PROJECT_DIR, ".claude", "drive-allowlist.txt")

# 파일 ID 하나를 받아 동작하는 도구들
FILE_ID_TOOLS = {
    "read_file_content",
    "download_file_content",
    "get_file_metadata",
    "get_file_permissions",
    "update_file",
    "trash_file",
    "share_file",
    "copy_file",
}


def load_allowed():
    allowed = {AI_FOLDER_ID}
    try:
        with open(ALLOWLIST, encoding="utf-8") as f:
            allowed.update(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        pass
    return allowed


def save_allowed(new_ids):
    if not new_ids:
        return
    os.makedirs(os.path.dirname(ALLOWLIST), exist_ok=True)
    with open(ALLOWLIST, "a", encoding="utf-8") as f:
        for i in sorted(new_ids):
            f.write(i + "\n")


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "[AI폴더 전용 규칙] " + reason,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def check_search(query, allowed):
    parents = re.findall(r"parentId\s*=\s*'([^']*)'", query)
    if not parents:
        deny("검색에는 parentId = 'AI폴더 또는 그 하위 폴더 ID' 조건이 반드시 있어야 합니다.")
    outside = [p for p in parents if p not in allowed]
    if outside:
        deny("AI폴더 밖의 폴더는 검색할 수 없습니다: " + ", ".join(outside))
    # 따옴표 안의 값을 지운 뒤 or / not 으로 범위를 넓히는 것을 막는다
    bare = re.sub(r"'(?:\\'|[^'])*'", "''", query)
    if re.search(r"\b(or|not)\b", bare, re.IGNORECASE):
        deny("검색 범위를 넓힐 수 있는 or / not 은 사용할 수 없습니다.")


def pre(tool, args):
    allowed = load_allowed()
    if tool == "search_files":
        check_search(args.get("query") or "", allowed)
    elif tool == "list_recent_files":
        deny("최근 파일 목록은 Drive 전체를 보여주므로 사용할 수 없습니다.")
    elif tool == "create_file":
        if args.get("parentId") not in allowed:
            deny("새 파일은 AI폴더(또는 그 하위 폴더) 안에만 만들 수 있습니다. parentId를 지정하세요.")
    elif tool in FILE_ID_TOOLS:
        file_id = args.get("fileId")
        if file_id not in allowed:
            deny("AI폴더 안에서 확인된 파일만 사용할 수 있습니다: " + str(file_id))
        if tool == "copy_file" and args.get("parentId") not in allowed:
            deny("복사본은 AI폴더(또는 그 하위 폴더) 안에만 만들 수 있습니다.")
    else:
        deny("허용 목록에 없는 Google Drive 도구입니다: " + tool)


def walk(obj, out):
    """응답 안의 파일 객체(id 가 있는 dict)를 모두 찾는다. JSON 문자열도 풀어서 본다."""
    if isinstance(obj, dict):
        if isinstance(obj.get("id"), str):
            out.append(obj)
        for v in obj.values():
            walk(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk(v, out)
    elif isinstance(obj, str) and obj.lstrip()[:1] in ("{", "["):
        try:
            walk(json.loads(obj), out)
        except ValueError:
            pass


def post(tool, args, response):
    if tool not in ("search_files", "create_file", "copy_file"):
        return
    allowed = load_allowed()
    files = []
    walk(response, files)
    new_ids = set()
    for f in files:
        parent = f.get("parentId")
        if parent is None and tool in ("create_file", "copy_file"):
            parent = args.get("parentId")
        if parent in allowed and f["id"] not in allowed:
            new_ids.add(f["id"])
    save_allowed(new_ids)


def main():
    data = json.load(sys.stdin)
    name = data.get("tool_name", "")
    if not name.startswith(PREFIX):
        return
    tool = name[len(PREFIX):]
    args = data.get("tool_input") or {}
    if data.get("hook_event_name") == "PostToolUse":
        post(tool, args, data.get("tool_response"))
    else:
        pre(tool, args)


if __name__ == "__main__":
    main()
