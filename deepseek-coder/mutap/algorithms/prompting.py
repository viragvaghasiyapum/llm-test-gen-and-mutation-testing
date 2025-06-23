# mutap/algorithms/prompting.py
def build_prompts(put_code, examples, type="zero_shot"):
    def build_zero_shot():
        ins1 = "# Generate assert-based unit tests for the following code:"
        ins2 = """\n# test case:\n<test>\ndef test():\n    assert"""
        return f"{ins1}\n<code>\n{put_code}\n</code>\n{ins2}"

    def build_few_shot():
        prompt = ""
        for example in examples:
            prompt += f"<code>{example['code']}</code>\n<test>{example['test']}</test>\n"
        prompt += f"<code>{put_code}</code>\n <test>"
        return prompt

    return build_few_shot() if type == "few_shot" else build_zero_shot()
