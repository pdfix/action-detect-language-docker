CONFIG_FILE: str = "config.json"
DOCKER_NAMESPACE: str = "pdfix"
DOCKER_REPOSITORY: str = "detect-language"
DOCKER_IMAGE: str = f"{DOCKER_NAMESPACE}/{DOCKER_REPOSITORY}"

# Language detection on shorter texts or with lower probability is not reliable
DETECTION_MIN_WORDS: int = 3
DETECTION_MIN_PROBABILITY: float = 0.9
# Language used when user and document do not provide any
FALLBACK_LANGUAGE: str = "en"
SDK_ERROR_INVALID_PASSWORD: int = 34  # PDFix SDK error type of OpenDoc with a missing or wrong password
