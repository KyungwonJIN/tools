import os
import click
from pathlib import Path
from tqdm import tqdm
import re

def batch_rename(directory: str, pattern: str, replacement: str, recursive: bool = False):
    """
    디렉토리 내의 파일들의 이름을 일괄 변경
    
    Args:
        directory: 대상 디렉토리
        pattern: 찾을 패턴 (정규식 사용 가능)
        replacement: 바꿀 텍스트
        recursive: 하위 디렉토리 포함 여부
    """
    path = Path(directory)
    
    if recursive:
        files = list(path.rglob("*"))
    else:
        files = list(path.glob("*"))
    
    # 파일만 선택 (디렉토리 제외)
    files = [f for f in files if f.is_file()]
    
    for file in tqdm(files, desc="Renaming files"):
        new_name = re.sub(pattern, replacement, file.name)
        if new_name != file.name:
            new_path = file.parent / new_name
            file.rename(new_path)

def add_prefix(directory: str, prefix: str, recursive: bool = False):
    """파일 이름 앞에 접두사 추가"""
    path = Path(directory)
    
    if recursive:
        files = list(path.rglob("*"))
    else:
        files = list(path.glob("*"))
    
    files = [f for f in files if f.is_file()]
    
    for file in tqdm(files, desc="Adding prefix"):
        new_name = f"{prefix}{file.name}"
        new_path = file.parent / new_name
        file.rename(new_path)

def add_suffix(directory: str, suffix: str, recursive: bool = False):
    """파일 확장자 앞에 접미사 추가"""
    path = Path(directory)
    
    if recursive:
        files = list(path.rglob("*"))
    else:
        files = list(path.glob("*"))
    
    files = [f for f in files if f.is_file()]
    
    for file in tqdm(files, desc="Adding suffix"):
        name = file.stem
        ext = file.suffix
        new_name = f"{name}{suffix}{ext}"
        new_path = file.parent / new_name
        file.rename(new_path)

@click.group()
def cli():
    """파일 이름 변경 도구"""
    pass

@cli.command()
@click.argument('directory')
@click.argument('pattern')
@click.argument('replacement')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
def rename(directory, pattern, replacement, recursive):
    """파일 이름을 패턴에 따라 일괄 변경합니다."""
    batch_rename(directory, pattern, replacement, recursive)

@cli.command()
@click.argument('directory')
@click.argument('prefix')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
def prefix(directory, prefix, recursive):
    """파일 이름 앞에 접두사를 추가합니다."""
    add_prefix(directory, prefix, recursive)

@cli.command()
@click.argument('directory')
@click.argument('suffix')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
def suffix(directory, suffix, recursive):
    """파일 확장자 앞에 접미사를 추가합니다."""
    add_suffix(directory, suffix, recursive)

if __name__ == '__main__':
    cli()