import chromadb
import os
from datetime import datetime

class ChromaVault:
    def __init__(self, persist_directory="./chroma_db"):
        # Buat folder jika belum ada
        os.makedirs(persist_directory, exist_ok=True)
        
        # Guna PersistentClient dengan setting explicit
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=chromadb.config.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection("ayra_memories")
        except:
            self.collection = self.client.create_collection(
                name="ayra_memories",
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_conversation(self, user_msg, ayra_msg, mood_score, model_used, important=False):
        """Store a conversation turn in Chroma."""
        # Combine user and assistant message for embedding
        text = f"User: {user_msg}\nAyra: {ayra_msg}"
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "user_msg": user_msg[:200],
            "ayra_msg": ayra_msg[:200],
            "mood_score": mood_score,
            "model_used": model_used,
            "important": str(important)
        }
        # Use a unique ID based on timestamp + random
        import uuid
        doc_id = str(uuid.uuid4())
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def search(self, query, n_results=3):
        """Retrieve semantically similar conversations."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Format results for easy use
        memories = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                memories.append({
                    "text": doc,
                    "metadata": metadata,
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        return memories