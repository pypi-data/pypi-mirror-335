import configparser
from typing import List
from git import Repo
import os
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor


from .ProgressBar import ClonedProgreeBar
from .Zipper import Zipper
from .Generator import Generator

from .Parsers import extract_git_links_xml, extract_git_links_json,extract_links_lineby_line

from .errors import SSH_key_not_set,Permission_Denied_SSH
import atexit
import pkg_resources
Shh_key_path=""
THREADS=2
class GitToMark:

    BASE_DIR = "./RepoStore"
    OUT_DIR = "./Output"
    
    def _cleanup(self):
        """Clean up Git resources properly"""
        for repo in self.repo:
            if repo and hasattr(repo.git, '_terminate'):
                repo.git._terminate()
        self.repo.clear()
    def __init__(self, urls: List["str"]|str,ssh=False) -> None:
        '''
        urls:List of git repo links
        ssh:Enable fetching from SSH requires setting the ssh key path in GitToMark Config 
        '''
        
        self.ssh=ssh
        if ssh:
            if not Shh_key_path:
                raise SSH_key_not_set
            x=subprocess.run(f'ssh -i "{Shh_key_path}" -T git@github.com',text=False)
            if x.returncode!=1:
                raise Permission_Denied_SSH
           



        if isinstance(urls,str):
            urls=[urls]
        self.urls = []
        self.repo = []
        self.UID = [self.extract_repo_name(url,ssh) for url in urls]
        atexit.register(self._cleanup)
        with ThreadPoolExecutor(THREADS) as DownloadPool:
            # self.repo=[self.Create_repo_Handle(url,i) for i,url in enumerate(self.urls)]
            for r in DownloadPool.map(
                lambda args: self.Create_repo_Handle(*args,ssh), enumerate(urls)
            ):
                if r:
                    self.repo.append(r)
    
    @classmethod
    def from_xml(cls, path):
        links = extract_git_links_xml(path)
        return cls(links)

    @classmethod 
    def from_file(cls,path):
        links=extract_links_lineby_line(path)
        return cls(links)
    @classmethod
    def from_json(cls, path):
        links = extract_git_links_json(path)
        return cls(links)
    @staticmethod
    def config(threads=10,ssh_path=""):
        global THREADS,Shh_key_path
        THREADS=threads
        Shh_key_path=ssh_path
    @property
    def store(self):
        Zipper(self.UID)

    def extract_repo_name(self, path,ssh):
        if not ssh:
            name = path.split("/")[-2:]
            name[1] = name[1][:-4]
            name.insert(1, "-")
            name = "".join(name)
            return name
        else:
            name=path.split(":")[1].split(".")[0].split("/")
            name.insert(1,"-")
            name="".join(name)
            return name

    @property
    def generate(self):
        with ThreadPoolExecutor(THREADS) as pool:
            i = 0
            for url, repo in zip(self.urls, self.repo):
                if self.ssh:
                    url=url.split(":")[1:]
                    url=''.join(url)

                Reponame = url.split("/")[-2:]
                Reponame[1] = Reponame[1][:-4]
                outfile = Reponame[1]
                Reponame.insert(1, "-")
                Reponame = "".join(Reponame)
                # pool.submit(Generator,(Reponame,repo,outfile))
                instance = Generator(Reponame, repo, outfile, i)

                    
                pool.submit(instance.Generate_MD)

                i += 1

    def Create_repo_Handle(self, i, url,ssh):
        handle = None
        try:
            if os.path.exists(self.BASE_DIR + f"/{self.UID[i]}"):
                self.urls.append(url)
                handle = Repo(self.BASE_DIR + f"/{self.UID[i]}")
            else:
                if not ssh:
                    if requests.get(url).status_code == 200:
                        handle = Repo.clone_from(
                            url,
                            self.BASE_DIR + f"/{self.UID[i]}",
                            progress=ClonedProgreeBar(i, self.UID[i]),
                        )
                        self.urls.append(url)
                    else:
                        print(f"Invalid Url:{url}")
                else:
                    handle = Repo.clone_from(
                        url,
                        self.BASE_DIR + f"/{self.UID[i]}",
                        progress=ClonedProgreeBar(i, self.UID[i]),
                        env={"GIT_SSH_COMMAND": f'ssh -i "{self.config["Default"]["Shh_key_path"]}"'}
                    )
                    self.urls.append(url)
            
            if handle:
                self.repo.append(handle)
            return handle
            
        except Exception as e:
            print(f"Error creating repo handle: {e}")
            return None