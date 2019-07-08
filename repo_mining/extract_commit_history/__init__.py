from git import Repo
import os
import subprocess
import re
import json
import time
from os import path
import aiofiles as aiof 
import asyncio
# Title: Extracting Commit History
# Perquisites: Ensure that gumtree is installed - https://github.com/GumTreeDiff/gumtree/releases and
#              added to system path:
#                                    - nanon ~/.bashrc
#                                    - export PATH=$PATH:/*/gumtree*/bin


class ExtractHistory:
    def __init__(self, application, csha):
        self.application = application
        self.csha = csha
        self.git_ext = "https://github.com/"
        self.flag_dict = {"build": "False", "maintenance": "False", "testing": "False"}
        self.total_files = 0
        self.deleted_files = 0

    def parse_application(self, application_name):
        organization = application_name.split("-", 1)[0]
        project = application_name.split("-", 1)[1]
        return organization, project

    def clone_repo(self, repo_url, repo_dir):
        cloned_repo = Repo.clone_from(repo_url, repo_dir)
        assert cloned_repo.__class__ is Repo
        return cloned_repo

    def parse_filename(self, file_path):
        filename = file_path.split("/")[-1]
        return filename

    def create_javaFiles(self, pwd, prev_commit_dict, curr_commit_dict):
        prev_dirs = dict()
        curr_dirs = dict()
        for old_ext in prev_commit_dict.keys():
            filename = old_ext
            old_ext = self.parse_filename(old_ext)
            prev_dirs[filename] = pwd + "/" + old_ext.split(".")[0] + "_prev.java"
            curr_dirs[filename] = pwd + "/" + old_ext.split(".")[0] + "_curr.java"

        for old_ext, new_ext in prev_dirs.items():
            if not path.exists(new_ext):  # create .java files
                with open(new_ext, "w") as java:
                    java.write(prev_commit_dict[old_ext])

        for old_ext, new_ext in curr_dirs.items():
            if not path.exists(new_ext):
                with open(new_ext, "w") as java:
                    java.write(curr_commit_dict[old_ext])
        return prev_dirs, curr_dirs

    def is_FileDeleted(self, commit, paths):

        current_files = []
        for file in commit.tree.traverse():
            current_files.append(file.path)

        if paths not in current_files:
            self.deleted_files = self.deleted_files + 1
            return True
        else:
            return False

    def delete_tmpFiles(self, pwd, prev_dirs, curr_dirs):

        # Delete java files
        for new_prev_ext, new_curr_ext in zip(prev_dirs.values(), curr_dirs.values()):
            rm_prev = new_prev_ext.split(".java")[0]
            rm_curr = new_curr_ext.split(".java")[0]
            cmd = ["rm", rm_prev + ".java"]
            cmd2 = ["rm", rm_curr + ".java"]
            subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
            time.sleep(2)
            subprocess.Popen(cmd2, stdout=subprocess.PIPE).communicate()[0]

        # Delete txt files
        for new_prev_ext in prev_dirs.values():
            rm_cluster = new_prev_ext.split("_prev")[0] + "_cluster.txt"
            rm_diff = new_prev_ext.split("_prev")[0] + "_diff.txt"
            cmd = ["rm", rm_cluster]
            cmd2 = ["rm", rm_diff]
            subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
            time.sleep(2)
            subprocess.Popen(cmd2, stdout=subprocess.PIPE).communicate()[0]

        # check if all files were deleted
        rw_files = os.listdir(pwd)
        for new_prev_ext, new_curr_ext in zip(prev_dirs.values(), curr_dirs.values()):
            if new_prev_ext in rw_files or new_curr_ext in rw_files:
                print("Problem deleting files" + new_prev_ext + " and " + new_curr_ext + "in working directory")

    def parse_diff(self, diff_content):

        diff_list = diff_content.split('\n')

        # remove 'Match'
        diff_list_new = []
        for line in diff_list:
            if 'Match' in line or line == '':
                continue
            diff_list_new.append(line)

        return diff_list_new

    def parse_clusters(self, cluster_content):

        clusters = cluster_content.split('New cluster:\n')
        roots = []
        operations = []

        for item in clusters:
            if item == '':
                continue
            else:
                cluster = item.split('------------\n')
                roots.append(cluster[0].strip('\n'))
                sub_operations = []
                for ele in cluster[1].strip('\n').split('\n'):
                    sub_operations.append(ele)
                operations.append(sub_operations)
        return roots, operations

    async def write_JSON(self, prev_dirs, curr_dirs):

        # compute gumtree cluster and diff and store values in .txt files
        for prev_java, curr_java in zip(prev_dirs.values(), curr_dirs.values()):
            prev_file = self.parse_filename(prev_java)
            curr_file = self.parse_filename(curr_java)
            cmd_cluster = ["gumtree", "cluster", prev_file, curr_file]
            cmd_diff = ["gumtree", "diff", prev_file, curr_file]

            output = subprocess.Popen(cmd_cluster, stdout=subprocess.PIPE).communicate()[0]
            cluster_file = curr_file.split("_")[0] + "_cluster.txt"
            if not path.exists(cluster_file):
                async with aiof.open(cluster_file, "wb") as f:
                    await f.write(output)
            

            output = subprocess.Popen(cmd_diff, stdout=subprocess.PIPE).communicate()[0]
            diff_file = curr_file.split("_")[0] + "_diff.txt"
            if not path.exists(diff_file):
                async with aiof.open(diff_file, "wb") as f:
                    await f.write(output)


        # create json object
        data = {}
        data["application"] = self.application
        data["csha"] = self.csha
        data["files"] = []
        data["commit_stats"] = []
        data["commit_stats"].append({
            "total_files": self.total_files,
            "deleted_files": self.deleted_files,
            "testing": self.flag_dict["testing"],
            "maintenance": self.flag_dict["maintenance"],
            "build": self.flag_dict["build"]
        })
        for prev_file in prev_dirs.values():
            prev_file = prev_file.split(".")[0] + ".txt"
            with open(prev_file.split("/")[-1].split("_")[0] + "_cluster.txt", "r") as cluster:

                # get roots and operations
                cluster_content = cluster.read()
                roots, operations = self.parse_clusters(cluster_content)

                # creat actions for json key
                actions = {}
                actions['actions'] = []

                for root, operation in zip(roots, operations):
                    new_cluster = {}
                    new_cluster['root'] = root  # new cluster operation
                    new_cluster['operations'] = operation  # operations inside new cluster
                    actions['actions'].append(new_cluster)

                # append actions to json
                data["files"].append({
                    self.parse_filename(prev_file).split("_")[0] + "_cluster": actions
                })

            with open(prev_file.split("/")[-1].split("_")[0] + "_diff.txt", "r") as diff:
                diff_content = diff.read()
                # operation_list = []
                operation_list = self.parse_diff(diff_content)

                # create operations from text
                operations = {}
                operations['operations'] = operation_list

                # append operations to json
                data["files"].append({
                    self.parse_filename(prev_file).split("_")[0] + "_diff": operations
                })
        # make temp folder to store JSON
        pwd = os.getcwd()
        json_dir = pwd + "/tmp_JSON"
        if not path.exists(json_dir):
            cmd = ["mkdir", json_dir]
            subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

        # store json files in tmp folder
        json_path = json_dir + "/" + self.application + "_" + self.csha + ".json"
        data_json = json.dumps(data, ensure_ascii=False)
        if not path.exists(json_path):
            async with aiof.open(json_path, "w") as f:
                await f.write(data_json)
                
                
        
        return json_path

    def delete_JSON(self, pwd):
        cmd = ["rm", pwd + self.csha + ".json"]
        subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

    async def clone(self):
        # make directory folder
        pwd = os.getcwd()

        all_files = pwd + "/repos"
        cmd = ["mkdir", all_files]
        if not path.exists(all_files):
            subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

        repo_dir = all_files + "/" + self.application
        cmd = ["mkdir", repo_dir]
        if not path.exists(repo_dir):
            subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

        # clone project into directory if not empty
        if len(os.listdir(repo_dir)) == 0:
            organization, project = self.parse_application(self.application)
            repo_url = self.git_ext + organization + "/" + project
            cloned_repo = self.clone_repo(repo_url, repo_dir)

        # set repo as current working repository
        cloned_repo = Repo(repo_dir)

        # set sha as current branch and obtain modified files
        curr_commit = cloned_repo.commit(self.csha)
        curr_content = dict()
        current_files = []
        main_java_files = []
        all_files = []

        build_reg = r"^.*(build|pom).*\.(xml|gradle.*)$"
        util_reg = r"^.*([u|U]til|[h|H]elper).*"
        test_reg = r".*[tT]est.*"
        for file in curr_commit.stats.files.keys():
            all_files.append(file)
            if re.match(build_reg, str(file)):
                self.flag_dict["build"] = "True"
            if re.match(util_reg, str(file)):
                self.flag_dict["maintenance"] = "True"
            if re.match(test_reg, str(file)):
                self.flag_dict["testing"] = "True"
            if re.match(r"^.*\.java$", str(file)) and not(re.match(util_reg, str(file)) or re.match(test_reg, str(file))):
                main_java_files.append(file)
        self.total_files = len(all_files)

        for file in all_files:
            if self.is_FileDeleted(curr_commit, file) and file in main_java_files:
                curr_content[file] = " "
                current_files.append(file)
            else:
                if file in main_java_files:
                    curr_content[file] = cloned_repo.git.show("%s:%s" % (curr_commit, file))
                    current_files.append(file)
        # set sha as parent branch and traverse subtree to obtain modified files
        prev_content = dict()
        if curr_commit.parents:
            prev_commit = curr_commit.parents[0]
            prev_commit = cloned_repo.commit(prev_commit)
            prev_commit_t = prev_commit.tree

            for file in prev_commit_t.traverse():
                if file.path in current_files:
                    prev_content[file.path] = cloned_repo.git.show("%s:%s" % (prev_commit, file.path))
        else:
            for file in current_files:
                prev_content[""+file] = " "

        # create temporary java files and gumtree statistics
        prev_dirs, curr_dirs = self.create_javaFiles(pwd, prev_content, curr_content)

        # create JSON obj
        json_path = await self.write_JSON(prev_dirs, curr_dirs)

        with open(json_path) as f:
            data = json.load(f)

        # silently delete java files and text files
        self.delete_tmpFiles(pwd, prev_dirs, curr_dirs)

        print("finished mining repository...{}: {}".format(self.application, self.csha))
    
        return data

    def get_flags(self):
        return self.flag_dict


