from openai import OpenAI
import numpy as np
import heapq

client = OpenAI()  # reads OPENAI_API_KEY from the environment automatically

def cosine(a, b): return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

snippets = [
    "Nimbus Coffee Roasters was founded in 2014 by Mara Delacroix and Toby Fenn in Portland, Oregon.",
    "As of 2023, Nimbus operates seven café locations across Oregon and Washington.",
    "Nimbus sells three house blends: Stratus (light roast), Cumulus (medium roast), and Thunderhead (dark roast).",
    "All beans are sold as whole bean in 12-ounce bags and ground to order in-store; there is no pre-ground or flavored coffee.",
    "Nimbus sources green coffee directly from farms in Ethiopia, Colombia, and Guatemala.",
    "Direct-trade contracts guarantee farmers a minimum price of $3.10 per pound, above the Fair Trade baseline.",
    "All Nimbus cafés have used compostable cups and lids since January 2022.",
    "The roasting facility runs on 100% renewable electricity, with a goal of carbon neutrality by 2030.",
    "The Cloud Club loyalty program costs $9 per month and includes one free 12-ounce bag plus 10% off in-store drinks.",
    "Membership can be cancelled at any time with no penalty, and there is no annual plan.",
]

snippet_embeddings = []

for (i, snippet) in enumerate(snippets):
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=snippet
    ).data[0].embedding
    snippet_embeddings.append((snippet, embedding))

query_embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="What is Nimbus Coffee Roasters?"
).data[0].embedding

cosine_similarities = []

for snippet, embedding in snippet_embeddings:
    cosine_similarity = cosine(query_embedding, embedding)
    cosine_similarities.append((cosine_similarity, snippet))

# Get the top 3 most similar snippets
top_3_similarities = heapq.nlargest(3, cosine_similarities)

chat = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer using only the text below. If it's not there, say you don't know."},
        {
            "role": "user",
            "content": str(top_3_similarities[0][1])
            + str(top_3_similarities[1][1])
            + str(top_3_similarities[2][1])
            + "What is Nimbus Coffee Roasters?"
        },
    ],
)

print(chat.choices[0].message.content)