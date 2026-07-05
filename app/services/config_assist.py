from __future__ import annotations

from typing import Any

from app.providers import PublicAssetSearchProvider


SECTOR_ASSIST_SCHEMA: dict[str, Any] = {
    "horizon": "long | medium | short",
    "driver": "string",
    "risks": "string",
    "indicators": ["string"],
    "upstream": ["string"],
    "downstream": ["string"],
    "related_assets": [
        {
            "name": "string",
            "ticker": "string optional",
            "market": "A-share | HK | US optional",
            "rationale": "string",
        }
    ],
    "confidence": 0.0,
    "risk_notes": ["string"],
    "disclaimer": "不构成投资建议，不提供确定性买卖指令。",
}

ASSET_ASSIST_SCHEMA: dict[str, Any] = {
    "name": "string",
    "ticker": "string optional",
    "market": "A-share | HK | US",
    "sector": "string",
    "rationale": "string",
    "confidence": 0.0,
    "risk_notes": ["string"],
    "disclaimer": "不构成投资建议，不提供确定性买卖指令。",
}


class ConfigAssistService:
    def __init__(
        self,
        *,
        llm_provider: Any,
        asset_search_provider: PublicAssetSearchProvider | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.asset_search_provider = asset_search_provider or PublicAssetSearchProvider()

    def assist_sector(self, name: str, *, market_scope: list[str] | None = None) -> dict[str, Any]:
        output = self.llm_provider.run_structured_task(
            "assist_sector_config",
            {
                "sector_name": name,
                "market_scope": market_scope or ["A-share", "HK"],
                "instruction": (
                    "生成机构投研风格行业画像。候选标的应优先覆盖 A 股和港股，"
                    "避免短线荐股话术，只给研究覆盖和代表性产业链映射。"
                ),
            },
            evidence_refs=[f"sector_name:{name}"],
            required_output=SECTOR_ASSIST_SCHEMA,
        )
        result = self._normalize_sector_result(name, output.result)
        validated_assets = self._validate_related_assets(
            result.get("related_assets") or [],
            market_scope=market_scope,
        )
        result["validatedAssets"] = validated_assets
        result["relatedTickers"] = [asset["ticker"] for asset in validated_assets]
        result["provider"] = output.provider
        result["model"] = output.model
        result["confidence"] = output.confidence
        result["risk_notes"] = output.risk_notes
        result["disclaimer"] = output.disclaimer
        return result

    def assist_asset(self, name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        output = self.llm_provider.run_structured_task(
            "assist_asset_config",
            {
                "asset_name": name,
                "ticker_hint": payload.get("ticker"),
                "market_hint": payload.get("market"),
                "sector_hint": payload.get("sector"),
                "instruction": "识别标的代码、市场和所属行业，仅输出研究配置字段。",
            },
            evidence_refs=[f"asset_name:{name}"],
            required_output=ASSET_ASSIST_SCHEMA,
        )
        result = dict(output.result)
        candidate = {
            "name": result.get("name") or name,
            "ticker": result.get("ticker") or payload.get("ticker") or "",
            "market": result.get("market") or payload.get("market") or "A-share",
            "rationale": result.get("rationale") or "",
        }
        validated_assets = self._validate_related_assets([candidate], market_scope=None)
        if validated_assets:
            result.update(validated_assets[0])
        result.setdefault("name", name)
        result.setdefault("sector", payload.get("sector") or "待分类")
        result["validatedAssets"] = validated_assets
        result["provider"] = output.provider
        result["model"] = output.model
        result["confidence"] = output.confidence
        result["risk_notes"] = output.risk_notes
        result["disclaimer"] = output.disclaimer
        return result

    @staticmethod
    def _normalize_sector_result(name: str, result: dict[str, Any]) -> dict[str, Any]:
        indicators = _list(result.get("indicators") or result.get("观察指标"))
        upstream = _list(result.get("upstream") or result.get("上游"))
        downstream = _list(result.get("downstream") or result.get("下游"))
        related_assets = result.get("related_assets") or result.get("candidate_assets") or []
        return {
            "horizon": _horizon(result.get("horizon") or result.get("cycle") or result.get("观察周期")),
            "driver": str(result.get("driver") or result.get("summary") or f"{name} 行业画像由 DeepSeek 生成。"),
            "risks": _join(result.get("risks") or result.get("risk_notes") or []),
            "indicators": indicators[:8],
            "upstream": upstream[:8],
            "downstream": downstream[:8],
            "related_assets": related_assets if isinstance(related_assets, list) else [],
        }

    def _validate_related_assets(
        self,
        candidates: list[Any],
        *,
        market_scope: list[str] | None,
    ) -> list[dict[str, Any]]:
        validated: list[dict[str, Any]] = []
        seen: set[str] = set()
        for candidate in candidates[:40]:
            normalized = _candidate(candidate)
            query = normalized.get("ticker") or normalized.get("name")
            if not query:
                continue
            markets = _candidate_markets(normalized.get("market"), market_scope)
            results = self.asset_search_provider.search_assets(query, limit=6, markets=markets)
            match = _best_match(results, normalized)
            if not match or match["ticker"] in seen:
                continue
            seen.add(match["ticker"])
            validated.append(
                {
                    "ticker": match["ticker"],
                    "name": match["name"],
                    "market": match["market"],
                    "exchange": match.get("exchange"),
                    "source": match.get("source"),
                    "rationale": normalized.get("rationale") or "",
                }
            )
        return validated


def _candidate(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "ticker": str(value.get("ticker") or value.get("code") or "").strip(),
            "name": str(value.get("name") or value.get("company") or "").strip(),
            "market": str(value.get("market") or "").strip(),
            "rationale": str(value.get("rationale") or value.get("reason") or "").strip(),
        }
    return {"ticker": "", "name": str(value).strip(), "market": "", "rationale": ""}


def _candidate_markets(candidate_market: str | None, market_scope: list[str] | None) -> list[str]:
    value = (candidate_market or "").strip().lower()
    if value in {"a-share", "a股", "a", "cn"}:
        return ["A-share"]
    if value in {"hk", "港股"}:
        return ["HK"]
    return market_scope or ["A-share", "HK"]


def _best_match(results: list[dict[str, Any]], candidate: dict[str, str]) -> dict[str, Any] | None:
    if not results:
        return None
    ticker = candidate.get("ticker", "").upper()
    for result in results:
        if ticker and result.get("ticker", "").upper() == ticker:
            return result
    return results[0] if float(results[0].get("score") or 0) >= 0.7 else None


def _horizon(value: Any) -> str:
    text = str(value or "").lower()
    if text in {"long", "长期", "1-3年", "1至3年"}:
        return "long"
    if text in {"short", "短期", "1天至1个月", "1 day to 1 month"}:
        return "short"
    return "medium"


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").replace("，", ",").split(",") if item.strip()]


def _join(value: Any) -> str:
    if isinstance(value, list):
        return "；".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()
