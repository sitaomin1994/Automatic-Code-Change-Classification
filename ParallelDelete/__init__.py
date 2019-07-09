import threading
import os


class ParallelDelete(threading.Thread):
    def __init__(self, pwd, prev_dirs, curr_dirs):
        threading.Thread.__init__(self)
        self.pwd = pwd
        self.prev_dirs = prev_dirs
        self.curr_dirs = curr_dirs

    def run(self):
        file_paths = []  # list of file paths to delete

        # java paths
        for new_prev_ext, new_curr_ext in zip(self.prev_dirs.values(), self.curr_dirs.values()):
            file_paths.append(new_prev_ext.split(".java")[0])
            file_paths.append(new_curr_ext.split(".java")[0])

        # gumtree paths
        for new_prev_ext in self.prev_dirs.values():
            file_paths.append(new_prev_ext.split("_prev")[0] + "_cluster.txt")
            file_paths.append(new_prev_ext.split("_prev")[0] + "_diff.txt")
        for file_path in file_paths:
            if os.path.isfile(file_path):
                self.remove_file(file_path)
        return

    def remove_file(self, file_path):
        os.remove(file_path)