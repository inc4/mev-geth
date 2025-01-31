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

dangling_branches = [branch for branch in origin_branches if branch not in upstream_branches]

print("Upstream branches: ", upstream_branches)
print("Origin branches: ", origin_branches)
print("New branches: ", new_branches)
print("Common branches: ", common_branches)
print("Dangling branches: ", dangling_branches)

def merge_existing_branch(git, branch, main_branch):
    try:
        git.checkout(branch)
        git.rebase("--reapply-cherry-picks", "-Xours", "upstream/" + branch)
        git.push("-f")
        git.checkout(main_branch)
    except exc.GitCommandError as err:
        print("*"*20 + "-MERGE CONFLICT-" + "*"*20)
        print(branch)
        print(err)
        git.rebase("--abort")
    else:
        print("*"*20 + "-Successfuly merged " + branch + " branch-" + "*"*20)

def merge_non_existing_branch(git, branch, main_branch):
    try:
        git.switch('-c', branch, "upstream/" + branch)
        git.push("-f", "--set-upstream", "origin", branch)
        git.checkout(main_branch)
    except exc.GitCommandError as err:
        print("*"*20 + "-MERGE CONFLICT-" + "*"*20)
        print(branch)
        print(err)
    else:
        print("*"*20 + "-Successfuly merged " + branch + " branch-" + "*"*20)

def delete_branch(git, branch):
    git.push("origin", "--delete", branch)

git = repo.git

print("\n" + "*"*20 + "-Syncing common branches-" + "*"*20)
for branch in common_branches:
    merge_existing_branch(git, branch, main_branch)

print("\n" + "*"*20 + "-Syncing new branches-" + "*"*20)
for branch in new_branches:
    merge_non_existing_branch(git, branch, main_branch)

print("\n" + "*"*20 + "-Deleting old dangling branches-" + "*"*20)
for branch in dangling_branches:
    delete_branch(git, branch)
