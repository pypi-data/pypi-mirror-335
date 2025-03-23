import pathlib

class FileTools:
    def get_file_content(self, file_path: str) -> str:
        mark_elements_script = pathlib.Path(file_path).read_text(encoding="utf-8")
        return mark_elements_script
                