import pathlib
import tempfile
import git


class GitManager(object):
    STATUS_ADD = 'A'
    STATUS_MODIFY = 'M'
    STATUS_DELETE = 'D'
    STATUS_RENAME = 'R'
    STATUS_RENAME_FROM = 'RF'
    STATUS_RENAME_TO = 'RT'

    def __init__(self, git_path, projects_root_path):
        self.repo = git.Repo(git_path)
        self.projects_root_path = projects_root_path
        self.git = self.repo.git

    def git_pull(self):
        repo = self.repo
        repo.git.pull('origin', repo.active_branch)

    def git_commit(self, message, include_files_in_message=False):
        repo = self.repo
        index = repo.index
        index.add([self.projects_root_path])
        diff_message = repo.git.diff('--name-status', '--cached')
        if len(diff_message) == 0:
            return False
        else:
            if include_files_in_message:
                message = message + '\n' + diff_message
        index.commit(message)
        return True

    def git_push(self, raise_push_error=False, reset_on_error=False):
        repo = self.repo
        try:
            repo.git.push('--set-upstream', 'origin', repo.active_branch)
        except git.GitCommandError:
            if reset_on_error:
                repo.git.reset('origin/{}'.format(repo.active_branch), '--hard')
            if raise_push_error:
                raise
            return False
        return True

    def get_staged_files_dict(self, path, old_ref=None, new_ref=None):
        repo = self.repo
        if old_ref is None and new_ref is None:
            diff_message_list = repo.git.diff('--name-status', '--cached', path).split('\n')
        else:
            diff_message_list = repo.git.diff(old_ref, new_ref, '--name-status', path).split('\n')
        if diff_message_list == ['']:
            return {}
        diff_status_file_list = [i.split('\t') for i in diff_message_list]
        diff_status_file_dict_by_project = {}
        for status_file in diff_status_file_list:
            status = status_file[0]
            file_path = status_file[1]
            project = status_file[1].split('/')[-3]
            if self.STATUS_RENAME in status:
                file_path_add = status_file[2]
                if project in diff_status_file_dict_by_project:
                    diff_status_file_dict_by_project[project][file_path] = self.STATUS_RENAME_FROM
                    diff_status_file_dict_by_project[project][file_path_add] = self.STATUS_RENAME_TO
                else:
                    diff_status_file_dict_by_project[project] = {file_path: self.STATUS_RENAME_FROM,
                                                                 file_path_add: self.STATUS_RENAME_TO}
            else:
                if project in diff_status_file_dict_by_project:
                    diff_status_file_dict_by_project[project][file_path] = status
                else:
                    diff_status_file_dict_by_project[project] = {file_path: status}
        return diff_status_file_dict_by_project

    # def __get_ssk_key(self):
    #     repo = self.repo
    #     with pathlib.Path(SSH_KEY_PATH).open() as f:
    #         temp_file_kwargs = dict(mode='w', encoding='ascii')
    #         ssh_temp_file = tempfile.NamedTemporaryFile(**temp_file_kwargs)
    #         ssh_temp_file.write(f.read())
    #         ssh_temp_file.flush()
    #     repo.git.update_environment(GIT_SSH_COMMAND="ssh -i %s" % ssh_temp_file.name)
    #     return ssh_temp_file

    def get_latest_commit_ref(self):
        repo = self.repo
        return repo.git.log('-n1', '--format=format:%h')
