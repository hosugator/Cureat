#!/usr/bin/env python
import uvicorn
import sys
import os

# 프로젝트 루트를 시스템 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    print("서버를 192.168.45.20:8000에서 시작합니다...")
    uvicorn.run(
        "backend.app.main:app",
        host="192.168.45.20",
        port=8000,
        reload=False
    )