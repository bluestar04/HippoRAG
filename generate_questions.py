import json
import os
import json
import pandas as pd
from openai import OpenAI, APIConnectionError

BASE_URL = "https://llm1-compute.cms.hu-berlin.de/v1/"
OPENAI_API_KEY = "secret_but_not_used"
PROMPT_FILE = "hipporag_questions_prompt.txt"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

INPUT_FILE = "merged_data.jsonl"
OUTPUT_FILE = "questions.jsonl"

client = OpenAI(base_url=BASE_URL, api_key=OPENAI_API_KEY)

# def generate_question(patient_id, patient_text, article_id, article_title, article_text):
#     prompt = f"""
#     You are given a clinical case report and a biomedical research abstract. 
#     Your task is to analyze them **together** and identify what **new clinical or biological questions become answerable only when considering both texts jointly**.

#     CASE REPORT (Patient ID: {patient_id}):
#     {patient_text}

#     RESEARCH ABSTRACT (Article ID: {article_id}, Title: {article_title}):
#     {article_text}

#     Instructions:
#     1. Carefully read the **case report** and the **abstract**.
#     2. Determine whether the given abstract is meaningfully related to that case report. If they are not related, say “No meaningful joint question could be found.”
#     3. If meaningfully related, formulate questions that **cannot be answered by the case report alone** and **cannot be answered by the abstract alone**, but **can only be answered when both the case report and abstract are considered together**. 
#     4. The questions should be **specific to the patient's details**, and not generic biomedical questions. 
#     5. For each question:
#         * Write the **question**.
#         * Provide a **short explanation** of how the **case report provides the clinical context** and how the **abstract provides the missing biological or medical explanation**. Do not claim causality unless explicitly stated in the abstract.
#         * For this question and explanation, list the information you retrieved directly from 
#             - the case report
#             - the abstract
#     6. Focus on **mechanisms, disease interpretation, diagnostic reasoning, or clinical implications**.
#     """

#     try:
#         response = client.chat.completions.create(
#             model="llm1",
#             messages=[
#                 {"role": "system", "content": "You are a medical researcher. Answer concisely."},
#                 {"role": "user", "content": prompt},
#             ],
#             max_tokens=600,
#             temperature=0.1,
#             stream=False
#         )
#         return response.choices[0].message.content.strip()
#     except APIConnectionError as e:
#         return f"Error connecting to API: {e}"
#     except Exception as e:
#         return f"An error occurred: {e}"

def generate_question(patient_text, article_title, article_text):
    prompt = PROMPT_TEMPLATE.format(
        patient_text=patient_text or "",
        article_title=article_title or "",
        article_text=article_text or ""
    )

    try:
        response = client.chat.completions.create(
            model="llm1",
            messages=[
                {"role": "system", "content": "You are a medical researcher. Answer concisely."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
            temperature=0.1,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except APIConnectionError as e:
        return f"Error connecting to API: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def convert_jsonl_to_csv(jsonl_input, csv_output):
    data = []
    
    with open(jsonl_input, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    df = pd.DataFrame(data)
    df.columns = ['Patient ID', 'Article ID', 'Question']
    df.to_csv(csv_output, index=False, sep=',', encoding='utf-8-sig')

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f_in, \
        open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
    
        for line in f_in:
            data = json.loads(line)
            
            patient_id = data.get('patient_id')
            patient_text = data.get('patient_text')
            article_id = data.get('article_id')
            article_title = data.get('article_title')
            article_text = data.get('article_text')
        

            question = generate_question( patient_text, article_title, article_text)
                
            result = {
                "patient_id": patient_id,
                "article_id": article_id,
                "question": question
            }
            
            f_out.write(json.dumps(result, ensure_ascii=False) + '\n')
            f_out.flush()
 
    convert_jsonl_to_csv(OUTPUT_FILE, 'test/questions.csv')

if __name__ == '__main__':
    main()
