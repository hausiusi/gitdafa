import shutil
import subprocess
import sys
from pathlib import Path


def test_cli_ignores_directory_relative_to_launch_directory(tmp_path):
    source = Path(__file__).resolve().parents[1]
    tool = tmp_path / "gitdafa"
    tool.mkdir()
    for name in ("_cmd", "config", "git", "loc", "models"):
        shutil.copytree(source / name, tool / name)
    for name in ("census.py", "run.py"):
        shutil.copyfile(source / name, tool / name)

    target = tmp_path / "target"
    for directory, filename in (("assets", "omit.py"), ("assets-extra", "keep.py")):
        folder = target / directory
        folder.mkdir(parents=True)
        (folder / filename).write_text("pass\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com",
         "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "test"],
        cwd=target, check=True,
    )

    result = subprocess.run(
        [sys.executable, "run.py", "-pd", "../target", "-id",
         "..\\target\\assets\\", "-s", "loc"],
        cwd=tool, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert "keep.py" in result.stdout
    assert "omit.py" not in result.stdout
