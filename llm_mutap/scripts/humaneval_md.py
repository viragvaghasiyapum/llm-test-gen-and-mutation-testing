import json
import mutap.utils.helper as helper

def jsonl_to_markdown(input_path, output_path):
    with open(input_path, "r") as fin, open(output_path, "w") as fout:
        for line in fin:
            obj = json.loads(line)
            task_id = obj.get("task_id", "Unknown Task")

            fout.write(f"## {task_id}\n\n")

            for key, value in obj.items():
                fout.write(f"### {key}\n\n")
                fout.write("```python\n")
                fout.write(str(value).strip() + "\n")
                fout.write("```\n\n")

    print(f"✅ Markdown saved to: {output_path}")

if __name__ == "__main__":
    jsonl_to_markdown(helper.getPath('humaneval_src'), helper.getPath('humaneval_converted_md'))