from git import Repo
from git import exc
import os

upstream_url = "https://github.com/flashbots/mev-geth.git"
main_branch = "master"

repo = Repo(os.getcwd())

repo.config_writer().set_value("user", "name", "devops").release()
repo.config_writer().set_value("user", "email", "devops@inc4.net").release()
repo.config_writer().set_value("checkout", "defaultRemote", "origin").release()

upstream = repo.create_remote("upstream", upstream_url)

upstream.fetch()

remote_origin_refs = repo.remote("origin").refs
remote_upstream_refs = repo.remote("upstream").refs

origin_branches = [branch.name.split('/', 1)[1] for branch in remote_origin_refs]
upstream_branches = [branch.name.split('/', 1)[1] for branch in remote_upstream_refs]

common_branches = [branch for branch in upstream_branches if branch in origin_branches]
new_branches = [branch for branch in upstream_branches if branch not in origin_branches]

print("Upstream branches: ", upstream_branches)
print("Origin branches: ", origin_branches)
print("New branches: ", new_branches)
print("Common branches: ", common_branches)

def merge_existing_branch(git, branch, main_branch):
    try:
        git.checkout(branch)
        git.rebase("--reapply-cherry-picks", "upstream/" + branch)
        git.push()
        git.checkout(main_branch)
    except exc.GitCommandError as err:
        print("*"*20 + "-MERGE CONFLICT-" + "*"*20)
        print(branch)
        print(err)
        git.rebase("--abort")
        # git.reset("--hard", "ORIG_HEAD")
        # git.merge("--abort")
    else:
        print("*"*20 + "-Successfuly merged " + branch + " branch-" + "*"*20)

def merge_non_existing_branch(git, branch, main_branch):
    try:
        git.checkout(main_branch)
        git.checkout('-b', branch)
        git.rebase("--reapply-cherry-picks", "upstream/" + branch)
        git.push("--set-upstream", "origin", branch)
        git.checkout(main_branch)
    except exc.GitCommandError as err:
        print("*"*20 + "-MERGE CONFLICT-" + "*"*20)
        print(branch)
        print(err)
        git.rebase("--abort")
        # git.reset("--hard", "ORIG_HEAD")
        
        # git.merge("--abort")
    else:
        print("*"*20 + "-Successfuly merged " + branch + " branch-" + "*"*20)


git = repo.git

print("*"*20 + "-Syncing common branches-" + "*"*20)
for branch in common_branches:
    merge_existing_branch(git, branch, main_branch)

print("*"*20 + "-Syncing new branches-" + "*"*20)
for branch in new_branches:
    merge_non_existing_branch(git, branch, main_branch)
