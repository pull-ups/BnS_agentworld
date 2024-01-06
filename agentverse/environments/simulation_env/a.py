def find_conversations(adj_matrix):
    """
    Finds pairs of NPCs engaged in conversation based on the adjacency matrix.
    
    :param adj_matrix: A 4x4 matrix where adj_matrix[i][j] == 1 indicates that NPCs i and j are together.
    :return: A list of pairs (tuples) indicating which NPCs are engaged in conversation.
    """
    num_npcs = len(adj_matrix)
    conversations = []

    # Find NPCs that are together
    for i in range(num_npcs):
        for j in range(i + 1, num_npcs):
            if adj_matrix[i][j] == 1:
                # Check if either NPC is already engaged in a conversation
                already_in_convo = any(i in pair or j in pair for pair in conversations)
                if not already_in_convo:
                    conversations.append((i, j))

    return conversations

# Example usage
adj_matrix = [
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1],
    [0, 1, 1, 0]
]
adj_matrix = [
    [1, 0, 1, 1],
    [0, 1, 0, 0],
    [1, 0, 1, 1],
    [1, 0, 1, 1]
]
conversations = find_conversations(adj_matrix)
print(conversations)