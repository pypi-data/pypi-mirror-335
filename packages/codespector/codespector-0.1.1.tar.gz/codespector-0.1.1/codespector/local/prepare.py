import ujson
import subprocess
import os


class CodeSpectorDataPreparer:
    def __init__(
        self,
        output_dir: str,
        compare_branch: str,
    ):
        self.output_dir = output_dir
        self.compare_branch = compare_branch

        self.original_files_tmp = 'original_files_tmp.json'
        self.code_changes_only = 'code_changes_only.txt'
        self.diff_file = 'diff.json'
        self.combined_file = 'combined.json'

    def _prepare_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _prepare_diff_file(self):
        diff_output = subprocess.run(['git', 'diff', self.compare_branch], stdout=subprocess.PIPE, text=True).stdout

        filtered_diff = [
            line
            for line in diff_output.splitlines()
            if (line.startswith('+') or line.startswith('-'))
            and not line.startswith('+++')
            and not line.startswith('---')
        ]

        with open(os.path.join(self.output_dir, self.code_changes_only), 'w', encoding='utf-8') as f:
            f.write('\n'.join(filtered_diff))

        diff_json = {'diff': '\n'.join(filtered_diff)}
        diff_filepath = os.path.join(self.output_dir, self.diff_file)
        with open(diff_filepath, 'w', encoding='utf-8') as f:
            ujson.dump(diff_json, f, indent=4, ensure_ascii=False)

        with open(os.path.join(self.output_dir, self.original_files_tmp), 'r', encoding='utf-8') as f:
            original_files_data = ujson.load(f)

        with open(diff_filepath, 'r', encoding='utf-8') as f:
            diff_data = ujson.load(f)

        combined_data = {**original_files_data, **diff_data}

        with open(os.path.join(self.output_dir, self.combined_file), 'w', encoding='utf-8') as f:
            ujson.dump(combined_data, f, indent=4, ensure_ascii=False)

    def _prepare_name_only_file(self):
        changed_files = subprocess.run(
            ['git', 'diff', '--name-only', self.compare_branch], stdout=subprocess.PIPE, text=True
        ).stdout.splitlines()

        result = {'original files': []}

        for file in changed_files:
            if not file.endswith('.py'):
                continue

            if os.path.isfile(file):
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                result['original files'].append({'filename': file, 'content': content})

        filepath = os.path.join(self.output_dir, self.original_files_tmp)

        with open(filepath, 'w', encoding='utf-8') as f:
            ujson.dump(result, f, indent=4, ensure_ascii=False)

    def prepare_data(self) -> str:
        self._prepare_dir()
        self._prepare_name_only_file()
        self._prepare_diff_file()

    def start(self):
        self.prepare_data()
