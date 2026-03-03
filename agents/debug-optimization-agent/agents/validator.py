"""Validator agent for validating optimization suggestions."""

from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel

from tools.code_executor import CodeExecutor
from models.llm_provider import LLMFactory
from utils.logger import AgentLogger
from prompts.validator_prompts import VALIDATOR_SYSTEM_PROMPT, VALIDATOR_USER_PROMPT


class ValidatorAgent:
    """Agent for validating optimization suggestions and code changes."""
    
    def __init__(self, llm: BaseChatModel = None):
        """
        Initialize validator agent.
        
        Args:
            llm: Language model to use
        """
        self.llm = llm or LLMFactory.create_validator_llm()
        self.logger = AgentLogger("Validator")
        self.executor = CodeExecutor()
    
    def validate(
        self,
        original_code: str,
        optimized_code: str,
        optimization_description: str
    ) -> Dict[str, Any]:
        """
        Validate optimization suggestion.
        
        Args:
            original_code: Original code
            optimized_code: Optimized code
            optimization_description: Description of the optimization
            
        Returns:
            Validation results
        """
        self.logger.info("Starting validation")
        
        try:
            results = {
                "syntax_valid": False,
                "functionally_equivalent": False,
                "performance_improved": False,
                "safe_to_apply": False,
                "validation_details": {},
                "warnings": [],
                "errors": []
            }
            
            # Syntax validation
            syntax_result = self._validate_syntax(optimized_code)
            results["syntax_valid"] = syntax_result["valid"]
            if not syntax_result["valid"]:
                results["errors"].append(f"Syntax error: {syntax_result['error']}")
                return results
            
            # Functional equivalence check
            equivalence_result = self._check_functional_equivalence(
                original_code,
                optimized_code
            )
            results["functionally_equivalent"] = equivalence_result["equivalent"]
            results["validation_details"]["equivalence"] = equivalence_result
            
            if not equivalence_result["equivalent"]:
                results["warnings"].append(
                    "Functional equivalence could not be verified"
                )
            
            # Performance comparison
            performance_result = self._compare_performance(
                original_code,
                optimized_code
            )
            results["performance_improved"] = performance_result["improved"]
            results["validation_details"]["performance"] = performance_result
            
            # Safety check
            safety_result = self._check_safety(optimized_code)
            results["safe_to_apply"] = safety_result["safe"]
            results["validation_details"]["safety"] = safety_result
            
            if not safety_result["safe"]:
                results["errors"].append(f"Safety concern: {safety_result['reason']}")
            
            # Get LLM review
            llm_review = self._get_llm_review(
                original_code,
                optimized_code,
                optimization_description,
                results
            )
            results["llm_review"] = llm_review
            
            # Overall recommendation
            results["recommendation"] = self._generate_recommendation(results)
            
            self.logger.info(f"Validation complete: {results['recommendation']}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return {
                "error": str(e),
                "syntax_valid": False,
                "functionally_equivalent": False,
                "performance_improved": False,
                "safe_to_apply": False,
                "recommendation": "REJECT"
            }
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate code syntax."""
        self.logger.debug("Validating syntax")
        
        try:
            compile(code, '<string>', 'exec')
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Line {e.lineno}: {e.msg}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _check_functional_equivalence(
        self,
        original: str,
        optimized: str
    ) -> Dict[str, Any]:
        """Check if optimized code is functionally equivalent."""
        self.logger.debug("Checking functional equivalence")
        
        # For now, we can't fully verify equivalence without test cases
        # This is a placeholder that does basic checks
        
        try:
            # Check if both codes have similar structure
            import ast
            
            original_tree = ast.parse(original)
            optimized_tree = ast.parse(optimized)
            
            original_funcs = [n.name for n in ast.walk(original_tree) if isinstance(n, ast.FunctionDef)]
            optimized_funcs = [n.name for n in ast.walk(optimized_tree) if isinstance(n, ast.FunctionDef)]
            
            # Basic check: same function names
            same_functions = set(original_funcs) == set(optimized_funcs)
            
            return {
                "equivalent": same_functions,
                "method": "structural_comparison",
                "confidence": "low",
                "note": "Full equivalence requires test cases"
            }
            
        except Exception as e:
            return {
                "equivalent": False,
                "error": str(e),
                "method": "failed",
                "confidence": "none"
            }
    
    def _compare_performance(
        self,
        original: str,
        optimized: str
    ) -> Dict[str, Any]:
        """Compare performance of original vs optimized code."""
        self.logger.debug("Comparing performance")
        
        # Check if code is safe to execute
        if not self.executor.is_safe(original) or not self.executor.is_safe(optimized):
            return {
                "improved": False,
                "skipped": True,
                "reason": "Code unsafe for execution"
            }
        
        try:
            # This is a simplified comparison
            # In production, you'd want more sophisticated benchmarking
            
            original_result = self.executor.execute_with_timeout(original, timeout=5)
            optimized_result = self.executor.execute_with_timeout(optimized, timeout=5)
            
            if not original_result["success"] or not optimized_result["success"]:
                return {
                    "improved": False,
                    "skipped": True,
                    "reason": "Execution failed"
                }
            
            # Compare execution times if available
            original_time = original_result.get("execution_time", 0)
            optimized_time = optimized_result.get("execution_time", 0)
            
            improved = optimized_time < original_time
            improvement_percent = 0
            
            if original_time > 0:
                improvement_percent = ((original_time - optimized_time) / original_time) * 100
            
            return {
                "improved": improved,
                "original_time": original_time,
                "optimized_time": optimized_time,
                "improvement_percent": round(improvement_percent, 2),
                "skipped": False
            }
            
        except Exception as e:
            return {
                "improved": False,
                "error": str(e),
                "skipped": True
            }
    
    def _check_safety(self, code: str) -> Dict[str, Any]:
        """Check if code is safe to apply."""
        self.logger.debug("Checking safety")
        
        try:
            is_safe = self.executor.is_safe(code)
            
            if not is_safe:
                return {
                    "safe": False,
                    "reason": "Code contains potentially unsafe operations"
                }
            
            return {
                "safe": True,
                "reason": "No obvious safety concerns detected"
            }
            
        except Exception as e:
            return {
                "safe": False,
                "reason": f"Safety check failed: {str(e)}"
            }
    
    def _get_llm_review(
        self,
        original: str,
        optimized: str,
        description: str,
        validation_results: Dict
    ) -> str:
        """Get LLM review of the optimization."""
        self.logger.debug("Getting LLM review")
        
        try:
            user_message = VALIDATOR_USER_PROMPT.format(
                original_code=original[:1000],
                optimized_code=optimized[:1000],
                optimization_description=description,
                syntax_valid=validation_results["syntax_valid"],
                safe=validation_results.get("validation_details", {}).get("safety", {}).get("safe", False)
            )
            
            messages = [
                SystemMessage(content=VALIDATOR_SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            self.logger.error(f"LLM review failed: {str(e)}")
            return "LLM review unavailable"
    
    def _generate_recommendation(self, results: Dict) -> str:
        """Generate overall recommendation."""
        if not results["syntax_valid"]:
            return "REJECT - Syntax errors"
        
        if not results["safe_to_apply"]:
            return "REJECT - Safety concerns"
        
        if results["performance_improved"] and results["functionally_equivalent"]:
            return "APPROVE - Safe and beneficial"
        
        if results["performance_improved"]:
            return "REVIEW - Performance improved but verify equivalence"
        
        if results["functionally_equivalent"]:
            return "REVIEW - Functionally equivalent but verify performance"
        
        return "REVIEW - Manual verification recommended"
    
    def batch_validate(
        self,
        original_code: str,
        optimizations: List[Dict]
    ) -> List[Dict]:
        """
        Validate multiple optimizations.
        
        Args:
            original_code: Original code
            optimizations: List of optimization suggestions
            
        Returns:
            List of validation results
        """
        self.logger.info(f"Batch validating {len(optimizations)} optimizations")
        
        results = []
        for opt in optimizations:
            result = self.validate(
                original_code,
                opt.get("optimized_code", ""),
                opt.get("description", "")
            )
            result["optimization_title"] = opt.get("title", "Unknown")
            results.append(result)
        
        return results