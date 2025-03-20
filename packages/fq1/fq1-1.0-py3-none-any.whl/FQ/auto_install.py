import subprocess
import sys

def install_github_repo(repo_url):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"git+{repo_url}@0.11.18"])
        print(f"Đã cài đặt thành công từ {repo_url}")
    except subprocess.CalledProcessError:
        print(f"Lỗi khi cài đặt từ {repo_url}")

if __name__ == "__main__":
    repo_url = "https://github.com/NgocAnLam/fqtest.git"
    install_github_repo(repo_url)
