from client import IngestionClient

# Initialize
client = IngestionClient()
<<<<<<< HEAD

# Upload a file
# result = client.upload_file("C:\\Users\\omvis\\Downloads\\Gmail - Poster Session for UPLINK Interns at ACM IKDD CODS’25 Conference.pdf")
# print(result["chunks_processed"])

# # Search
results = client.search("what was the email from IKDD office to Om Vishesh", n_results=3)
print(results)

# Ingest directory
# result = client.ingest_directory("/path/to/documents")
=======
# 
# Upload  file
# result = client.upload_file("C:\\Users\\Hp\\Downloads\\simpleadio.mp3")
# print(result["chunks_processed"])

# Search
results = client.search("up Scholarship", n_results=5)
print(results)
>>>>>>> ed8660f32c6d5ea3fdd01b8a7f69a9dd55dc5392
