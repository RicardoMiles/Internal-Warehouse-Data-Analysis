### Project Structure Setup

Place four folders in the root directory of the project: `\UK`,` \DE`,` \NL`, `\FR`

```shell
mkdir UK DE NL FR
```

Import data files into the corresponding folders using the following filename format (from iWMS):

<img width="1840" height="1119" alt="Image" src="https://github.com/user-attachments/assets/9d2efffd-9e55-4be1-bf8e-9656dfd5abc6" />

Under the root directory of current project create folders: `Internal-Warehouse-Data-Analysis\UK`,`Internal-Warehouse-Data-Analysis\FR`,`Internal-Warehouse-Data-Analysis\NL`,`Internal-Warehouse-Data-Analysis\DE`

Copy and paste all of inventory / inbound / outbound data into the folders with country name, like the screenshot shown above. 

Run program in terminal (any Commandline Tool) as followed instruction:

1. Deploy the virtual environment for analytic program
```bash
	python ./deploy_env.py
```


2. Activate the virtual environment for analytic program on Linux and macOS
```bash
	chmod u+x activate_env.sh
	source ./activate_env.sh
```
​	Activate the virtual environment for analytic program on Windows
```powershell
	Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
	.\activate_env.ps1
```

3. Run the program
```bash
python ./run_program.py

# Windows
python.exe ./run_program.py
```

​	Run the program with parameter, after placing the data files, run the script with one of the following parameter 	options, defaultly date will be today:

```bash
# 1. Specify a date (format: YYYY-MM-DD)
python ./run_program.py 2025-10-29

# 2. Use yesterday's date automatically
python ./run_program.py --yesterday

# 3. Explicitly specify date with --date flag
python ./program.py --date 2025-10-29

# Windows ver running
python.exe ./run_program.py 2025-10-29

python.exe ./run_program.py --yesterday

python.exe ./program.py --date 2025-10-29
```

> **Note**: The date will be converted to YYYYMMDD format internally (e.g., 20251029) to match the data file naming convention.

### 项目结构设置

在项目根目录下放置四个文件夹：`\UK`、`\DE`、` \NL`、`\FR`

```shell
mkdir UK DE NL FR
```

将数据文件导入对应文件夹中，使用以下文件名格式（来自 iWMS）：

<img width="1840" height="1119" alt="Image" src="https://github.com/user-attachments/assets/9d2efffd-9e55-4be1-bf8e-9656dfd5abc6" />

在当前项目的根目录下创建以下文件夹：  
`Internal-Warehouse-Data-Analysis\UK`、`Internal-Warehouse-Data-Analysis\FR`、`Internal-Warehouse-Data-Analysis\NL`、`Internal-Warehouse-Data-Analysis\DE`

将所有 **库存 / 入库 / 出库** 数据复制粘贴到对应国家名称的文件夹中，如上截图所示。

在终端（任意命令行工具）中按以下步骤运行程序：

---

1. **部署分析程序的虚拟环境**

```bash
python ./deploy_env.py
```

---

2. **在 Linux 和 macOS 上激活虚拟环境**

```bash
chmod u+x activate_env.sh
source ./activate_env.sh
```

​	**在 Windows 上激活虚拟环境**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\activate_env.ps1
```

---

3. **运行程序**

```bash
python ./run_program.py

# Windows 系统
python.exe ./run_program.py
```

​	**带参数运行程序**（放置好数据文件后，选择以下任一方式运行脚本，默认日期为今天）：

```bash
# 1. 指定日期（格式：YYYY-MM-DD）
python ./run_program.py 2025-10-29

# 2. 自动使用昨天的日期
python ./run_program.py --yesterday

# 3. 使用 --date 参数显式指定日期
python ./run_program.py --date 2025-10-29

# Windows 版运行方式
python.exe ./run_program.py 2025-10-29
python.exe ./run_program.py --yesterday
python.exe ./run_program.py --date 2025-10-29
```

> **注意**：输入的日期会在内部自动转换为 `YYYYMMDD` 格式（例如 `20251029`），以匹配数据文件的命名规则。
