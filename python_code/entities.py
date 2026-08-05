def chunk_to_entity(chunk):
    words = []

    for token in chunk:
        if token.dep_ in ("det"):
            continue
        if token == chunk.root and token.pos_ == "NOUN":
            words.append(token.lemma_)
        else:
            words.append(token.text)

    return " ".join(words)

def extract_entities(sentence):
    entity_map = {}
        
    for chunk in sentence.noun_chunks:
        if chunk.root in entity_map:
            continue

        if chunk.root.pos_ == "PRON":
            continue

        entity_map[chunk.root] = chunk_to_entity(chunk)
    
    #temporary catch
    for token in sentence:
        if token.pos_ in ("NOUN","PROPN") and token not in entity_map:
            entity_map[token] = token.text

    return entity_map