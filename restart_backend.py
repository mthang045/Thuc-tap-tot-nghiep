import subprocess, time, os, sys

# Kill existing python processes running app.py
try:
    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
    time.sleep(2)
except:
    pass

# Clear pycache
pycache = r"C:\Users\buimi\OneDrive\Documents\Thực tập\backend\__pycache__"
if os.path.exists(pycache):
    import shutil
    shutil.rmtree(pycache)
    print(f"Cleared {pycache}")

# Start backend
backend_dir = r"C:\Users\buimi\OneDrive\Documents\Thực tập\backend"
app_file = os.path.join(backend_dir, "app.py")

print(f"Starting {app_file}...")
subprocess.Popen([sys.executable, app_file], cwd=backend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
print("Backend started!")
