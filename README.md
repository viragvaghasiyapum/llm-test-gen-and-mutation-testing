
# 🧪 MuTAP - Mutation Test Case Generation using Augmented Prompt

MuTAP is a mutation testing-based system that leverages Large Language Models (LLMs) to generate effective unit test cases for Python programs, especially where natural language descriptions of the code are unavailable.

---

## 📖 About MuTAP

MuTAP enhances test generation by:
- Prompting LLMs with the Program Under Test (PUT)
- Generating initial tests
- Identifying undetected mutants
- Augmenting prompts with surviving mutants
- Iterating until mutation score reaches 100% or no more mutants remain
- Reached average score up to 95.23% Mutation Score and 72.00% real-world buggy code detection rate for a short test run on 20 problems each

---

## 📦 Project Structure & Setup

### 1. 🔧 Model Setup

Models should be placed in the `/model` directory.

- **DeepSeek Coder 6.7B (Q4_K_M)**
  - [Download GGUF Model](https://huggingface.co/TheBloke/deepseek-coder-6.7B-base-GGUF/tree/main)

- **LLaMA 2 7B Chat (Q4_K_M)**
  - [Download GGUF Model](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/tree/main)

---

### 2. 🏗 llama.cpp Setup

- Clone and build llama.cpp:
  ```bash
  git clone https://github.com/ggerganov/llama.cpp.git
  cd llama.cpp
  make
  ```
- Place the build under:
  ```
  /buildllama
  ```

---

### 3. 📂 Dataset Setup

#### 3.1 HumanEval
- Source: [OpenAI HumanEval](https://github.com/openai/human-eval)
- Extract: `human-eval-*.jsonl` from `data/HumanEval.jsonl.gz`
- Place under:  
  ```
  data/humaneval/
  ```

#### 3.2 Refactory
- Source: [GitHub Refactory](https://github.com/githubhuyang/refactory)
- Extract: `question directories` from `data.zip`
- Place under:  
  ```
  data/refactory/
  ```

📝 When you run `main.py`, formatted datasets will automatically be generated and saved in:
```
output/formatted/
```

---

## 🐳 Docker Instructions

### 🧠 GPU-Compatible Setup (CUDA-enabled)
- Uses a CUDA-friendly Ubuntu image.
- No changes required to Dockerfile.

### 🧱 Non-GPU Setup
If you're not using a GPU:
- Use a normal Ubuntu image.
- Modify Dockerfile accordingly to replace CUDA build with normal build for llama.cpp .
- **Important:** Remove `'runtime'` and `'environment'` keys from `docker-compose.yaml`.

---

### 🚀 Run MuTAP

```bash
cd llm-mutap
docker-compose build --no-cache
docker-compose run --rm mutap-cli
```

---

