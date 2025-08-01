import os
import click
from pathlib import Path
from collections import Counter
from typing import Dict, Optional, Tuple
from tqdm import tqdm

def analyze_txt_labels(
    label_dir: str,
    class_names_file: Optional[str] = None,
    recursive: bool = False,
    verbose: bool = False
) -> Tuple[Dict, Dict]:
    """
    YOLO 형식의 txt 라벨 파일들을 분석

    Args:
        label_dir: 라벨 파일이 있는 디렉토리
        class_names_file: 클래스 이름이 있는 파일 (옵션)
        recursive: 하위 디렉토리 포함 여부
        verbose: 상세 정보 출력 여부

    Returns:
        Tuple[Dict, Dict]: (기본 통계, 클래스별 통계)
    """
    path = Path(label_dir)
    
    # 클래스 이름 로드 (있는 경우)
    class_names = {}
    if class_names_file:
        with open(class_names_file, 'r') as f:
            for idx, line in enumerate(f):
                class_names[idx] = line.strip()
    
    # 라벨 파일 찾기
    if recursive:
        label_files = list(path.rglob("*.txt"))
    else:
        label_files = list(path.glob("*.txt"))
    
    # 통계 초기화
    stats = {
        "total_files": len(label_files),
        "empty_files": 0,
        "no_object_files": 0,  # 객체가 없는 파일 수
        "total_objects": 0,
        "error_files": []  # 에러가 발생한 파일 목록
    }
    
    class_stats = {}  # class_id -> {"count": int, "files": int}
    
    # 파일 분석
    for label_file in tqdm(label_files, desc="Analyzing labels"):
        classes_in_file = set()
        objects_in_file = 0
        
        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()
                
                if not lines:
                    stats["empty_files"] += 1
                    if verbose:
                        print(f"빈 파일: {label_file}")
                    continue
                
                valid_lines = 0
                for line in lines:
                    line = line.strip()
                    if not line:  # 빈 줄 건너뛰기
                        continue
                        
                    parts = line.split()
                    if len(parts) != 5:  # YOLO 형식: class_id x y width height
                        if verbose:
                            print(f"잘못된 형식의 라인 ({len(parts)} values): {label_file} - {line}")
                        continue
                    
                    try:
                        class_id = int(float(parts[0]))
                        
                        # 클래스별 통계 초기화 (필요한 경우)
                        if class_id not in class_stats:
                            class_stats[class_id] = {"count": 0, "files": 0}
                        
                        # 클래스별 객체 수 증가
                        class_stats[class_id]["count"] += 1
                        objects_in_file += 1
                        classes_in_file.add(class_id)
                        valid_lines += 1
                        
                    except ValueError as e:
                        if verbose:
                            print(f"클래스 ID 변환 오류: {label_file} - {line}")
                        continue
                
                if valid_lines == 0:
                    stats["no_object_files"] += 1
                    if verbose:
                        print(f"유효한 객체가 없는 파일: {label_file}")
                
                stats["total_objects"] += objects_in_file
                
                # 클래스별 파일 수 업데이트
                for class_id in classes_in_file:
                    class_stats[class_id]["files"] += 1
                    
        except Exception as e:
            stats["error_files"].append(str(label_file))
            if verbose:
                print(f"파일 처리 오류: {label_file} - {str(e)}")
    
    return stats, class_stats

@click.group()
def cli():
    """라벨 분석 도구"""
    pass

@cli.command()
@click.argument('label_dir')
@click.option('--names', '-n', help='클래스 이름 파일 경로')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
def analyze(label_dir, names, recursive, verbose):
    """YOLO 형식의 txt 라벨 파일들을 분석합니다."""
    stats, class_stats = analyze_txt_labels(label_dir, names, recursive, verbose)
    
    click.echo("\n=== 기본 통계 ===")
    click.echo(f"총 파일 수: {stats['total_files']}")
    click.echo(f"빈 파일 수: {stats['empty_files']}")
    click.echo(f"객체가 없는 파일 수: {stats['no_object_files']}")
    click.echo(f"총 객체 수: {stats['total_objects']}")
    
    if stats['error_files']:
        click.echo(f"\n처리 중 오류가 발생한 파일 수: {len(stats['error_files'])}")
        if verbose:
            click.echo("오류 파일 목록:")
            for file in stats['error_files']:
                click.echo(f"  - {file}")
    
    click.echo("\n=== 클래스별 통계 ===")
    for class_id, class_stat in sorted(class_stats.items()):
        class_name = f"(class {class_id})"
        if names:  # 클래스 이름이 있는 경우
            try:
                with open(names, 'r') as f:
                    lines = f.readlines()
                    if 0 <= class_id < len(lines):
                        class_name = lines[class_id].strip()
            except Exception:
                pass
        
        click.echo(f"\n클래스 {class_id} {class_name}:")
        click.echo(f"  총 객체 수: {class_stat['count']}")
        click.echo(f"  등장한 파일 수: {class_stat['files']}")

if __name__ == '__main__':
    cli()