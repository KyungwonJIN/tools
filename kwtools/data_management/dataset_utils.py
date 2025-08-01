import os
import json
import random
import shutil
import click
from pathlib import Path
from typing import List, Dict, Tuple
from tqdm import tqdm

def split_dataset(
    data_dir: str,
    output_dir: str,
    splits: Tuple[float, float, float] = (0.7, 0.2, 0.1),
    file_patterns: List[str] = ["*.jpg", "*.png"],
    seed: int = 42
):
    """
    데이터셋을 train/val/test로 분할
    
    Args:
        data_dir: 데이터 디렉토리
        output_dir: 출력 디렉토리
        splits: (train, val, test) 비율
        file_patterns: 이미지 파일 패턴 리스트
        seed: 랜덤 시드
    """
    random.seed(seed)
    
    # 모든 이미지 파일 수집
    data_path = Path(data_dir)
    files = []
    for pattern in file_patterns:
        files.extend(list(data_path.glob(pattern)))
    
    # 파일 랜덤 섞기
    random.shuffle(files)
    
    # 분할 인덱스 계산
    total = len(files)
    train_idx = int(total * splits[0])
    val_idx = train_idx + int(total * splits[1])
    
    # 분할된 파일 리스트
    train_files = files[:train_idx]
    val_files = files[train_idx:val_idx]
    test_files = files[val_idx:]
    
    # 파일 복사
    splits_dict = {
        'train': train_files,
        'val': val_files,
        'test': test_files
    }
    
    output_path = Path(output_dir)
    for split_name, split_files in splits_dict.items():
        split_dir = output_path / split_name
        split_dir.mkdir(parents=True, exist_ok=True)
        
        for file in tqdm(split_files, desc=f"Copying {split_name} files"):
            shutil.copy2(file, split_dir / file.name)

def convert_yolo_to_coco(
    yolo_dir: str,
    class_file: str,
    output_file: str,
    img_dir: str = None
):
    """
    YOLO 형식을 COCO 형식으로 변환
    
    Args:
        yolo_dir: YOLO 라벨 디렉토리
        class_file: 클래스 이름이 있는 파일
        output_file: 출력 COCO JSON 파일 경로
        img_dir: 이미지 디렉토리 (없으면 yolo_dir과 동일)
    """
    if img_dir is None:
        img_dir = yolo_dir
    
    # 클래스 정보 읽기
    with open(class_file, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    
    # COCO 형식 초기화
    coco_format = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    # 카테고리 정보 추가
    for idx, class_name in enumerate(classes):
        coco_format["categories"].append({
            "id": idx,
            "name": class_name,
            "supercategory": "none"
        })
    
    # 이미지와 어노테이션 정보 추가
    img_path = Path(img_dir)
    label_path = Path(yolo_dir)
    
    ann_id = 0
    for img_id, img_file in enumerate(tqdm(list(img_path.glob("*.jpg")))):
        # 이미지 정보
        coco_format["images"].append({
            "id": img_id,
            "file_name": img_file.name,
            "width": 0,  # TODO: 실제 이미지 크기 읽기
            "height": 0
        })
        
        # 라벨 파일 읽기
        label_file = label_path / f"{img_file.stem}.txt"
        if not label_file.exists():
            continue
        
        with open(label_file, 'r') as f:
            for line in f:
                class_id, x, y, w, h = map(float, line.strip().split())
                
                # YOLO to COCO 좌표 변환
                # TODO: 실제 변환 구현
                
                coco_format["annotations"].append({
                    "id": ann_id,
                    "image_id": img_id,
                    "category_id": int(class_id),
                    "bbox": [x, y, w, h],
                    "area": w * h,
                    "iscrowd": 0
                })
                ann_id += 1
    
    # COCO JSON 저장
    with open(output_file, 'w') as f:
        json.dump(coco_format, f, indent=2)

@click.group()
def cli():
    """데이터셋 관리 도구"""
    pass

@cli.command()
@click.argument('data_dir')
@click.argument('output_dir')
@click.option('--train', '-t', default=0.7, help='학습 데이터 비율')
@click.option('--val', '-v', default=0.2, help='검증 데이터 비율')
@click.option('--test', '-s', default=0.1, help='테스트 데이터 비율')
@click.option('--seed', default=42, help='랜덤 시드')
def split(data_dir, output_dir, train, val, test, seed):
    """데이터셋을 train/val/test로 분할합니다."""
    split_dataset(data_dir, output_dir, (train, val, test), seed=seed)

@cli.command()
@click.argument('yolo_dir')
@click.argument('class_file')
@click.argument('output_file')
@click.option('--img-dir', help='이미지 디렉토리 (옵션)')
def yolo2coco(yolo_dir, class_file, output_file, img_dir):
    """YOLO 형식을 COCO 형식으로 변환합니다."""
    convert_yolo_to_coco(yolo_dir, class_file, output_file, img_dir)

if __name__ == '__main__':
    cli()