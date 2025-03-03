from typing import List, Optional
import dspy
from openai import AsyncOpenAI
from .config import settings
import os

class AsyncOpenAIWrapper:
    """Wrapper for AsyncOpenAI client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    async def forward(self, prompt: str, **kwargs):
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

class CodeAnalyzer(dspy.Module):
    """DSPy module for analyzing code and providing insights."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.predictor = AsyncOpenAIWrapper(api_key=api_key or settings.OPENAI_API_KEY)
    
    async def forward(self, code: str) -> dspy.Prediction:
        """Analyze code and provide insights."""
        prompt = """Analyze the following code and provide:
        1. A brief description of what it does
        2. Its time complexity
        3. Suggestions for improvement
        
        Code:
        {code}
        """.format(code=code)
        
        result = await self.predictor.forward(prompt)
        return dspy.Prediction(
            analysis=result,
            complexity="O(1)",  # This would be parsed from the result
            suggestions=["Add tests"]  # This would be parsed from the result
        )

    async def analyze_code(self, code: str) -> str:
        """Analyze code and provide feedback."""
        prompt = f"Analyze this code:\n{code}"
        return await self.predictor.forward(prompt)

class CodeGenerator(dspy.Module):
    """DSPy module for generating code based on requirements."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.predictor = AsyncOpenAIWrapper(api_key=api_key or settings.OPENAI_API_KEY)
    
    async def forward(self, requirements: List[str]) -> dspy.Prediction:
        """Generate code based on requirements."""
        prompt = """Generate code that meets these requirements:
        {requirements}
        
        Provide:
        1. The implementation
        2. An explanation of how it works
        """.format(requirements="\n".join(requirements))
        
        result = await self.predictor.forward(prompt)
        return dspy.Prediction(
            code=result,
            explanation="Implementation explanation"  # This would be parsed from the result
        )

    async def generate_code(self, description: str) -> str:
        """Generate code based on description."""
        prompt = f"Generate code for:\n{description}"
        return await self.predictor.forward(prompt)

class TestGenerator(dspy.Module):
    """DSPy module for generating tests for code."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.predictor = AsyncOpenAIWrapper(api_key=api_key or settings.OPENAI_API_KEY)
    
    async def forward(self, code: str) -> dspy.Prediction:
        """Generate tests for the given code."""
        prompt = """Write comprehensive tests for this code:
        {code}
        
        Provide:
        1. The test implementation using pytest
        2. A list of test cases covered
        """.format(code=code)
        
        result = await self.predictor.forward(prompt)
        return dspy.Prediction(
            test_code=result,
            test_cases=["basic test"]  # This would be parsed from the result
        )

    async def generate_test(self, code: str) -> str:
        """Generate tests for given code."""
        prompt = f"Generate tests for:\n{code}"
        return await self.predictor.forward(prompt)
