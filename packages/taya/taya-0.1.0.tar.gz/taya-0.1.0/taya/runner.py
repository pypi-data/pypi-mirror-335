import subprocess

def main():
    # تشغيل ملف test.py
    try:
        subprocess.run(["python", "test.py"], check=True)
        print("STARTED")
    except subprocess.CalledProcessError as e:
        print(f"FAILED STARTED{e}")

if __name__ == "__main__":
    main()
