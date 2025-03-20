from sys import stdout
import os, platform
from git import Repo
from tqdm import tqdm
from .MarkdownUtils import Markdown
import pathlib
import os


class Generator:
    BASE_DIR = "./RepoStore"
    OUT_DIR = pathlib.Path("Output")

    def __init__(self, reponame: str, repo: Repo, outfile: str, i):
        self.out_dir = pathlib.Path(os.getcwd()) / self.OUT_DIR
        self.repoName = reponame
        self.repo = repo
        self.tree = repo.head.commit.tree
        self.MDout = str(self.out_dir / f"{reponame}.md")
        self.MD = Markdown(self.MDout)
        self.total = 0
        self.dirs = 0
        if  os.stat(self.OUT_DIR / f"{self.repoName}.md").st_size == 0:
            self.pbar = tqdm(
                position=i,
                desc=f"Processing:{reponame}",
                bar_format="{l_bar}{bar:50}| {n_fmt}/{total_fmt} [{elapsed}]",
            )
        # self.Generate_MD()

    def print_files_from_git(self, root, level=0):
        for entry in root:
            # print(f'{"-" * 4 * level}| {entry.path}, {entry.type}')
            self.total += 1

            tmp = f"{' ' * level * 2}- {entry.path}" + "\n"

            yield tmp
            if entry.type == "tree":
                self.dirs += 1
                yield from self.print_files_from_git(entry, level + 1)

    def write_files_in_MD(self, root, level=0):
        for entry in root:
            if entry.type == "tree":
                self.pbar.update(1)
                self.write_files_in_MD(entry, level + 1)
            else:
                self.pbar.update(1)
                self.MD.add_header(entry.path, 2)
                with open(
                    self.BASE_DIR + "/" + self.repoName + "/" + entry.path,
                    "r",
                    encoding="utf-8",
                ) as f:
                    x = entry.path.split(".")[-1]
                    if x.lower() != "md":
                        self.MD.add_code_block(f.read(), x)

    def __clear_stdout(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def write_git_tree(self):
        self.MD.add_header("Git Tree", 2)

        for line in self.print_files_from_git(self.tree):
            # stdout.write(f"\033[{self.i+1};1H")
            # stdout.write("\033[2K")
            # stdout.write(f"\rFiles:{self.total-self.dirs}|Dirs:{self.dirs}")
            # stdout.flush()
            # self.__clear_stdout()
            # pbar.total=self.total-self.dirs

            self.MD.add_para(
                line,
            )
        self.pbar.total = self.total

    def write_header(self):
        # split=self.urls.split('/')[-2:]
        # split.insert(1,"/")
        #
        # Headinfo=''.join(split)[:-4]
        self.MD.add_header(self.repoName.replace("-", "/"))

    def Generate_MD(self):
        if (
            os.path.exists(self.OUT_DIR / f"{self.repoName}.md")
            and os.stat(self.OUT_DIR / f"{self.repoName}.md").st_size != 0
        ):
            print(f"{self.repoName} Already Exists")
            return
        self.write_header()
        self.write_git_tree()

        self.write_files_in_MD(self.tree)

    def print_tree(self):
        self.print_files_from_git(self.tree)
