import json
import pandas as pd

def merge(qrels, queries, corpus, output):
    df_qrels = pd.read_csv(qrels, sep='\t')
    qrels_dict = df_qrels.drop_duplicates(subset='query_id', keep='first').set_index('query_id')['corpus_id'].to_dict()

    corpus_lookup = {}
    with open(corpus, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            corpus_lookup[item['_id']] = {
                'title': item.get('title', ''),
                'text': item.get('text', '')
            }

    with open(queries, 'r', encoding='utf-8') as f_in, \
         open(output, 'w', encoding='utf-8') as f_out:
        
        for line in f_in:
            query = json.loads(line)
            query_id = query.get('_id')
            
            if query_id in qrels_dict:
                corpus_id = str(qrels_dict[query_id])
                query['corpus_id'] = corpus_id
                
                if corpus_id in corpus_lookup:
                    corpus_data = corpus_lookup[corpus_id]
                    query['corpus_title'] = corpus_data['title']
                    query['corpus_text'] = corpus_data['text']
            
            f_out.write(json.dumps(query, ensure_ascii=False) + '\n')

def main():
    merge(
        'Cancer_Patients/PAR_cancer/cancer_qrels_train.tsv', 
        'test/cancer_train_queries.jsonl', 
        'Cancer_Patients/PAR_cancer/cancer_corpus.jsonl', 
        'merged_data.jsonl'
    )

if __name__ == '__main__':
    main()