from .prepare import CodeSpectorDataPreparer
from .reviewer import CodeSpectorReviewer


class LocalCodespector:
    def __init__(
        self,
        chat_token: str,
        chat_agent: str,
        compare_branch: str,
        output_dir: str,
        system_content: str,
        chat_model: str,
    ):
        self.chat_token = chat_token
        self.chat_agent = chat_agent
        self.compare_branch = compare_branch
        self.output_dir = output_dir
        self.system_content = system_content
        self.chat_model = chat_model

        self.data_preparer = CodeSpectorDataPreparer(output_dir=self.output_dir, compare_branch=self.compare_branch)
        self.reviewer = CodeSpectorReviewer(
            diff_file=self.data_preparer.combined_file,
            chat_token=self.chat_token,
            chat_agent=self.chat_agent,
            system_content=self.system_content,
            output_dir=self.output_dir,
            chat_model=self.chat_model,
        )
        self.processes = [self.data_preparer, self.reviewer]

    def review(self):
        for process in self.processes:
            process.start()
