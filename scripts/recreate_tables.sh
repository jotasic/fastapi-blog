#! /usr/bin/env bash
set -e
set -x

# 스크립트가 위치한 디렉토리의 상위 디렉토리(프로젝트 루트)로 이동
cd "$(dirname "$0")/.."

# python -m 옵션으로 스크립트를 모듈처럼 실행
# 이렇게 하면 파이썬이 프로젝트 루트에서부터 모듈을 찾기 시작함.
python -m app.recreate_tables
