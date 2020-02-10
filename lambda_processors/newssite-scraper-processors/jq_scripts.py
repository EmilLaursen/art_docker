NON_EMPTY_FILEKEYS = """
    .Contents[]
        | select(.Size > 0)
        | .Key
        | select(endswith(".jsonl"))
"""

EMPTY_FILEKEYS = """
    .Contents[]
        | select(.Size == 0)
        | .Key
        | select(endswith(".jsonl"))
"""

DELETE_FILTER = """
    .ResponseMetadata  | {HTTPStatusCode, RetryAttempts}
"""