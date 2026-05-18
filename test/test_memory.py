from memory.memory_store import MemoryStore
store = MemoryStore()
store.save_memory("L001", "Learner scored 55 in Vector Databases")
store.save_memory("L001", "Learner prefers practical examples")
memories = store.retrieve_memories("L002", query="what does learner know", k=5)
print(memories)
# Expected: ['Learner scored 55 in Vector Databases', 'Learner prefers practical examples']
