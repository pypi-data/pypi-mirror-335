from pathlib import Path

from airflow_integrations.file_system import FileSystem


def prepare_object(fs: FileSystem, remote_path: Path, local_path: Path):
    assert local_path.exists()
    with fs.open(remote_path, "wb") as remote_file:
        with local_path.open("rb") as local_file:
            remote_file.write(local_file.read())
