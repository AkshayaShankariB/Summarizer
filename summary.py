import ollama

# ✂️ Split text into chunks
def split_text(text, chunk_size=800):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


# 🔍 Extract main topic from query
def extract_topic(query):
    stop_words = {
        "explain", "in", "on", "about", "give", "points",
        "what", "is", "the", "of", "are", "define"
    }

    words = query.lower().split()
    keywords = [w for w in words if w not in stop_words and not w.isdigit()]

    return " ".join(keywords)


# 🔢 Extract number of points from query
def extract_number(query):
    for word in query.split():
        if word.isdigit():
            return int(word)
    return None


# 🔍 Filter chunks based on topic
def filter_chunks(chunks, query):
    if query.strip() == "":
        return chunks  # no filtering

    topic = extract_topic(query)

    if topic == "":
        return chunks

    filtered = [chunk for chunk in chunks if topic in chunk.lower()]

    return filtered if filtered else chunks  # fallback


# 🧠 Prompt for chunk summarization
def create_prompt(chunk, query):
    if query.strip() == "":
        return f"""
Summarize the following text into clear bullet points.
Keep it short and simple.

Text:
{chunk}
"""
    else:
        topic = extract_topic(query)

        return f"""
Topic: {topic}

Task:
- Extract ONLY information related to this topic
- Ignore all unrelated content
- If nothing relevant is found, return: No relevant information found
- Provide bullet points only

Text:
{chunk}
"""


# 🤖 Summarize each chunk
def summarize_chunk(chunk, query):
    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': create_prompt(chunk, query)}]
        )
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# 🧠 Final summary
def final_summary(summaries, query):
    combined = "\n".join(summaries)

    if query.strip() == "":
        final_prompt = f"""
Convert the following into clean, well-structured bullet points.
Remove repetition and keep it concise.

{combined}
"""
    else:
        topic = extract_topic(query)
        num_points = extract_number(query)

        # 🎯 Dynamic points handling
        if num_points:
            point_instruction = f"Provide EXACTLY {num_points} bullet points."
        else:
            point_instruction = "Provide a reasonable number of bullet points."

        final_prompt = f"""
Topic: {topic}

Task:
- Keep ONLY points related to this topic
- Remove all unrelated content completely
- {point_instruction}
- Keep it clear and concise

{combined}
"""

    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': final_prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Error: {str(e)}"