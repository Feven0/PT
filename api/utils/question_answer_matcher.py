"""
Structured Question-Answer Matching System

This module provides a robust, deterministic approach to matching questions with answers
without relying on LLM interpretation. It uses embeddings and similarity scoring for
reliable, consistent results.
"""

import re
import json
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
from api.services.secret import get_auth

OPENAI_API_KEY  = get_auth(ssmkey='OPENAI_PARROT_API_KEY')

logger = logging.getLogger(__name__)

@dataclass
class Question:
    """Represents a single question with metadata."""
    text: str
    section_type: str
    ideal_answer: Optional[str] = None
    question_id: Optional[str] = None

@dataclass
class Answer:
    """Represents a single answer with metadata."""
    text: str
    answer_id: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class Match:
    """Represents a question-answer match."""
    question: Question
    answer: Answer
    similarity_score: float
    relevance_score: int  # 0-100
    match_reason: str

class QuestionAnswerMatcher:
    """
    Robust question-answer matching system using OpenAI embeddings and similarity scoring.
    
    CRITICAL DEPENDENCY: This system is STRICTLY dependent on OpenAI embeddings.
    It will NEVER use random or fallback embeddings as they produce meaningless results.
    If OpenAI API is unavailable, the system will fail with clear error messages.
    """
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize the matcher with OpenAI's embedding model.
        
        Args:
            model_name: Name of the OpenAI embedding model to use
        """
        self.model_name = model_name
        self.similarity_threshold = 0.15  # Lowered: Minimum cosine similarity (was 0.3)
        self.relevance_threshold = 30     # Lowered: Minimum relevance score (was 60)
        # Three-band routing (whole-text only, no segmentation)
        self.strong_accept_threshold = 30  # >= 30% → accept directly
        self.borderline_floor = 18         # 18%–30% → send to LLM verifier
        
    def parse_template_questions(self, template_questions: List[Dict]) -> List[Question]:
        """
        Parse template questions into structured Question objects.
        
        Args:
            template_questions: Raw template questions data
            
        Returns:
            List of Question objects
        """
        logger.info(f"🔍 Starting to parse template questions - Input type: {type(template_questions)}, Length: {len(str(template_questions))}")
        logger.info(f"📋 Raw template data: {template_questions}")

        # Accept stringified list inputs (e.g., "['Q1', 'Q2']") by coercing to list
        if isinstance(template_questions, str):
            stripped = template_questions.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    # Prefer JSON if it is valid JSON, else fall back to literal_eval
                    try:
                        parsed = json.loads(stripped)
                    except Exception:
                        import ast
                        parsed = ast.literal_eval(stripped)
                    if isinstance(parsed, list):
                        logger.info("🧩 Detected stringified list for template_questions; coercing to list[str]")
                        template_questions = parsed
                except Exception as e:
                    logger.warning(f"Failed to coerce stringified template_questions to list: {e}")
        
        # Diagnostics: show per-element types for the first few items if list
        if isinstance(template_questions, list):
            preview_n = min(5, len(template_questions))
            for i in range(preview_n):
                elem = template_questions[i]
                logger.info(
                    f"   🔍 [DEBUG] template_questions[{i}] type={type(elem)} :: sample='{str(elem)[:120]}{'...' if len(str(elem))>120 else ''}'"
                )
            all_dicts = all(isinstance(q, dict) for q in template_questions)
            all_strings = all(isinstance(q, str) for q in template_questions)
            logger.info(f"   🔧 [DEBUG] list diagnostics → all_dicts={all_dicts}, all_strings={all_strings}")
            if all_strings:
                logger.info("🧩 Detected simple list[str]; wrapping as a single section for parsing")
                template_questions = [{
                    "sectionType": "General",
                    "questions": [{"question": q} for q in template_questions]
                }]
            elif not all_dicts:
                logger.warn("   ⚠️ Mixed or unexpected element types in template_questions; proceeding without coercion")
        
        questions = []
        
        for section_idx, section in enumerate(template_questions):
            logger.info(f"📂 Processing section {section_idx + 1}: {type(section)}")
            
            if not isinstance(section, dict):
                logger.warn(f"   ⚠️ Section {section_idx + 1} is not a dict, skipping: {section}")
                continue
                
            if 'questions' not in section:
                logger.warn(f"   ⚠️ Section {section_idx + 1} has no 'questions' key, skipping: {section}")
                continue
                
            section_type = section.get('sectionType', 'Unknown Section')
            section_questions = section.get('questions', [])
            
            logger.info(f"   📝 Section '{section_type}' has {len(section_questions)} questions")
            
            for i, question_data in enumerate(section_questions):
                logger.info(f"      🔍 Processing question {i + 1} in section '{section_type}': {type(question_data)}")
                
                if not isinstance(question_data, dict):
                    logger.warn(f"         ⚠️ Question {i + 1} is not a dict, skipping: {question_data}")
                    continue
                    
                if 'question' not in question_data:
                    logger.warn(f"         ⚠️ Question {i + 1} has no 'question' key, skipping: {question_data}")
                    continue
                    
                question_text = question_data['question'].strip()
                logger.info(f"         📄 Raw question text: '{question_text}'")
                
                if not question_text:
                    logger.warn(f"         ⚠️ Question {i + 1} has empty text, skipping")
                    continue
                    
                # Clean and normalize question text
                cleaned_text = self._clean_text(question_text)
                logger.info(f"         ✨ Cleaned question text: '{cleaned_text}'")
                
                question = Question(
                    text=cleaned_text,
                    section_type=section_type,
                    ideal_answer=question_data.get('ideal_answer'),
                    question_id=f"{section_type}_{i}"
                )
                questions.append(question)
                
                logger.info(f"         ✅ Created Question: ID='{question.question_id}', Section='{question.section_type}', IdealAnswer='{question.ideal_answer}'")
                
        logger.info(f"🎯 Successfully parsed {len(questions)} questions from template")
        for q_idx, q in enumerate(questions):
            logger.info(f"   Q{q_idx + 1}: [{q.question_id}] '{q.text}' (Section: {q.section_type})")
        
        return questions
    
    def process_answers(self, answer_transcript: str) -> List[Answer]:
        """
        Process answer transcript into Answer objects without segmentation.
        Takes complete answers as provided.
        
        Args:
            answer_transcript: Raw answer transcript (string or list)
            
        Returns:
            List of Answer objects
        """
        logger.info(f"🔍 Starting to process answer transcript - Input type: {type(answer_transcript)}")
        logger.info(f"📋 Raw answer data: {answer_transcript}")
        
        if not answer_transcript:
            logger.warn("⚠️ Empty answer transcript provided")
            return []
        
        answers = []
        
        # Handle both string and list inputs
        if isinstance(answer_transcript, str):
            stripped = answer_transcript.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    # Prefer JSON; fallback to safe literal eval
                    try:
                        parsed = json.loads(stripped)
                    except Exception:
                        import ast
                        parsed = ast.literal_eval(stripped)
                    if isinstance(parsed, list):
                        logger.info("🧩 Detected stringified list for answer_transcript; coercing to list[str]")
                        answer_transcript = parsed
                except Exception as e:
                    logger.warning(f"Failed to coerce stringified answer_transcript to list: {e}")

        if isinstance(answer_transcript, list):
            logger.info(f"📝 Processing list input with {len(answer_transcript)} items")
            
            # Each item in the list is a complete answer
            for i, answer_text in enumerate(answer_transcript):
                logger.info(f"   🔍 Processing answer item {i + 1}: {type(answer_text)} - '{str(answer_text)[:100]}{'...' if len(str(answer_text)) > 100 else ''}'")
                
                if answer_text and str(answer_text).strip():
                    cleaned_text = str(answer_text).strip()
                    logger.info(f"   ✨ Cleaned answer text: '{cleaned_text[:100]}{'...' if len(cleaned_text) > 100 else ''}'")
                    
                    answer = Answer(
                        text=cleaned_text,
                        answer_id=f"answer_{i}"
                    )
                    answers.append(answer)
                    logger.info(f"   ✅ Created Answer: ID='{answer.answer_id}', Length={len(answer.text)} chars")
                else:
                    logger.warn(f"   ⚠️ Answer item {i + 1} is empty or None, skipping")
        else:
            logger.info(f"📝 Processing string input")
            
            # Single string answer
            if str(answer_transcript).strip():
                cleaned_text = str(answer_transcript).strip()
                logger.info(f"   ✨ Cleaned answer text: '{cleaned_text[:100]}{'...' if len(cleaned_text) > 100 else ''}'")
                
                answer = Answer(
                    text=cleaned_text,
                    answer_id="answer_0"
                )
                answers.append(answer)
                logger.info(f"   ✅ Created Answer: ID='{answer.answer_id}', Length={len(answer.text)} chars")
            else:
                logger.warn("   ⚠️ String answer is empty, skipping")
                
        logger.info(f"🎯 Successfully processed {len(answers)} complete answers (no segmentation)")
        for a_idx, a in enumerate(answers):
            logger.info(f"   A{a_idx + 1}: [{a.answer_id}] '{a.text[:80]}{'...' if len(a.text) > 80 else ''}'")
        
        return answers
    
    def _split_by_delimiters(self, text: str) -> List[str]:
        """
        Split text by common answer delimiters.
        
        Args:
            text: Text to split
            
        Returns:
            List of text segments
        """
        # Common delimiters that indicate answer boundaries
        delimiters = [
            r'\.\s+(?=[A-Z])',  # Period followed by capital letter
            r'\.\s*$',          # Period at end of line
            r'\?\s+',           # Question mark
            r'!\s+',            # Exclamation mark
            r'\n\s*\n',         # Double newlines
            r'\.\s*My\s+',      # "My" after period (common in interviews)
            r'\.\s*I\s+',       # "I" after period
            r'\.\s*So\s+',      # "So" after period
            r'\.\s*Well\s+',    # "Well" after period
        ]
        
        segments = [text]
        for delimiter in delimiters:
            new_segments = []
            for segment in segments:
                parts = re.split(delimiter, segment)
                new_segments.extend(parts)
            segments = new_segments
            
        return [s.strip() for s in segments if s.strip()]
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common interview artifacts
        text = re.sub(r'^(um|uh|er|ah)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+(um|uh|er|ah)\s+', ' ', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def compute_similarities(self, questions: List[Question], answers: List[Answer]) -> np.ndarray:
        """
        Compute similarity matrix between questions and answers using OpenAI embeddings.
        
        Args:
            questions: List of Question objects
            answers: List of Answer objects
            
        Returns:
            Similarity matrix of shape (len(questions), len(answers))
        """
        logger.info(f"🔍 Starting similarity computation - Questions: {len(questions)}, Answers: {len(answers)}")
        
        if not questions or not answers:
            logger.warn("⚠️ Empty questions or answers list, returning empty matrix")
            return np.array([])
            
        # Prepare texts for embedding
        question_texts = [q.text for q in questions]
        answer_texts = [a.text for a in answers]
        
        logger.info(f"📝 Question texts prepared:")
        for i, text in enumerate(question_texts):
            logger.info(f"   Q{i+1}: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            
        logger.info(f"📝 Answer texts prepared:")
        for i, text in enumerate(answer_texts):
            logger.info(f"   A{i+1}: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        
        # Compute embeddings using OpenAI
        logger.info(f"🤖 Computing OpenAI embeddings for {len(question_texts)} questions...")
        question_embeddings = self._get_openai_embeddings(question_texts)
        logger.info(f"✅ Question embeddings computed: shape {question_embeddings.shape}")
        
        logger.info(f"🤖 Computing OpenAI embeddings for {len(answer_texts)} answers...")
        answer_embeddings = self._get_openai_embeddings(answer_texts)
        logger.info(f"✅ Answer embeddings computed: shape {answer_embeddings.shape}")
        
        # Debug embeddings
        logger.info(f"🔍 Debugging embeddings:")
        logger.info(f"   Question embeddings shape: {question_embeddings.shape}, dtype: {question_embeddings.dtype}")
        logger.info(f"   Answer embeddings shape: {answer_embeddings.shape}, dtype: {answer_embeddings.dtype}")
        logger.info(f"   Question embeddings range: [{question_embeddings.min():.6f}, {question_embeddings.max():.6f}]")
        logger.info(f"   Answer embeddings range: [{answer_embeddings.min():.6f}, {answer_embeddings.max():.6f}]")
        
        # Compute cosine similarity
        logger.info(f"📊 Computing cosine similarity matrix...")
        
        try:
            similarity_matrix = cosine_similarity(question_embeddings, answer_embeddings)
            logger.info(f"✅ Cosine similarity computed successfully")
        except Exception as e:
            logger.error(f"❌ Cosine similarity computation failed: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Question embeddings: shape={question_embeddings.shape}, dtype={question_embeddings.dtype}")
            logger.error(f"❌ Answer embeddings: shape={answer_embeddings.shape}, dtype={answer_embeddings.dtype}")
            raise e  # Re-raise to see the full error
        
        logger.info(f"✅ Similarity matrix computed: shape {similarity_matrix.shape}")
        
        # Log the full similarity matrix
        logger.info(f"📊 Full similarity matrix:")
        for q_idx in range(len(questions)):
            logger.info(f"   Q{q_idx+1} ({questions[q_idx].text[:50]}...):")
            for a_idx in range(len(answers)):
                score = similarity_matrix[q_idx, a_idx]
                logger.info(f"      vs A{a_idx+1}: {score:.4f} ({answers[a_idx].text[:50]}...)")
        
        return similarity_matrix
    
    def _get_openai_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings from OpenAI API.
        
        CRITICAL: This method NEVER uses random or fallback embeddings.
        If OpenAI API fails, the entire matching process must fail.
        Random embeddings would produce completely meaningless similarity scores.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
            
        Raises:
            RuntimeError: If OpenAI API fails or API key is missing
        """
        logger.info(f"🤖 Requesting OpenAI embeddings for {len(texts)} texts using model '{self.model_name}'")
        
        try:
            logger.info(f"📤 Sending request to OpenAI API using provided API key...")
            # Use the provided API key
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            
            logger.info(f"✅ OpenAI API response received successfully")
            logger.info(f"📊 Response details: {len(response.data)} embeddings, model: {response.model}")
            
            embeddings = [data.embedding for data in response.data]
            embeddings_array = np.array(embeddings)
            
            logger.info(f"📊 Embeddings array created: shape {embeddings_array.shape}, dtype {embeddings_array.dtype}")
            logger.info(f"📊 Embedding dimensions: {embeddings_array.shape[1]} per text")
            
            # Log sample embedding values (first few dimensions)
            for i, embedding in enumerate(embeddings[:3]):  # Log first 3 embeddings
                logger.info(f"   Sample embedding {i+1}: first 5 values = {embedding[:5]}")
            
            return embeddings_array
            
        except Exception as e:
            logger.error(f"❌ Failed to get OpenAI embeddings: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            
            # CRITICAL: Never use fallback embeddings - they produce meaningless results
            logger.error(f"❌ Cannot proceed without valid OpenAI embeddings")
            logger.error(f"❌ The system requires real semantic embeddings for accurate matching")
            logger.error(f"❌ Random embeddings would produce completely meaningless similarity scores")
            raise RuntimeError(f"OpenAI embeddings are required for accurate matching. Cannot proceed without valid embeddings. Error: {e}")

    def _llm_verify_match(self, question_text: str, answer_text: str) -> Dict[str, Any]:
        """
        Borderline verifier: ask the LLM to render a minimal JSON verdict whether
        the whole answer appropriately answers the whole question.
        Returns a dict like {"is_match": bool, "reason": str, "confidence": "low|medium|high"}.
        """
        prompt = (
            "You are a strict evaluator. Given a question and a candidate answer, decide if the answer reasonably answers the question. "
            "Evaluate the ENTIRE question and the ENTIRE answer AS-IS. Do NOT rewrite, summarize, extract, segment, trim, or transform them. "
            "Do NOT propose a better answer. Do NOT ignore parts. Only judge whether the provided full answer addresses the provided full question. "
            "Reply in strict JSON only with no extra text: {\"is_match\": true|false, \"confidence\": \"low|medium|high\", \"reason\": \"...\"}.\n\n"
            f"Question (verbatim):\n{question_text}\n\n"
            f"Answer (verbatim):\n{answer_text}\n"
        )
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return strict JSON only. No prose. Do not rewrite or segment inputs."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=200,
            )
            content = resp.choices[0].message.content
            # best-effort JSON parse
            try:
                return json.loads(content)
            except Exception:
                # fallback: attempt to extract JSON substring
                import re as _re
                m = _re.search(r"\{[\s\S]*\}", content)
                return json.loads(m.group(0)) if m else {"is_match": False, "confidence": "low", "reason": "invalid_json"}
        except Exception as e:
            logger.warn(f"LLM verifier exception: {e}")
            return {"is_match": False, "confidence": "low", "reason": f"exception: {e}"}
    
    def find_matches(self, questions: List[Question], answers: List[Answer]) -> List[Match]:
        """
        Find best matches between questions and answers.
        
        Args:
            questions: List of Question objects
            answers: List of Answer objects
            
        Returns:
            List of Match objects
        """
        logger.info(f"🔍 Starting match finding process - Questions: {len(questions)}, Answers: {len(answers)}")
        logger.info(f"📊 Thresholds: similarity >= {self.similarity_threshold}, relevance >= {self.relevance_threshold}")
        
        if not questions or not answers:
            logger.warn("⚠️ Empty questions or answers list, returning empty matches")
            return []
            
        # Compute similarities
        logger.info(f"📊 Computing similarity matrix...")
        similarity_matrix = self.compute_similarities(questions, answers)
        
        matches = []
        used_answers = set()
        
        logger.info(f"🎯 Starting to find best matches for each question...")
        
        # Find best matches
        for q_idx, question in enumerate(questions):
            logger.info(f"🔍 Processing Question {q_idx + 1}: '{question.text[:80]}{'...' if len(question.text) > 80 else ''}'")
            
            best_match = None
            best_score = 0
            best_answer_idx = -1
            second_best_score = 0
            second_best_idx = -1
            
            logger.info(f"   📊 Checking against {len(answers)} answers:")
            
            for a_idx, answer in enumerate(answers):
                if a_idx in used_answers:
                    logger.info(f"      A{a_idx + 1}: SKIPPED (already used)")
                    continue
                    
                similarity = similarity_matrix[q_idx, a_idx]
                
                # Convert similarity to relevance score (0-100)
                relevance_score = int(similarity * 100)
                
                logger.info(f"      A{a_idx + 1}: similarity={similarity:.4f}, relevance={relevance_score}% - '{answer.text[:50]}{'...' if len(answer.text) > 50 else ''}'")
                
                if similarity >= self.similarity_threshold:
                    logger.info(f"         ✅ Above similarity threshold ({self.similarity_threshold})")
                    if relevance_score > best_score:
                        logger.info(f"         🏆 NEW BEST MATCH! Previous best: {best_score}%, New: {relevance_score}%")
                        # demote current best to second best
                        second_best_score = best_score
                        second_best_idx = best_answer_idx
                        # promote
                        best_score = relevance_score
                        best_match = answer
                        best_answer_idx = a_idx
                    elif relevance_score > second_best_score:
                        second_best_score = relevance_score
                        second_best_idx = a_idx
                    else:
                        logger.info(f"         📉 Not better than current best ({best_score}%)")
                else:
                    logger.info(f"         ❌ Below similarity threshold ({self.similarity_threshold})")
            
            # Banding decision with optional LLM verifier on borderline
            decision_reason = None
            if best_match and best_score >= self.strong_accept_threshold:
                decision_reason = "accepted_by_embedding"
            elif best_match and best_score >= self.borderline_floor:
                logger.info(f"   🤔 BORDERLINE case for Q{q_idx + 1}: best={best_score}%, second_best={second_best_score}% → verifying via LLM")
                try:
                    verifier = self._llm_verify_match(question.text, best_match.text)
                    logger.info(f"   🧠 Verifier response: {verifier}")
                    if isinstance(verifier, dict) and verifier.get("is_match") and verifier.get("confidence") != "low":
                        decision_reason = "accepted_by_verifier"
                    else:
                        decision_reason = "rejected_by_verifier"
                        best_match = None
                except Exception as e:
                    logger.warn(f"   ⚠️ Verifier failed: {e}")
                    decision_reason = "verifier_error"
                    best_match = None

            # Check if we found a valid match after banding
            if best_match and (decision_reason in ("accepted_by_embedding", "accepted_by_verifier")):
                logger.info(f"   ✅ VALID MATCH FOUND: A{best_answer_idx + 1} with score {best_score}% ({decision_reason})")
                match = Match(
                    question=question,
                    answer=best_match,
                    similarity_score=similarity_matrix[q_idx, best_answer_idx],
                    relevance_score=best_score,
                    match_reason=("Semantic similarity (strong)" if decision_reason == "accepted_by_embedding" else "Semantic similarity (borderline, LLM verified)")
                )
                matches.append(match)
                used_answers.add(best_answer_idx)
                
                logger.info(f"   📝 Match details: Q{q_idx + 1} → A{best_answer_idx + 1}")
                logger.info(f"      Question: '{question.text[:100]}{'...' if len(question.text) > 100 else ''}'")
                logger.info(f"      Answer: '{best_match.text[:100]}{'...' if len(best_match.text) > 100 else ''}'")
                logger.info(f"      Similarity: {similarity_matrix[q_idx, best_answer_idx]:.4f}")
                logger.info(f"      Relevance: {best_score}% (second_best={second_best_score}%)")
            else:
                logger.warn(f"   ❌ NO VALID MATCH FOUND for Q{q_idx + 1}")
                if best_match:
                    logger.warn(f"      Best candidate: A{best_answer_idx + 1} with score {best_score}% (below threshold {self.relevance_threshold}%)")
                else:
                    logger.warn(f"      No candidates above similarity threshold {self.similarity_threshold}")
                
        logger.info(f"🎯 Match finding completed: {len(matches)} valid matches found")
        logger.info(f"📊 Used answers: {sorted(used_answers)}")
        logger.info(f"📊 Unused answers: {sorted(set(range(len(answers))) - used_answers)}")
        
        return matches
    
    def match_questions_answers(self, template_questions: List[Dict], answer_transcript: str) -> Dict[str, Any]:
        """
        Main method to match questions with answers.
        
        Args:
            template_questions: Raw template questions data
            answer_transcript: Raw answer transcript
            
        Returns:
            Dictionary with matching results
        """
        try:
            logger.info(f"🚀 Starting QuestionAnswerMatcher.match_questions_answers()")
            logger.info(f"📋 Input parameters:")
            logger.info(f"   template_questions type: {type(template_questions)}, length: {len(template_questions) if template_questions else 0}")
            logger.info(f"   answer_transcript type: {type(answer_transcript)}, length: {len(str(answer_transcript)) if answer_transcript else 0}")
            
            # CRITICAL: Validate OpenAI API key before proceeding
            logger.info(f"🔑 Validating OpenAI API key availability...")
            try:
                # Test OpenAI API key with a simple request using provided key
                import openai
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                test_response = client.embeddings.create(
                    model=self.model_name,
                    input=["test"]
                )
                logger.info(f"✅ OpenAI API key validated successfully using provided key")
            except Exception as api_error:
                logger.error(f"❌ OpenAI API key validation failed: {api_error}")
                logger.error(f"❌ Cannot proceed without valid OpenAI API key")
                return {
                    "error": "OpenAI API key required", 
                    "details": f"Cannot perform question-answer matching without OpenAI embeddings. API error: {api_error}"
                }
            
            # Parse questions
            logger.info(f"🔍 Step 1: Parsing template questions...")
            questions = self.parse_template_questions(template_questions)
            if not questions:
                logger.error(f"❌ No valid questions found after parsing")
                return {"error": "No valid questions found"}
            
            logger.info(f"✅ Successfully parsed {len(questions)} questions")
            
            # Process answers (no segmentation)
            logger.info(f"🔍 Step 2: Processing answer transcript...")
            answers = self.process_answers(answer_transcript)
            if not answers:
                logger.error(f"❌ No valid answers found after processing")
                return {"error": "No valid answers found"}
            
            logger.info(f"✅ Successfully processed {len(answers)} answers")
            
            # Find matches
            logger.info(f"🔍 Step 3: Finding matches between questions and answers...")
            matches = self.find_matches(questions, answers)
            
            logger.info(f"✅ Match finding completed: {len(matches)} matches found")
            
            # Format results
            logger.info(f"🔍 Step 4: Formatting results...")
            result = {
                "total_questions": len(questions),
                "total_answers": len(answers),
                "matches_found": len(matches),
                "matches": []
            }
            
            logger.info(f"📊 Result summary: {result['total_questions']} questions, {result['total_answers']} answers, {result['matches_found']} matches")
            
            # Add all questions to result (matched and unmatched)
            matched_question_ids = {match.question.question_id for match in matches}
            logger.info(f"📊 Matched question IDs: {matched_question_ids}")
            
            for question in questions:
                logger.info(f"🔍 Processing question for result: {question.question_id}")
                
                if question.question_id in matched_question_ids:
                    # Find the match for this question
                    match = next(m for m in matches if m.question.question_id == question.question_id)
                    
                    match_result = {
                        "question": question.text,
                        "answer": match.answer.text,
                        "relevance_score": match.relevance_score,
                        "reason": match.match_reason,
                        "similarity_score": float(match.similarity_score),
                        "band": "strong" if match.relevance_score >= self.strong_accept_threshold else ("borderline" if match.relevance_score >= self.borderline_floor else "low"),
                        "section_type": question.section_type
                    }
                    
                    logger.info(f"   ✅ MATCHED: Q{question.question_id} → A{match.answer.answer_id} (score: {match.relevance_score}%)")
                    logger.info(f"      Question: '{question.text[:80]}{'...' if len(question.text) > 80 else ''}'")
                    logger.info(f"      Answer: '{match.answer.text[:80]}{'...' if len(match.answer.text) > 80 else ''}'")
                    
                else:
                    # Unmatched question - do not assign default scores to sensitive data
                    match_result = {
                        "question": question.text,
                        "answer": None,
                        "relevance_score": None,  # CRITICAL: Never assign default scores to sensitive data
                        "reason": "No matching answer found",
                        "similarity_score": None,
                        "band": "low",
                        "section_type": question.section_type
                    }
                    
                    logger.warn(f"   ❌ UNMATCHED: Q{question.question_id} - '{question.text[:80]}{'...' if len(question.text) > 80 else ''}'")
                
                result["matches"].append(match_result)
            
            logger.info(f"🎯 Final result prepared with {len(result['matches'])} entries")
            logger.info(f"📊 Match statistics:")
            logger.info(f"   Total questions: {result['total_questions']}")
            logger.info(f"   Total answers: {result['total_answers']}")
            logger.info(f"   Successful matches: {result['matches_found']}")
            logger.info(f"   Unmatched questions: {result['total_questions'] - result['matches_found']}")
            
            return result
            
        except RuntimeError as e:
            if "OpenAI embeddings are required" in str(e):
                logger.error(f"❌ CRITICAL: Cannot perform matching without OpenAI API key")
                logger.error(f"❌ The system requires valid embeddings to produce meaningful similarity scores")
                logger.error(f"❌ Random embeddings would produce completely meaningless results")
                return {"error": "OpenAI API key required", "details": "Cannot perform question-answer matching without OpenAI embeddings. Please configure OPENAI_API_KEY environment variable."}
            else:
                raise e
        except Exception as e:
            logger.error(f"❌ Error in match_questions_answers: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {"error": f"Internal error: {str(e)}"}
    
    def get_matching_statistics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about the matching results.
        
        Args:
            result: Result from match_questions_answers
            
        Returns:
            Dictionary with statistics
        """
        if "error" in result:
            return {"error": result["error"]}
            
        matches = result.get("matches", [])
        matched_count = sum(1 for m in matches if m["answer"] is not None)
        unmatched_count = len(matches) - matched_count
        
        scores = [m["relevance_score"] for m in matches if m["answer"] is not None]
        
        stats = {
            "total_questions": result["total_questions"],
            "matched_questions": matched_count,
            "unmatched_questions": unmatched_count,
            "match_rate": matched_count / result["total_questions"] if result["total_questions"] > 0 else None,  # CRITICAL: Never assign default values
            "average_score": np.mean(scores) if scores else None,  # CRITICAL: Never assign default values
            "score_distribution": {
                "high_scores": sum(1 for s in scores if s >= 80),
                "medium_scores": sum(1 for s in scores if 60 <= s < 80),
                "low_scores": sum(1 for s in scores if s < 60)
            }
        }
        
        return stats

