import hashlib
import json


class Hasher:
    def __init__(self, path: str):
        self._path = path
        try:
            with open(path, mode="rt", encoding="utf-8") as f:
                self._hashes = json.load(f)
        except FileNotFoundError:
            self._hashes = {}

    def update_hash(self, filepath: str, new_hash: str) -> None:
        """Update hash value for this filepath in the datafile"""
        self._hashes[filepath] = new_hash
        self._save()

    def has_changed(self, filepath: str, curr_hash: str) -> bool:
        """Check if the hash of this file changed. Returns True if file doesn't have previous hash value"""
        try:
            return self._hashes[filepath] != curr_hash
        except KeyError:
            return True

    def reset_hashes(self) -> None:
        """Remove all hashes from the file"""
        self._hashes = {}
        self._save()

    def _save(self) -> None:
        with open(self._path, mode="wt", encoding="utf-8") as f:
            json.dump(self._hashes, f)

    @staticmethod
    def calculate_hash(filepath: str) -> str:
        """Calculate MD5 hash for the file"""
        with open(filepath, mode="rt", encoding="utf-8") as f:
            encoded_text = f.read().encode("utf-8")
        return hashlib.md5(encoded_text).hexdigest()
