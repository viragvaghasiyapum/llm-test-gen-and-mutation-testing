import subprocess
import os

model_path = "/code/model/deepseek-coder-6.7b-base.Q4_K_M.gguf"
binary_path = "/code/llama.cpp/build/bin/llama-cli"

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
                binary_path,
                "-m", model_path,
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