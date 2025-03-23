from typing import Dict, Any, List
from datetime import datetime

def analyze_estimate(estimate_data: Dict[str, Any]) -> Dict[str, Any]:
    """견적서 데이터 분석"""
    try:
        analysis = {
            "total_amount": 0,
            "process_count": 0,
            "item_count": 0,
            "process_analysis": [],
            "cost_analysis": {
                "high_cost_items": [],
                "low_cost_items": [],
                "avg_unit_price": 0
            },
            "efficiency_analysis": {
                "duplicate_items": [],
                "similar_items": [],
                "optimization_suggestions": []
            },
            "suggestions": []
        }

        total_unit_price = 0
        item_count = 0
        all_items = []

        # 공정별 분석
        for process in estimate_data.get("processes", []):
            process_total = 0
            process_items = process.get("items", [])
            
            # 항목별 금액 계산
            for item in process_items:
                quantity = float(item.get("quantity", 0))
                unit_price = float(item.get("unitPrice", 0))
                amount = quantity * unit_price
                process_total += amount
                total_unit_price += unit_price
                item_count += 1

                # 고가/저가 항목 분류
                item_info = {
                    "name": item.get("name", ""),
                    "process": process.get("name", ""),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_amount": amount
                }
                all_items.append(item_info)

            # 공정 분석 추가
            analysis["process_analysis"].append({
                "process_name": process.get("name", ""),
                "total_amount": process_total,
                "item_count": len(process_items),
                "avg_item_price": process_total / len(process_items) if process_items else 0
            })

            analysis["total_amount"] += process_total

        analysis["process_count"] = len(estimate_data.get("processes", []))
        analysis["item_count"] = item_count

        # 평균 단가 계산
        if item_count > 0:
            analysis["cost_analysis"]["avg_unit_price"] = total_unit_price / item_count

        # 고가/저가 항목 분류
        sorted_items = sorted(all_items, key=lambda x: x["total_amount"], reverse=True)
        analysis["cost_analysis"]["high_cost_items"] = sorted_items[:5]  # 상위 5개
        analysis["cost_analysis"]["low_cost_items"] = sorted_items[-5:]  # 하위 5개

        # 중복/유사 항목 분석
        item_names = {}
        for item in all_items:
            name = item["name"].lower()
            if name in item_names:
                analysis["efficiency_analysis"]["duplicate_items"].append({
                    "name": item["name"],
                    "processes": [item_names[name]["process"], item["process"]]
                })
            else:
                item_names[name] = item

        # 개선 제안 생성
        if analysis["total_amount"] > 50000000:
            analysis["suggestions"].append("고액 견적서입니다. 원가 절감 방안을 검토해보세요.")
        
        if analysis["item_count"] > 50:
            analysis["suggestions"].append("항목이 많습니다. 유사 항목을 통합하여 관리효율을 높일 수 있습니다.")

        if len(analysis["efficiency_analysis"]["duplicate_items"]) > 0:
            analysis["suggestions"].append("중복된 항목이 발견되었습니다. 통합 관리를 고려해보세요.")

        # 원가 최적화 제안
        high_cost_items = analysis["cost_analysis"]["high_cost_items"]
        if high_cost_items:
            top_item = high_cost_items[0]
            analysis["suggestions"].append(
                f"'{top_item['name']}'의 단가가 가장 높습니다. 대체 공급업체 검토를 추천합니다."
            )

        return analysis

    except Exception as e:
        print(f"견적서 분석 중 오류 발생: {str(e)}")
        return {
            "error": f"견적서 분석 실패: {str(e)}"
        } 