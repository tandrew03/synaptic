# indicate which file types Synaptic can ingest from user.
ALLOWED_FILE_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp", "text/plain"}

# subset of allowed files types for easier accessing due to allowed
# file size being the same
IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

# declare the maximum allowed size for each file type
MAXIMUM_SIZE = {
    "application/pdf": 250 * 1024 * 1024,
    "image/jpeg": 25 * 1024 * 1024,
    "image/png": 25 * 1024 * 1024,
    "image/webp": 25 * 1024 * 1024,
    "text/plain": 5 * 1024 * 1024
}

# map document type to authority level
TYPE_LEVEL = {
    "user_note": 0,
    "supplemental_reading": 1,
    "lecture": 2,
    "textbook": 3,
    "exam": 4
}