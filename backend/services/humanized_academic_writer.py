import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_humanized_academic_section(
    section_name: str,
    theme: str,
    sources: str,
    user_notes: str | None = None,
) -> str:
    prompt = f"""
Você é um orientador acadêmico.
Escreva a seção "{section_name}" sobre o tema "{theme}".

Regras obrigatórias:
- Use linguagem acadêmica clara, mas natural.
- Não use frases genéricas.
- Não invente referências.
- Cada argumento relevante deve estar apoiado nas fontes fornecidas.
- Evite repetição mecânica de conectivos.
- Alterne frases curtas e médias.
- Use transições lógicas entre ideias.
- Não escreva como propaganda.
- Não prometa originalidade artificial.
- O texto deve servir como rascunho editável pelo aluno.
- Quando faltar evidência, escreva que a literatura disponível é limitada.
- Inclua indicações onde o aluno deve inserir observações próprias.

Observações do aluno:
{user_notes or "Nenhuma observação enviada."}

Fontes disponíveis:
{sources}
""".strip()

    response = _client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você escreve textos acadêmicos originais, rastreáveis, "
                    "prudentes e baseados em fontes reais."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.45,
    )
    return response.choices[0].message.content
