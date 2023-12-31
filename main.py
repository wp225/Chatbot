import spacy

# Load the spaCy language model
nlp = spacy.load('en_core_web_sm')

# Parse user input
def parse_input(user_input):
    doc = nlp(user_input)
    intent = None
    parameters = {}

    for token in doc:
        if token.dep_ == 'ROOT':
            intent = token.lemma_
        else:
            parameters[token.text] = token.lemma_

    return intent, parameters

def generate_query(intent, parameters):
    if intent == 'search':
        query = "SELECT * FROM your_table WHERE"
        conditions = []
        for key, value in parameters.items():
            conditions.append(f"{key} = '{value}'")
        query += " AND ".join(conditions)
        print(query)
    else:
        return None

parse_input('hi how are u ')