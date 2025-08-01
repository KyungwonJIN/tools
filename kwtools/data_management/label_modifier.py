import os
import json
import click
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List, Union

def modify_yolo_labels(
    label_dir: str,
    class_mapping: Dict[int, int],
    recursive: bool = False
) -> None:
    """
    YOLO 형식 라벨 파일의 클래스를 수정

    Args:
        label_dir: 라벨 파일이 있는 디렉토리
        class_mapping: {원본 클래스 ID: 새로운 클래스 ID} 형식의 매핑
        recursive: 하위 디렉토리 포함 여부
    """
    path = Path(label_dir)
    
    if recursive:
        label_files = list(path.rglob("*.txt"))
    else:
        label_files = list(path.glob("*.txt"))
    
    for label_file in tqdm(label_files, desc="Modifying YOLO labels"):
        # 파일 내용 읽기
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        modified_lines = []
        for line in lines:
            parts = line.strip().split()
            if not parts:  # 빈 줄 건너뛰기
                continue
                
            class_id = int(float(parts[0]))  # 첫 번째 값이 클래스 ID
            if class_id in class_mapping:
                # 클래스 ID 수정
                parts[0] = str(class_mapping[class_id])
                modified_lines.append(' '.join(parts) + '\n')
            else:
                modified_lines.append(line)
        
        # 수정된 내용 저장
        with open(label_file, 'w') as f:
            f.writelines(modified_lines)

def modify_coco_labels(
    json_file: str,
    class_mapping: Dict[int, Union[int, str]],
    output_file: str = None
) -> None:
    """
    COCO 형식 라벨 파일의 클래스를 수정

    Args:
        json_file: COCO 형식 JSON 파일 경로
        class_mapping: {원본 클래스 ID: 새로운 클래스 ID 또는 이름} 형식의 매핑
        output_file: 출력 파일 경로 (None이면 원본 파일 덮어쓰기)
    """
    if output_file is None:
        output_file = json_file
    
    # JSON 파일 읽기
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # 카테고리 수정
    id_to_new_id = {}  # 이전 ID와 새로운 ID 매핑
    for cat in data['categories']:
        old_id = cat['id']
        if old_id in class_mapping:
            new_value = class_mapping[old_id]
            if isinstance(new_value, str):
                # 클래스 이름만 변경
                cat['name'] = new_value
            else:
                # ID 변경 (및 선택적으로 이름도 변경)
                id_to_new_id[old_id] = new_value
                cat['id'] = new_value
                if isinstance(new_value, dict):
                    cat['name'] = new_value.get('name', cat['name'])
    
    # 어노테이션 수정
    if id_to_new_id:
        for ann in data['annotations']:
            old_id = ann['category_id']
            if old_id in id_to_new_id:
                ann['category_id'] = id_to_new_id[old_id]
    
    # 수정된 내용 저장
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

@click.command()
@click.argument('label_dir')
@click.argument('mapping_file')
@click.option('--recursive', '-r', is_flag=True, help='하위 디렉토리 포함')
@click.option('--format', '-f', type=click.Choice(['yolo', 'coco']), required=True, help='라벨 형식')
@click.option('--output', '-o', help='출력 파일 경로 (COCO 형식만 해당)')
def cli(label_dir, mapping_file, recursive, format, output):
    """라벨 클래스를 수정합니다.
    
    mapping_file은 JSON 형식으로 다음과 같이 작성:
    YOLO 형식: {"0": 1, "1": 2, ...}  # 이전 클래스 ID: 새로운 클래스 ID
    COCO 형식: {
        "1": 2,  # ID만 변경
        "2": {"id": 3, "name": "new_name"},  # ID와 이름 모두 변경
        "3": "new_name"  # 이름만 변경
    }
    """
    # 매핑 파일 읽기
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    # 문자열 키를 정수로 변환
    mapping = {int(k): v for k, v in mapping.items()}
    
    if format == 'yolo':
        # YOLO 형식은 모든 값이 정수여야 함
        mapping = {k: int(v) for k, v in mapping.items()}
        modify_yolo_labels(label_dir, mapping, recursive)
    else:  # coco
        if not output and not click.confirm('출력 파일이 지정되지 않아 원본 파일을 덮어쓰게 됩니다. 계속하시겠습니까?'):
            return
        modify_coco_labels(label_dir, mapping, output)
    
    click.echo("라벨 수정이 완료되었습니다.")

if __name__ == '__main__':
    cli()