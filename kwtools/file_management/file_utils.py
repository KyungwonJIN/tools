import os
import click
import shutil
import hashlib
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Set
from collections import defaultdict

def copy_files_by_pattern(source_dir: str, target_dir: str, pattern: str, recursive: bool = False):
    """
    특정 패턴의 파일만 복사
    
    Args:
        source_dir: 원본 디렉토리
        target_dir: 대상 디렉토리
        pattern: 파일 패턴 (*.jpg, *.txt 등)
        recursive: 하위 디렉토리 포함 여부
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # 대상 디렉토리 생성
    target_path.mkdir(parents=True, exist_ok=True)
    
    if recursive:
        files = list(source_path.rglob(pattern))
    else:
        files = list(source_path.glob(pattern))
    
    for file in tqdm(files, desc="Copying files"):
        # 상대 경로 유지
        rel_path = file.relative_to(source_path)
        target_file = target_path / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target_file)

def get_file_hash(file_path: Path, block_size: int = 65536) -> str:
    """파일의 SHA-256 해시값 계산"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def find_duplicate_files(directory: str, recursive: bool = False) -> Dict[str, List[str]]:
    """
    중복 파일 찾기
    
    Returns:
        Dict[str, List[str]]: 해시값을 키로, 중복 파일 경로 리스트를 값으로 하는 딕셔너리
    """
    path = Path(directory)
    
    if recursive:
        files = list(path.rglob("*"))
    else:
        files = list(path.glob("*"))
    
    files = [f for f in files if f.is_file()]
    hash_dict = defaultdict(list)
    
    for file in tqdm(files, desc="Checking files"):
        file_hash = get_file_hash(file)
        hash_dict[file_hash].append(str(file))
    
    # 중복된 파일만 반환
    return {k: v for k, v in hash_dict.items() if len(v) > 1}

@click.group()
def cli():
    """파일 유틸리티 도구"""
    pass

@cli.command()
@click.argument('source_dir')
@click.argument('target_dir')
@click.argument('pattern')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
def copy(source_dir, target_dir, pattern, recursive):
    """특정 패턴의 파일만 복사합니다."""
    copy_files_by_pattern(source_dir, target_dir, pattern, recursive)

@cli.command()
@click.argument('directory')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
def find_duplicates(directory, recursive):
    """중복 파일을 찾아서 출력합니다."""
    duplicates = find_duplicate_files(directory, recursive)
    
    if not duplicates:
        click.echo("중복 파일이 없습니다.")
        return
    
    click.echo("\n=== 중복 파일 목록 ===")
    for hash_value, file_list in duplicates.items():
        click.echo(f"\n동일한 파일들 (hash: {hash_value[:8]}...):")
        for file_path in file_list:
            click.echo(f"  - {file_path}")

if __name__ == '__main__':
    cli()