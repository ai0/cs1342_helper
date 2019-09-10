import os
import asyncio
import pathlib
import shutil
from argparse import ArgumentParser

from model import Student
from utils import run_command, async_retry


DATA_DIR = pathlib.Path(os.path.abspath(__file__)).parent / 'data'
TEMPLATES_DIR = pathlib.Path(os.path.abspath(__file__)).parent / 'templates'


def load_students(section):
    return [Student(first_name='tf', last_name='boy', smu_id='888', smu_email='x@smu.edu', github_username='47724564')]


@async_retry(tries=2)
async def download_repo(student, parent_path, folder_name, assignment, template_filename='Grade.md'):
    output_path = parent_path / folder_name
    assert not output_path.exists()
    github_uri = f'git@github.com:SouthernMethodistUniversity/{assignment}-{student.github_username}.git'
    await run_command('git', 'clone', github_uri, str(output_path), '--quiet')
    assert output_path.exists()
    shutil.copy(str(TEMPLATES_DIR / template_filename), str(output_path / template_filename))
    assert (output_path / template_filename).exists()


async def download_task(section, assignment, students, path):
    parent_path = path / section / assignment
    if not parent_path.exists():
        parent_path.mkdir(parents=True)

    def gen_folder_name(student):
        return f'{student.smu_id}_{student.first_name}-{student.last_name}'

    await asyncio.gather(*(
        download_repo(student, parent_path, gen_folder_name(student), assignment)
        for student in students))


if __name__ == "__main__":
    parser = ArgumentParser(description='CS1342 TA Helper')
    parser.add_argument('-s', dest='section', type=str, help='the section name, ex: N11', required=True)
    parser.add_argument('-a', dest='assignment', type=str, help='the assignment name, ex: labquiz1', required=True)
    parser.add_argument('-p', dest='path', type=str, help='the path of clone repos, save to current path by default')
    parser.add_argument('-dl', dest='dl_repo', action="store_true", help='download repos')
    parser.add_argument('-up', dest='up_repo', action="store_true", help='push graded repos')
    args = parser.parse_args()
    if args.dl_repo:
        students = load_students(args.section)
        path = pathlib.Path(args.path) if args.path else pathlib.Path.cwd()
        asyncio.run(download_task(args.section, args.assignment, students, path))
    elif args.up_repo:
        pass
