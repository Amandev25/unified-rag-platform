from rag_client import create_rag_client

# Initialize
rag = create_rag_client()

# rag.upload_file("D:\\ollama-rag\\my_documents\\coursera certificate.pdf")
# Ask a question
result = rag.generate_answer("what is the coursera certificate about?")
print(result)

