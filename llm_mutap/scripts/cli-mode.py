import subprocess
import os
import mutap.utils.helper as helper

print('CLI-Mode: "deepseek-coder-6.7b-base"')
while True:
    prompt = input("> ").strip() 
    if prompt.lower() in {"exit", "quit"}:
        break
    elif prompt.lower() == "clear":
        os.system("clear")
        print('CLI-Mode: "deepseek-coder-6.7b-base"')
        continue

    try:
        process = subprocess.Popen([
                helper.getPath("binary"),
                "-m", helper.getPath("model"),
                "-p", prompt,
                "--n-predict", "512",
                "--temp", "0.2",
                "--top-p", "0.95",
                "--repeat-penalty", "1.1"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Stream output line by line
        for line in process.stdout:
            if "</test>" in line:
                break
            print(line, end="")

    except Exception as e:
        print(f"Error: {e}")