def chunkify_content(content, chunk_count, chunk_size=None):
    if chunk_size is None:
        chunk_size = int(len(content) / chunk_count)
    chunks = []
    last_boundary = 0

    for i in range(chunk_count):
        if i == chunk_count - 1:
            chunks.append(content[last_boundary:])
        else:
            chunks.append(content[last_boundary : last_boundary + chunk_size])

        last_boundary += chunk_size

    return chunks
