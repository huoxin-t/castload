import requests

# 测试文件下载API
response = requests.get('http://localhost:5000/api/download-file/test_podcast.mp3')

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

# 将文件保存到本地
if response.status_code == 200:
    with open('downloaded_test.mp3', 'wb') as f:
        f.write(response.content)
    print("File downloaded successfully")
else:
    print("Failed to download file")