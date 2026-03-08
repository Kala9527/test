#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 连通性与功能测试脚本
- 文字生成：OpenAI 格式 POST /v1/chat/completions
- 图片生成：Gemini POST /v1beta/models/gemini-3-pro-image-preview:generateContent
- 视频生成：Sora（OpenAI 格式）
"""

import os
import sys
import json
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("请先安装依赖: pip install -r requirements.txt")
    sys.exit(1)

# 加载 .env（项目根目录）
load_dotenv(Path(__file__).resolve().parent / ".env")

# 配置（优先从环境变量读取）
CHAT_BASE_URL = os.getenv("CHAT_BASE_URL", "https://api.openai.com").rstrip("/")
CHAT_API_KEY = os.getenv("CHAT_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "claude-haiku-4-5-20251001")

GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com").rstrip("/")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")

SORA_BASE_URL = os.getenv("SORA_BASE_URL", "https://api.openai.com").rstrip("/")
SORA_API_KEY = os.getenv("SORA_API_KEY", "")
SORA_MODEL = os.getenv("SORA_MODEL", "sora-2-pro-all")


def test_chat_completions():
    """测试文字生成：OpenAI 格式 POST /v1/chat/completions"""
    print("\n--- 1. 文字生成 (OpenAI 格式 /v1/chat/completions) ---")
    if not CHAT_API_KEY:
        print("跳过: 未设置 CHAT_API_KEY")
        return False
    url = f"{CHAT_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CHAT_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": "回复一句话：你好，API 连通正常。"}],
        "max_tokens": 100,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        print(f"状态: {r.status_code}")
        print(f"模型: {CHAT_MODEL}")
        print(f"回复: {content[:200]}")
        return True
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                print("响应:", e.response.text[:500])
            except Exception:
                pass
        return False


def test_gemini_image():
    """测试图片生成：Gemini generateContent"""
    print("\n--- 2. 图片生成 (Gemini generateContent) ---")
    if not GEMINI_API_KEY:
        print("跳过: 未设置 GEMINI_API_KEY")
        return False
    # 使用用户指定的模型名
    model = GEMINI_IMAGE_MODEL
    url = f"{GEMINI_BASE_URL}/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": "Generate a simple image: a red circle on white background."}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "responseMimeType": "image/png",
        },
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            print(f"状态: {r.status_code}, 响应: {r.text[:500]}")
            return False
        data = r.json()
        if "candidates" in data and data["candidates"]:
            print("状态: 200, 图片生成接口调用成功")
            return True
        print("响应无 candidates:", json.dumps(data)[:300])
        return False
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                print("响应:", e.response.text[:500])
            except Exception:
                pass
        return False


def test_sora_video():
    """测试视频生成：OpenAI 格式（Sora）"""
    print("\n--- 3. 视频生成 (Sora / OpenAI 格式) ---")
    if not SORA_API_KEY:
        print("跳过: 未设置 SORA_API_KEY")
        return False
    url = f"{SORA_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {SORA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": SORA_MODEL,
        "messages": [{"role": "user", "content": "Generate a 2 second video: ocean waves."}],
        "max_tokens": 100,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            print(f"状态: {r.status_code}, 响应: {r.text[:400]}")
            return False
        print("状态: 200, 视频接口调用成功")
        return True
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                print("响应:", e.response.text[:400])
            except Exception:
                pass
        return False


def main():
    print("API 连通性及功能测试")
    print("配置: CHAT_BASE_URL=%s, CHAT_MODEL=%s" % (CHAT_BASE_URL, CHAT_MODEL))
    results = []
    results.append(("文字生成", test_chat_completions()))
    results.append(("图片生成", test_gemini_image()))
    results.append(("视频生成", test_sora_video()))
    print("\n--- 汇总 ---")
    for name, ok in results:
        print(f"  {name}: {'通过' if ok else '未通过'}")
    sys.exit(0 if any(r[1] for r in results) else 1)


if __name__ == "__main__":
    main()
