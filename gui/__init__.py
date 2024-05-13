import sys
from pathlib import Path

# 获取当前工作目录的路径
current_dir = Path.cwd()
print(current_dir)

# 将当前目录添加到sys.path的开头
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
