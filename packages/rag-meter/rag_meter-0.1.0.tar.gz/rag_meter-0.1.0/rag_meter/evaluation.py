import asyncio
from loguru import logger
from adapters.ragas.ragas_adapter import RAGASEvaluator
from adapters.deepeval.deepeval_adapter import DeepEvalRAGEvaluator
from adapters.models import RAGMeterRequest


async def run_simulation(request: RAGMeterRequest):

    results = await DeepEvalRAGEvaluator(request=request).evaluate()
    # results = await RAGASEvaluator(request=request).evaluate()
    logger.info(results)


# Main entry point for the script
if __name__ == "__main__":
    # Create a RAGMeterRequest instance with necessary data
    request = RAGMeterRequest(
        llm_answers=["Artificial Intelligence is...", "Neural networks are..."],
        questions=["What is AI?", "Explain neural networks."],
        retrieved_chunks=[
            ["Some context for AI -1", "Some context for AI -2"],
            ["context for neural networks1", "context for neural networks2"],
        ],
        ground_truth=["Artificial Intelligence refers to...", "A neural network is..."],
        frameworks=["ragas"],
    )

    # Run the simulation using asyncio
    asyncio.run(run_simulation(request))
