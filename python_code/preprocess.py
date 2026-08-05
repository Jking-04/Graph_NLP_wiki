import re

def text_preprocess(nlp_model,text):
    text = normalize_whitespace(text)
    text = coref_res(nlp_model,text)
    doc = nlp_model(text)

    return doc

def normalize_whitespace(text):
    text = re.sub(r"\s+", " ", text).strip()
    return text

def coref_res(nlp_model,text):
    doc = nlp_model(text,
                component_cfg={
                    "fastcoref": {
                    "resolve_text": True
                }
            }
        )
    
    resolved = doc._.resolved_text
    return resolved