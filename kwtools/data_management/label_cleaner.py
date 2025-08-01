import os
import click
from pathlib import Path
from tqdm import tqdm

def remove_confidence(
    label_dir: str,
    recursive: bool = False,
    backup: bool = True,
    verbose: bool = False
) -> None:
    """
    YOLO 형식 라벨에서 confidence 값을 제거합니다.
    
    Args:
        label_dir: 라벨 파일이 있는 디렉토리
        recursive: 하위 디렉토리 포함 여부
        backup: 원본 파일 백업 여부
        verbose: 상세 정보 출력 여부
    """
    path = Path(label_dir)
    
    # 라벨 파일 찾기
    if recursive:
        label_files = list(path.rglob("*.txt"))
    else:
        label_files = list(path.glob("*.txt"))
    
    stats = {
        "total_files": len(label_files),
        "modified_files": 0,
        "error_files": []
    }
    
    for label_file in tqdm(label_files, desc="Cleaning labels"):
        try:
            modified = False
            cleaned_lines = []
            
            with open(label_file, 'r') as f:
                lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if not line:  # 빈 줄 건너뛰기
                        continue
                        
                    parts = line.split()
                    # confidence 값이 있는 경우 (6개 값)
                    if len(parts) == 6:
                        # class_id x y width height conf -> class_id x y width height
                        cleaned_line = ' '.join(parts[:5])
                        cleaned_lines.append(cleaned_line + '\n')
                        modified = True
                    else:
                        cleaned_lines.append(line + '\n')
            
            if modified:
                stats["modified_files"] += 1
                if backup:
                    # 백업 파일 생성
                    backup_file = label_file.with_suffix('.txt.bak')
                    if not backup_file.exists():  # 기존 백업 파일이 없을 경우에만
                        label_file.rename(backup_file)
                
                # 수정된 내용 저장
                with open(label_file, 'w') as f:
                    f.writelines(cleaned_lines)
                
                if verbose:
                    print(f"수정됨: {label_file}")
                    
        except Exception as e:
            stats["error_files"].append(str(label_file))
            if verbose:
                print(f"오류 발생: {label_file} - {str(e)}")
    
    return stats

@click.command()
@click.argument('label_dir')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
@click.option('--no-backup', is_flag=True, help='백업 파일을 생성하지 않음')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
def cli(label_dir, recursive, no_backup, verbose):
    """YOLO 형식 라벨에서 confidence 값을 제거합니다."""
    stats = remove_confidence(label_dir, recursive, not no_backup, verbose)
    
    click.echo("\n=== 처리 결과 ===")
    click.echo(f"총 파일 수: {stats['total_files']}")
    click.echo(f"수정된 파일 수: {stats['modified_files']}")
    
    if stats['error_files']:
        click.echo(f"\n처리 중 오류가 발생한 파일 수: {len(stats['error_files'])}")
        if verbose:
            click.echo("오류 파일 목록:")
            for file in stats['error_files']:
                click.echo(f"  - {file}")

if __name__ == '__main__':
    cli()