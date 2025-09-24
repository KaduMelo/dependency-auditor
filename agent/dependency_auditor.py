import os
import glob
import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

PROMPT = open("agent/prompt.md").read()  # o prompt que você criou

def collect_dependency_files():
    files = []
    for pattern in ["**/package.json", "**/requirements.txt", "**/pom.xml", "**/go.mod"]:
        files.extend(glob.glob(pattern, recursive=True))
    return files

def main():
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    files = collect_dependency_files()
    content = ""
    for f in files:
        with open(f, "r") as fp:
            content += f"\n--- File: {f} ---\n{fp.read()}"

    prompt = PromptTemplate.from_template(PROMPT)
    chain = prompt | llm

    result = chain.invoke({"dependencies": content})
    
    ts = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    out_path = f"docs/agents/dependency-auditor/dependencies-report-{ts}.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w") as f:
        f.write(result.content)

    print(f"Report saved to {out_path}")

if __name__ == "__main__":
    main()
