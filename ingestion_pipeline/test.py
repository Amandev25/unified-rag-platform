from client import IngestionClient

# Initialize
client = IngestionClient()

# Upload a file
result = client.upload_file("C:\\Users\\Hp\\Downloads\\Prashant.pdf")
print(result["chunks_processed"])

# # Search
# results = client.search("what was the email from IKDD office to Om Vishesh", n_results=3)
# print(results)

# # Ingest directory
# # result = client.ingest_directory("/path/to/documents")
# 
# Upload  file
# result = client.upload_file("C:\\Users\\Hp\\Downloads\\simpleadio.mp3")
# print(result["chunks_processed"])

# Search
results = client.search("up Scholarship", n_results=5)
print(results)
