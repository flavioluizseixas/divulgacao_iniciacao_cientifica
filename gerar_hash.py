import uuid

def random_hash_8():
    return uuid.uuid4().hex[:8]

print(random_hash_8())