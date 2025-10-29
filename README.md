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
Activate the virtual environment for analytic program on Windows
```powershell
	Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
	.\activate_env.ps1
```

3. Run the program
```
    python ./run_program.py
```
