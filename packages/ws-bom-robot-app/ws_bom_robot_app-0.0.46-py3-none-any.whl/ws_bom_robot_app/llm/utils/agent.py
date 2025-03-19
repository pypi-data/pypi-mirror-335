import os
from langchain_core.embeddings import Embeddings
from ws_bom_robot_app.llm.models.api import LlmRules
from ws_bom_robot_app.llm.utils.print import HiddenPrints
from ws_bom_robot_app.llm.vector_store.db.manager import VectorDbManager
import warnings

async def get_rules(embeddings: Embeddings, rules: LlmRules, input: str) -> str:
  with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=Warning)
    if any([input=="",rules is None,rules and rules.vector_db == "",rules and not os.path.exists(rules.vector_db)]):
      return ""
    rules_prompt = ""
    rules_doc = await VectorDbManager.get_strategy(rules.vector_type).invoke(embeddings, rules.vector_db,input,search_type="similarity_score_threshold", search_kwargs={"score_threshold": rules.threshold}) #type: ignore
    if len(rules_doc) > 0:
      rules_prompt = "\nFollow this rules: \n RULES: \n"
      for rule_doc in rules_doc:
        rules_prompt += "- " + rule_doc.page_content + "\n"
    return rules_prompt
