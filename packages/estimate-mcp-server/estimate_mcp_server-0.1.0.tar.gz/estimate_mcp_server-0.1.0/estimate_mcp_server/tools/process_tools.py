from typing import Dict, Any, List
from datetime import datetime

def analyze_processes(estimate_data: Dict[str, Any]) -> Dict[str, Any]:
    """공정 데이터 분석"""
    try:
        analysis = {
            "process_details": [],
            "total_processes": 0,
            "total_items": 0,
            "process_statistics": {
                "highest_cost_process": None,
                "lowest_cost_process": None,
                "avg_process_cost": 0,
                "cost_distribution": []
            },
            "workflow_analysis": {
                "process_dependencies": [],
                "critical_processes": [],
                "optimization_suggestions": []
            },
            "suggestions": []
        }

        processes = estimate_data.get("processes", [])
        analysis["total_processes"] = len(processes)
        total_cost = 0

        # 공정별 상세 분석
        for process in processes:
            items = process.get("items", [])
            process_detail = {
                "name": process.get("name", ""),
                "item_count": len(items),
                "total_amount": 0,
                "avg_unit_price": 0,
                "has_notes": False,
                "item_categories": {},
                "cost_factors": []
            }

            # 항목 분석
            total_unit_price = 0
            for item in items:
                quantity = float(item.get("quantity", 0))
                unit_price = float(item.get("unitPrice", 0))
                amount = quantity * unit_price
                process_detail["total_amount"] += amount
                total_unit_price += unit_price

                # 비고 확인
                if item.get("note"):
                    process_detail["has_notes"] = True

                # 항목 카테고리 분류
                category = item.get("category", "기타")
                if category not in process_detail["item_categories"]:
                    process_detail["item_categories"][category] = {
                        "count": 0,
                        "total_amount": 0
                    }
                process_detail["item_categories"][category]["count"] += 1
                process_detail["item_categories"][category]["total_amount"] += amount

                # 비용 요인 분석
                if amount > process_detail["total_amount"] * 0.2:  # 20% 이상 차지하는 항목
                    process_detail["cost_factors"].append({
                        "item_name": item.get("name", ""),
                        "amount": amount,
                        "percentage": (amount / process_detail["total_amount"]) * 100
                    })

            # 평균 단가 계산
            if items:
                process_detail["avg_unit_price"] = total_unit_price / len(items)

            analysis["process_details"].append(process_detail)
            analysis["total_items"] += process_detail["item_count"]
            total_cost += process_detail["total_amount"]

        # 통계 분석
        if analysis["process_details"]:
            sorted_by_cost = sorted(
                analysis["process_details"], 
                key=lambda x: x["total_amount"]
            )
            analysis["process_statistics"]["highest_cost_process"] = sorted_by_cost[-1]
            analysis["process_statistics"]["lowest_cost_process"] = sorted_by_cost[0]
            analysis["process_statistics"]["avg_process_cost"] = total_cost / len(processes)
            
            # 비용 분포 계산
            for process in analysis["process_details"]:
                analysis["process_statistics"]["cost_distribution"].append({
                    "process_name": process["name"],
                    "percentage": (process["total_amount"] / total_cost) * 100
                })

        # 워크플로우 분석
        for i, process in enumerate(processes):
            if i > 0:
                analysis["workflow_analysis"]["process_dependencies"].append({
                    "from": processes[i-1]["name"],
                    "to": process["name"]
                })

            # 중요 공정 식별 (전체 비용의 20% 이상)
            if process["total_amount"] > total_cost * 0.2:
                analysis["workflow_analysis"]["critical_processes"].append(process["name"])

        # 개선 제안 생성
        if analysis["total_processes"] < 3:
            analysis["suggestions"].append("공정이 너무 적습니다. 누락된 공정이 없는지 확인해보세요.")

        for process_detail in analysis["process_details"]:
            if process_detail["item_count"] > 20:
                analysis["suggestions"].append(
                    f"{process_detail['name']} 공정의 항목이 많습니다. 효율적인 관리를 위해 그룹화를 고려해보세요."
                )
            if not process_detail["has_notes"]:
                analysis["suggestions"].append(
                    f"{process_detail['name']} 공정에 비고가 없습니다. 작업 지시사항을 추가하면 좋습니다."
                )

            # 비용 요인 관련 제안
            for factor in process_detail["cost_factors"]:
                analysis["suggestions"].append(
                    f"{process_detail['name']} 공정의 '{factor['item_name']}'이(가) 전체 비용의 {factor['percentage']:.1f}%를 차지합니다. 원가 절감을 검토해보세요."
                )

        # 워크플로우 최적화 제안
        if analysis["workflow_analysis"]["critical_processes"]:
            analysis["suggestions"].append(
                f"다음 공정들이 전체 비용의 20% 이상을 차지합니다: {', '.join(analysis['workflow_analysis']['critical_processes'])}. 해당 공정들의 원가 관리에 집중하세요."
            )

        return analysis

    except Exception as e:
        print(f"공정 분석 중 오류 발생: {str(e)}")
        return {
            "error": f"공정 분석 실패: {str(e)}"
        } 