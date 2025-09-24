import os
import glob
import datetime
from loguru import logger
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from openai import OpenAI

# Configuração de logs
os.makedirs("logs", exist_ok=True)
logger.add("logs/dependency_auditor_{time}.log", rotation="5 MB", retention="7 days", level="DEBUG")

# Carregar prompt
PROMPT_FILE = "agent/prompt.md"
if not os.path.exists(PROMPT_FILE):
    logger.error(f"Prompt file not found: {PROMPT_FILE}")
    raise FileNotFoundError(f"{PROMPT_FILE} not found")

with open(PROMPT_FILE, "r") as f:
    PROMPT = f.read()
logger.info("Prompt loaded successfully.")

# Função para coletar arquivos de dependência
def collect_dependency_files():
    patterns = ["**/package.json", "**/requirements.txt", "**/pom.xml", "**/go.mod"]
    files = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))
    return files

def main():
    # Inicializar LLM
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_KEY:
        logger.error("OPENAI_API_KEY not set in environment variables")
        raise EnvironmentError("OPENAI_API_KEY not set")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_KEY)

    # Cliente OpenAI direto para métricas de token
    client = OpenAI(api_key=OPENAI_KEY)

    # Coleta arquivos
    files = collect_dependency_files()
    if not files:
        logger.warning("No dependency files found")
        return
    logger.info(f"Found dependency files: {files}")

    content = ""
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            content += f"\n--- File: {f} ---\n{fp.read()}"

    # Preparar prompt
    prompt_template = PromptTemplate.from_template(PROMPT)
    input_text = prompt_template.format(dependencies=content)

    # Chamar LLM via OpenAI para capturar tokens
    logger.info("Calling OpenAI LLM for dependency audit...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a dependency auditor agent."},
            {"role": "user", "content": input_text}
        ]
    )

    report_md = response.choices[0].message.content

    # Tokens e custo estimado
    tokens_prompt = response.usage.prompt_tokens
    tokens_completion = response.usage.completion_tokens
    tokens_total = response.usage.total_tokens
    cost_per_1000_input = 0.0015
    cost_per_1000_output = 0.002
    cost = (tokens_prompt / 1000 * cost_per_1000_input) + (tokens_completion / 1000 * cost_per_1000_output)

    logger.info(f"Tokens used - prompt: {tokens_prompt}, completion: {tokens_completion}, total: {tokens_total}")
    logger.info(f"Estimated cost for this request: ${cost:.6f}")

    # Salvar relatório
    ts = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out_path = f"docs/agents/dependency-auditor/dependencies-report-{ts}.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    logger.success(f"Dependency Audit Report saved to {out_path}")
    print(f"Dependency Audit Report saved to {out_path}")

if __name__ == "__main__":
    main()
