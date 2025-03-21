import asyncio
import time
from fastapi import HTTPException, status
import pandas as pd
from typing import List
from loguru import logger
from phoenix.evals import (
    HallucinationEvaluator,
    QAEvaluator,
    ToxicityEvaluator,
    OpenAIModel,
    run_evals,
)

from ragmeter.adapters.arize.models import (
    ArizeEvalGeneration,
    ArizeEvalMetric,
    ArizeEvalRetrieval,
    ArizeEvaluationResponse,
)
from ragmeter.adapters.models import RAGMeterRequest


async def rag_arize_evaluation(
    request: RAGMeterRequest, retrieval_results=None, response_results=None
) -> List[ArizeEvaluationResponse]:
    try:

        st = time.time()
        logger.info("Evaluating with Arize in batch mode...")

        eval_model = OpenAIModel(model="gpt-4o-mini")
        hallucination_evaluator = HallucinationEvaluator(eval_model)
        qa_correctness_evaluator = QAEvaluator(eval_model)
        toxicity_evaluator = ToxicityEvaluator(eval_model)

        # Prepare a batch DataFrame for evaluation
        records = [
            {"input": question, "reference": answer, "output": generated}
            for question, answer, generated in zip(
                request.questions, request.ground_truth, request.llm_answers
            )
        ]
        df_batch = pd.DataFrame(records)

        # Run evaluations on the full batch asynchronously
        hallucination_df, qa_correctness_df, toxicity_df = await asyncio.to_thread(
            run_evals,
            dataframe=df_batch,
            evaluators=[
                hallucination_evaluator,
                qa_correctness_evaluator,
                toxicity_evaluator,
            ],
        )

        # Convert results into structured responses
        results = [
            ArizeEvaluationResponse(
                question=question,
                expected_answer=answer,
                generated_answer=generated,
                retrieved_contexts=retrieved_chunk,
                generation=ArizeEvalGeneration(
                    hallucination_eval=ArizeEvalMetric(
                        label=hallucination_df.iloc[i]["label"],
                        score=hallucination_df.iloc[i]["score"],
                        explanation=hallucination_df.iloc[i].get("explanation", ""),
                    ),
                    qa_correctness_eval=ArizeEvalMetric(
                        label=qa_correctness_df.iloc[i]["label"],
                        score=qa_correctness_df.iloc[i]["score"],
                        explanation=qa_correctness_df.iloc[i].get("explanation", ""),
                    ),
                    toxicity_eval=ArizeEvalMetric(
                        label=toxicity_df.iloc[i]["label"],
                        score=toxicity_df.iloc[i]["score"],
                        explanation=toxicity_df.iloc[i].get("explanation", ""),
                    ),
                ),
                retrieval=ArizeEvalRetrieval(),
            )
            for i, (question, answer, generated, retrieved_chunk) in enumerate(
                zip(
                    request.questions,
                    request.ground_truth,
                    request.llm_answers,
                    request.retrieved_chunks,
                )
            )
        ]

        logger.info(f"Arize batch evaluation completed in {(time.time() - st):.2f}s")
        return results

    except Exception as e:
        logger.error(f"{ERROR_MESSAGE_UNEXPECTED_ERROR_OCCURRED}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
