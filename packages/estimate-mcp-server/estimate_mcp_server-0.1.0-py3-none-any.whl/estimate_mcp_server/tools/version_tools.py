from typing import Dict, Any, List
from datetime import datetime
from estimate_mcp_server.utils.firebase_client import get_document as get_estimate_data, update_document as update_estimate_data

def get_versions(address: str) -> List[Dict[str, Any]]:
    """견적서 버전 목록 조회"""
    try:
        estimate_data = get_estimate_data(address)
        if not estimate_data:
            return []

        versions = estimate_data.get("versions", [])
        return sorted(versions, key=lambda x: x.get("created_at", ""), reverse=True)

    except Exception as e:
        print(f"버전 목록 조회 중 오류 발생: {str(e)}")
        return []

def create_version(address: str, version_data: Dict[str, Any]) -> bool:
    """새 버전 생성"""
    try:
        estimate_data = get_estimate_data(address)
        if not estimate_data:
            return False

        # 버전 정보 생성
        version = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "name": version_data.get("name", "Untitled Version"),
            "created_at": datetime.now().isoformat(),
            "processes": estimate_data.get("processes", []),
            "total_amount": version_data.get("total_amount", 0)
        }

        # 기존 버전 목록에 추가
        versions = estimate_data.get("versions", [])
        versions.append(version)

        # 데이터 업데이트
        update_data = {
            "versions": versions
        }
        return update_estimate_data(address, update_data)

    except Exception as e:
        print(f"버전 생성 중 오류 발생: {str(e)}")
        return False

def compare_versions(address: str, version_id1: str, version_id2: str) -> Dict[str, Any]:
    """두 버전 비교"""
    try:
        estimate_data = get_estimate_data(address)
        if not estimate_data:
            return {"error": "견적서를 찾을 수 없습니다."}

        versions = estimate_data.get("versions", [])
        version1 = next((v for v in versions if v["id"] == version_id1), None)
        version2 = next((v for v in versions if v["id"] == version_id2), None)

        if not version1 or not version2:
            return {"error": "비교할 버전을 찾을 수 없습니다."}

        comparison = {
            "version1": version1["name"],
            "version2": version2["name"],
            "differences": []
        }

        # 공정별 비교
        processes1 = {p["name"]: p for p in version1["processes"]}
        processes2 = {p["name"]: p for p in version2["processes"]}

        # 추가/삭제된 공정 확인
        all_processes = set(processes1.keys()) | set(processes2.keys())
        for process_name in all_processes:
            if process_name not in processes1:
                comparison["differences"].append({
                    "type": "process_added",
                    "process": process_name
                })
            elif process_name not in processes2:
                comparison["differences"].append({
                    "type": "process_removed",
                    "process": process_name
                })
            else:
                # 항목 비교
                items1 = {i["id"]: i for i in processes1[process_name]["items"]}
                items2 = {i["id"]: i for i in processes2[process_name]["items"]}
                
                for item_id, item1 in items1.items():
                    if item_id not in items2:
                        comparison["differences"].append({
                            "type": "item_removed",
                            "process": process_name,
                            "item": item1["name"]
                        })
                    else:
                        item2 = items2[item_id]
                        if item1["quantity"] != item2["quantity"] or item1["unitPrice"] != item2["unitPrice"]:
                            comparison["differences"].append({
                                "type": "item_modified",
                                "process": process_name,
                                "item": item1["name"],
                                "changes": {
                                    "quantity": {
                                        "from": item1["quantity"],
                                        "to": item2["quantity"]
                                    },
                                    "unitPrice": {
                                        "from": item1["unitPrice"],
                                        "to": item2["unitPrice"]
                                    }
                                }
                            })

                for item_id, item2 in items2.items():
                    if item_id not in items1:
                        comparison["differences"].append({
                            "type": "item_added",
                            "process": process_name,
                            "item": item2["name"]
                        })

        return comparison

    except Exception as e:
        print(f"버전 비교 중 오류 발생: {str(e)}")
        return {"error": f"버전 비교 실패: {str(e)}"}

def _compare_items(items1: List[Dict[str, Any]], items2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    두 버전의 항목들을 비교합니다.
    """
    changes = {
        "added": [],
        "removed": [],
        "modified": []
    }
    
    items1_dict = {item["id"]: item for item in items1}
    items2_dict = {item["id"]: item for item in items2}
    
    # 추가된 항목
    for item_id, item in items2_dict.items():
        if item_id not in items1_dict:
            changes["added"].append(item)
    
    # 제거된 항목
    for item_id, item in items1_dict.items():
        if item_id not in items2_dict:
            changes["removed"].append(item)
    
    # 수정된 항목
    for item_id, item1 in items1_dict.items():
        if item_id in items2_dict:
            item2 = items2_dict[item_id]
            if item1 != item2:
                changes["modified"].append({
                    "before": item1,
                    "after": item2
                })
    
    return changes

def _compare_processes(processes1: List[Dict[str, Any]], processes2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    두 버전의 공정들을 비교합니다.
    """
    return _compare_items(processes1, processes2)

def _calculate_total_cost(data: Dict[str, Any]) -> float:
    """
    총 비용을 계산합니다.
    """
    items = data.get("items", [])
    return sum(item.get("cost", 0) for item in items) 