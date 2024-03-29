import os
import asyncio
import pathlib
import shutil
import csv
import subprocess
from argparse import ArgumentParser

from model import Student
from utils import run_command, async_retry


DATA_DIR = pathlib.Path(os.path.abspath(__file__)).parent / 'data'
TEMPLATES_DIR = pathlib.Path(os.path.abspath(__file__)).parent / 'templates'


def load_students(section):
    data_path = DATA_DIR / f'{section}.csv'
    students = []
    with open(data_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(reader)
        for row in reader:
            if row[4] == '':
                print(f'Missing GitHub username for student {row[0]} - {row[1]} {row[2]} ({row[3]})')
            else:
                students.append(Student(smu_id=row[0], first_name=row[1], last_name=row[2], smu_email=row[3], github_username=row[4]))
    return students


def gen_folder_name(student):
    return f'{student.smu_id}_{student.first_name}-{student.last_name}'


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
    await asyncio.gather(*(
        download_repo(student, parent_path, gen_folder_name(student), assignment)
        for student in students))


def list_grade(section, assignment, students, path, template_filename='Grade.md'):
    parent_path = path / section / assignment
    assert parent_path.exists()
    for student in students:
        grade_file_path = parent_path / gen_folder_name(student) / template_filename
        with open(grade_file_path, 'r') as f:
            grade_line = f.readlines()[2]
            grade = grade_line.split(':')[-1].split('/')[0].strip()
            print(f'{student.smu_id} - {student.full_name} - {grade}')


def push_repo(section, assignment, path):
    parent_path = path / section / assignment
    assert parent_path.exists()
    for student_dir in parent_path.iterdir():
        if student_dir.is_dir():
            os.chdir(student_dir)
            subprocess.run(['git', 'add', '.'])
            subprocess.run(['git', 'commit', '-am', 'complete grading'])
            subprocess.run(['git', 'push'])


if __name__ == "__main__":
    parser = ArgumentParser(description='CS1342 TA Helper')
    parser.add_argument('-s', dest='section', type=str, help='the section name, ex: N11', required=True)
    parser.add_argument('-a', dest='assignment', type=str, help='the assignment name, ex: labquiz1', required=True)
    parser.add_argument('-p', dest='path', type=str, help='the path of clone repos, save to current path by default')
    parser.add_argument('-dl', dest='dl_repo', action="store_true", help='download repos')
    parser.add_argument('-ls', dest='list_grade', action="store_true", help='list grades for specific section')
    parser.add_argument('-up', dest='up_repo', action="store_true", help='push graded repos')
    args = parser.parse_args()
    if args.dl_repo:
        students = load_students(args.section)
        path = pathlib.Path(args.path) if args.path else pathlib.Path.cwd()
        asyncio.run(download_task(args.section, args.assignment, students, path))
    elif args.list_grade:
        students = load_students(args.section)
        path = pathlib.Path(args.path) if args.path else pathlib.Path.cwd()
        list_grade(args.section, args.assignment, students, path)
    elif args.up_repo:
        path = pathlib.Path(args.path) if args.path else pathlib.Path.cwd()
        push_repo(args.section, args.assignment, path)
    else:
        print('[Abort] missing action.')
