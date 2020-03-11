#! /usr/bin/env python3
import requests
from notion.client import NotionClient
from config import *
import os
import time
import zipfile
import shutil
import git

if PROXY:
    os.environ['http_proxy'] = PROXY
    os.environ['https_proxy'] = PROXY

client = NotionClient(TOKEN)
page = client.search_blocks(PAGE)[0]


def get_task_status(task_id):
    payload = {
        'taskIds': [task_id],
    }
    r = client.post('getTasks', payload)
    result = r.json()['results'][0]
    return result['state'], result.get('status', None)


def wait_for_task(task_id):
    print('Exporting', end='')
    for i in range(20):
        print('.', end='')
        (state, status) = get_task_status(task_id)
        if state in ['not_started', 'in_progress']:
            time.sleep(1)
        elif state == 'success':
            print()
            return status
        else:
            raise Exception('Unexpected task state: {}'.format(state))
    else:
        raise Exception('Tired of waiting for the export task')


def get_exported_url(block_id):
    payload = {
        "task": {
            "eventName": "exportBlock",
            "request": {
                "blockId": block_id,
                "recursive": True,
                "exportOptions": {
                    "exportType": TYPE,
                    "timeZone": "Asia/Shanghai"
                }
            }
        }
    }
    r = client.post('enqueueTask', payload)
    task_id = r.json().get('taskId', None)
    if not task_id:
        raise Exception('Could not get the scheduled task id: {}'.format(r))

    result = wait_for_task(task_id)
    url = result.get('exportURL', None)
    if not url:
        raise Exception('Unexpected task result: {}'.format(result))
    return url


exported_url = get_exported_url(page.id)
print('Downloading...')
exported = requests.get(exported_url)

os.unsetenv('https_proxy')

with open('exported.zip', 'wb') as fp:
    fp.write(exported.content)

with zipfile.ZipFile('exported.zip', 'r') as zfp:
    zfp.extractall('exported')

if TYPE == 'markdown':
    shutil.copy(f'exported/{PAGE}.md', f'{LOCAL}/README.md')

if not os.path.isdir(LOCAL):
    print('Cloning...')
    git.Repo.clone_from(url=REMOTE, to_path=LOCAL)

repo = git.Repo(LOCAL)

for name in os.listdir(LOCAL):
    if name == '.git' or name in PRESERVED:
        continue
    file_path = os.path.join(LOCAL, name)
    if os.path.isfile(file_path):
        os.remove(file_path)
    elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    else:
        raise RuntimeError(f'What? {file_path}')

for src_dir, dirs, files in os.walk('exported'):
    dst_dir = src_dir.replace('exported', LOCAL, 1)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for file_ in files:
        src_file = os.path.join(src_dir, file_)
        dst_file = os.path.join(dst_dir, file_)
        if os.path.exists(dst_file):
            # in case of the src and dst are the same file
            if os.path.samefile(src_file, dst_file):
                continue
            os.remove(dst_file)
        shutil.move(src_file, dst_dir)

message = input('Type your commit message: ')

push = False

print('Committing...')
try:
    repo.git.add(A=True)
    if message == '':
        repo.git.commit('-m', f'{time.strftime("%Y-%m-%d %H:%M:%S")}')
    else:
        repo.git.commit('-m', f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {message}')
    push = True
except git.exc.GitCommandError:
    print('Nothing to commit')

if push:
    print('Pushing...')
    repo.remote().push()

print('Cleaning...')
shutil.rmtree('exported')
os.remove('exported.zip')

print('Done.')
