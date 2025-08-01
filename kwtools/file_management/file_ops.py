import os
import shutil
import click
from pathlib import Path
from tqdm import tqdm

def move_files(source_pattern: str, target_dir: str, recursive: bool = False):
    """
    주어진 패턴에 맞는 파일들을 대상 디렉토리로 이동
    
    Args:
        source_pattern: 이동할 파일 패턴 (예: "*.jpg", "data/*.txt")
        target_dir: 대상 디렉토리
        recursive: 하위 디렉토리도 검색할지 여부
    """
    source_path = Path(source_pattern)
    target_path = Path(target_dir)
    
    # 대상 디렉토리가 없으면 생성
    target_path.mkdir(parents=True, exist_ok=True)
    
    # 파일 찾기
    if recursive:
        files = list(source_path.parent.rglob(source_path.name))
    else:
        files = list(source_path.parent.glob(source_path.name))
    
    # 파일 이동
    for file in tqdm(files, desc="Moving files"):
        shutil.move(str(file), str(target_path / file.name))

@click.group()
def cli():
    """파일 관리 도구"""
    pass

@cli.command()
@click.argument('source')
@click.argument('target')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
def move(source, target, recursive):
    """파일을 이동합니다."""
    move_files(source, target, recursive)

if __name__ == '__main__':
    cli()