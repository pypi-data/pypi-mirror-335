import zipfile
from zipfile import ZipFile
import hashlib
#hello

class Zipper:
    OUT_DIR = "./Output"

    def __init__(self, reponame) -> None:
        self.reponames = reponame
        self.UID = hashlib.sha256(("".join(self.reponames)).encode("utf-8")).hexdigest()
        self.archive()

    def archive(self):
        with ZipFile(f"Zips/{self.UID}.zip", "w") as zfile:
            for entry in self.reponames:
                zfile.write(self.OUT_DIR + f"/{entry}.md", entry + ".md")
