#!/usr/bin/env python3
"""
Server startup script
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="192.168.45.202", port=8000, reload=False)