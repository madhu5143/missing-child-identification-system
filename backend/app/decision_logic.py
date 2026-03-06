from typing import List, Dict, Any, Tuple

class DecisionEngine:
    def __init__(self):
        # Strict user specifications
        self.STRONG_MATCH_THRESHOLD = 0.78
        self.REVIEW_REQUIRED_THRESHOLD = 0.68
        self.GAP_DELTA_THRESHOLD = 0.07

    def evaluate_match_safety(self, candidates: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        """
        Receives the top K candidates from pgvector.
        Returns the final strict decision ('strong_match', 'review_required', 'no_match')
        along with the top candidate's data.
        
        Rules:
        - IF top1 >= 0.78 AND (top1 - top2) >= 0.07 -> strong_match
        - ELIF 0.68 <= top1 < 0.78 -> review_required
        - ELSE -> no_match
        """
        if not candidates or len(candidates) == 0:
            return ("no_match", {})
            
        top1_data = candidates[0]
        top1_sim = top1_data.get("similarity", 0.0)
        
        # Determine top2 similarity for the gap delta check
        top2_sim = 0.0
        if len(candidates) > 1:
            top2_sim = candidates[1].get("similarity", 0.0)
            
        gap = top1_sim - top2_sim

        print(f"DEBUG: top1_sim = {top1_sim}, top2_sim = {top2_sim}")
        # 1. Strong Match Check
        if top1_sim >= self.STRONG_MATCH_THRESHOLD and gap >= self.GAP_DELTA_THRESHOLD:
            return ("strong_match", top1_data)
            
        # 2. Borderline / Review Required Check
        if self.REVIEW_REQUIRED_THRESHOLD <= top1_sim < self.STRONG_MATCH_THRESHOLD:
            # Note: The specifications allow review_required merely if it's in this bracket,
            # but we also trigger review if the gap test for a >0.78 match failed.
            return ("review_required", top1_data)
        elif top1_sim >= self.STRONG_MATCH_THRESHOLD and gap < self.GAP_DELTA_THRESHOLD:
            # Over 0.78 but it looks too similar to someone else - send to manual review
            return ("review_required", top1_data)
            
        # 3. Flat Reject
        return ("no_match", top1_data)

_engine = None

def get_decision_engine():
    global _engine
    if _engine is None:
        _engine = DecisionEngine()
    return _engine

def process_top_candidates(candidates: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    engine = get_decision_engine()
    return engine.evaluate_match_safety(candidates)
