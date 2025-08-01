import os
import click
import numpy as np
from PIL import Image
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List, Tuple
from collections import defaultdict

def analyze_images(directory: str, recursive: bool = False) -> Dict:
    """
    이미지 파일들의 통계 분석
    
    Returns:
        Dict: 이미지 통계 정보
    """
    path = Path(directory)
    
    if recursive:
        files = list(path.rglob("*.jpg")) + list(path.rglob("*.png"))
    else:
        files = list(path.glob("*.jpg")) + list(path.glob("*.png"))
    
    stats = {
        "total_images": len(files),
        "formats": defaultdict(int),
        "sizes": defaultdict(int),
        "resolutions": defaultdict(int),
        "aspect_ratios": defaultdict(int),
        "color_modes": defaultdict(int),
        "total_size_mb": 0
    }
    
    for file in tqdm(files, desc="Analyzing images"):
        # 파일 형식
        stats["formats"][file.suffix.lower()] += 1
        
        # 파일 크기
        size_mb = file.stat().st_size / (1024 * 1024)
        stats["total_size_mb"] += size_mb
        size_category = f"{int(size_mb)}MB" if size_mb >= 1 else f"{int(size_mb * 1024)}KB"
        stats["sizes"][size_category] += 1
        
        # 이미지 속성
        try:
            with Image.open(file) as img:
                width, height = img.size
                resolution = f"{width}x{height}"
                stats["resolutions"][resolution] += 1
                
                # 화면비
                ratio = width / height
                if ratio == 1:
                    aspect = "1:1"
                elif ratio > 1:
                    aspect = f"{ratio:.2f}:1"
                else:
                    aspect = f"1:{1/ratio:.2f}"
                stats["aspect_ratios"][aspect] += 1
                
                # 컬러 모드
                stats["color_modes"][img.mode] += 1
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    return stats

@click.group()
def cli():
    """이미지 분석 도구"""
    pass

@cli.command()
@click.argument('directory')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
def analyze(directory, recursive):
    """이미지 파일들의 통계를 분석합니다."""
    stats = analyze_images(directory, recursive)
    
    click.echo("\n=== 이미지 통계 ===")
    click.echo(f"\n총 이미지 수: {stats['total_images']}")
    click.echo(f"총 용량: {stats['total_size_mb']:.2f}MB")
    
    click.echo("\n파일 형식:")
    for fmt, count in stats["formats"].items():
        click.echo(f"  - {fmt}: {count}")
    
    click.echo("\n파일 크기 분포:")
    for size, count in sorted(stats["sizes"].items()):
        click.echo(f"  - {size}: {count}")
    
    click.echo("\n해상도 TOP 5:")
    for res, count in sorted(stats["resolutions"].items(), key=lambda x: x[1], reverse=True)[:5]:
        click.echo(f"  - {res}: {count}")
    
    click.echo("\n화면비 분포:")
    for ratio, count in stats["aspect_ratios"].items():
        click.echo(f"  - {ratio}: {count}")
    
    click.echo("\n컬러 모드:")
    for mode, count in stats["color_modes"].items():
        click.echo(f"  - {mode}: {count}")

if __name__ == '__main__':
    cli()