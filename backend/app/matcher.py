import os
import certifi
import urllib.request
from typing import Dict, Any

from .alignment_engine import align_face
from .embedding_engine import generate_normalized_embedding
from .vector_index import search_database_top_k
from .decision_logic import process_top_candidates

from .database import get_db
from .models import MatchReport

class MatcherFacade:
    def __init__(self):
        # Trigger certifi override if mac/windows python issues SSL
        os.environ['SSL_CERT_FILE'] = certifi.where()

    def process_query_image(self, db_session, image_path: str, query_image_url: str = "Uploaded_Directly") -> Dict[str, Any]:
        """
        Orchestrator for the 10K-Scale Matching Pipeline.
        1. Aligns Face (No over-enhancement)
        2. Generates L2 Normalized Arcface embedding
        3. Executes pgvector sub-50ms query for Top 5 candidates
        4. Applies Decision Gap Logic
        5. Spawns Manual Review items for verification
        6. Returns structured output
        """
        try:
            # Step 1 & 2: Unified Detection & Embedding (L2 Normalized with RetinaFace)
            try:
                # We no longer align externally. DeepFace handles it internally via the engine.
                query_vector = generate_normalized_embedding(image_path)
            except ValueError as e:
                return {
                    "error": str(e),
                    "confidence_level": "no_match"
                }

            # 3. High-Speed pgvector Search (Top 5)
            print(f"DEBUG MATCHER: Vector generated, length: {len(query_vector)}")
            candidates = search_database_top_k(db_session, query_vector, k=5)
            print(f"DEBUG MATCHER: Pgvector Top 5 Candidates: {candidates}")
            if not candidates:
                print("DEBUG MATCHER: Pgvector returned empty list.")
                return {
                    "confidence_level": "no_match"
                }
                
            # 4. Enforce Gap Delta Logic (Top1 vs Top2)
            decision, top1_data = process_top_candidates(candidates)
            print(f"DEBUG MATCHER: Decision Logic Output = {decision}, Top 1 Data = {top1_data}")
            
            # 5. Handle Match Reports (Always create for strong_match or review_required)
            sim = top1_data.get("similarity", 0.0)
            child_id = top1_data.get("child_id")
            
            if decision in ["strong_match", "review_required"]:
                try:
                    report = MatchReport(
                        child_id=child_id,
                        similarity=sim,
                        reporter_image_url=query_image_url, 
                        status="pending_review" if decision == "review_required" else "verified_by_ai"
                    )
                    db_session.add(report)
                    db_session.commit()
                except Exception as db_e:
                   print(f"Failed to log background review: {db_e}")
                   
            # 6. Structured Response
            if decision == "no_match":
                 return {
                    "confidence_level": decision
                 }
                 
            return {
                "child_id": str(child_id) if child_id else None,
                "similarity": round(sim, 3),
                "confidence_level": decision,
                "full_name": top1_data.get("full_name"),
                "age": top1_data.get("age"),
                "gender": top1_data.get("gender"),
                "last_seen_location": top1_data.get("last_seen_location"),
                "station_name": top1_data.get("station_name"),
                "station_address": top1_data.get("station_address"),
                "station_contact_number": top1_data.get("station_contact_number")
            }
            
        except Exception as e:
            import traceback
            print(f"Matcher API Error: {str(e)}")
            traceback.print_exc()
            return {
                "error": str(e),
                "confidence_level": "error"
            }

_matcher = None

def get_matcher():
    global _matcher
    if _matcher is None:
        _matcher = MatcherFacade()
    return _matcher

def run_identification_pipeline(db, image_path: str, query_image_url: str = "Uploaded_Directly") -> Dict[str, Any]:
    matcher = get_matcher()
    return matcher.process_query_image(db, image_path, query_image_url)
