import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_article_card(article: dict) -> str:
    prompt = f"""
Você é um professor orientador especialista em TCC e revisão bibliográfica.
Com base no artigo abaixo, gere uma ficha descritiva acadêmica em português.
Não invente dados. Se uma informação não estiver no resumo ou metadados, escreva: "Não informado no resumo disponível".

ARTIGO:
Título: {article.get("title")}
Autores: {article.get("authors")}
Ano: {article.get("year")}
Periódico: {article.get("journal")}
DOI: {article.get("doi")}
Resumo: {article.get("abstract")}

Responda exatamente neste formato JSON:
{{
  "objective": "",
  "methodology": "",
  "results": "",
  "conclusion": "",
  "relevance": ""
}}
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Você extrai informações acadêmicas com precisão e evita alucinações.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def generate_review(
    theme: str,
    review_type: str,
    course: str,
    articles: list,
    cards: list,
    format_style: str,
) -> str:
    articles_text = ""
    for idx, article in enumerate(articles, start=1):
        articles_text += f"""
ARTIGO {idx}
Título: {article.get("title")}
Autores: {article.get("authors")}
Ano: {article.get("year")}
Periódico: {article.get("journal")}
Resumo: {article.get("abstract")}
"""

    prompt = f"""
Você é um professor universitário especialista em metodologia científica.
Gere um artigo de revisão bibliográfica em português para o curso de {course}.

Tema: {theme}
Tipo de revisão: {review_type}
Norma de formatação: {format_style}

Estrutura obrigatória:
1. Título
2. Resumo
3. Introdução
4. Justificativa
5. Objetivo Geral
6. Objetivos Específicos
7. Metodologia
8. Resultados
9. Discussão
10. Conclusão
11. Referências

Regras de escrita:
- Introdução: 5 parágrafos.
- Justificativa: 4 parágrafos.
- Metodologia: descrever bases, critérios de inclusão e exclusão.
- Resultados: sintetizar os artigos.
- Discussão: comparar os achados.
- Conclusão: 4 parágrafos.
- Cada parágrafo deve ter de 6 a 10 linhas.
- Não invente referências.
- Use apenas os artigos fornecidos abaixo.
- Não cite artigos que não estejam na lista.

ARTIGOS DISPONÍVEIS:
{articles_text}
"""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Você redige textos acadêmicos baseados exclusivamente nas fontes fornecidas.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
