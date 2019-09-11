import os
import pathlib
import csv

DATA_DIR = pathlib.Path(os.path.abspath(__file__)).parent / 'data'


def load_github():
    github_data_path = DATA_DIR / 'cs1342GitHubUsernames.csv'
    with open(github_data_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(reader)
        return {row[0]: row[1] for row in reader}


def prepare_section(section):
    github_data = load_github()
    section_data_path = DATA_DIR / f'cs1342_{section}.csv'
    output_path = DATA_DIR / f'{section}.csv'
    with open(section_data_path, 'r') as section_roster:
        reader = csv.reader(section_roster, delimiter=',')
        next(reader)
        with open(output_path, 'w') as final_csv:
            writer = csv.writer(final_csv)
            writer.writerow(['smu_id', 'first_name', 'last_name', 'smu_email', 'github_username'])
            for row in reader:
                first_name, last_name = row[0].split(',')
                github_user_name = github_data.get(row[2], '')
                writer.writerow((row[1], first_name, last_name, row[2], github_user_name))


if __name__ == "__main__":
    prepare_section('N12')
    prepare_section('N13')
