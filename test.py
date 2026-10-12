import json
import sys
import requests

TOKEN = "sk-HKHCY..."
BASE_URL = "https://www.imgurl.org"
IMAGE_PATH = r"D:\DataDisk\workspace\blog\media\image\article\cede49594efd021afc2e7a3da3c55c8f.jpg"
TIMEOUT = 60

# 在这里切换要测的 album_id
ALBUM_ID = 3390          # 改成你 yaml 里填的那个值再跑一次
# =========================================

def main():
    url = f"{BASE_URL}/api/v3/upload"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    params = {
        "dedup": True,
        "album_id": ALBUM_ID,
        "watermark": False,
        "compress": False,
    }

    print(f"→ POST {url}")
    print(f"→ album_id = {ALBUM_ID}")
    print("-" * 50)

    try:
        with open(IMAGE_PATH, "rb") as f:
            resp = requests.post(
                url,
                headers=headers,
                files={"file": f},
                data={"params": json.dumps(params)},
                timeout=TIMEOUT,
            )

        print(f"← HTTP 状态码: {resp.status_code}")
        print(f"← 响应体: {resp.text}")

        try:
            result = resp.json()
            if result.get("code") == 200:
                print("\n✅ 上传成功")
                print(f"   URL: {result['data']['url']}")
            else:
                print(f"\n❌ 上传失败: code={result.get('code')}, msg={result.get('msg')}")
        except Exception:
            print("\n⚠ 响应不是 JSON")

    except requests.exceptions.ReadTimeout:
        print("\n❌ 读取超时：连上了，但服务器没在超时时间内返回")
    except requests.exceptions.ConnectTimeout:
        print("\n❌ 连接超时：根本连不上")
    except Exception as e:
        print(f"\n❌ 其他错误: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()