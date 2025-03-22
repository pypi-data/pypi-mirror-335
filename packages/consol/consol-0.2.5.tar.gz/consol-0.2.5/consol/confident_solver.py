import enum
import typing
import sys

import pydantic
import langchain_openai
import langchain_ollama
import langchain_google_genai
import langchain_core
import tqdm.auto
import pandas as pd

from .output_formats import AbstractOutput, ReasonedMixin, FloatOutput, ABCDEFOutput, ABCDOutput, YesNoOutput
from .confidence_models import AbstractConfidenceModel, MsprtConfidenceModel, SprtConfidenceModel, PValueConfidenceModel, BayesianPosteriorConfidenceModel, VoteConfidenceModel

class LlmModelEnum(enum.StrEnum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O3_MINI_LOW = "o3-mini-low"
    O3_MINI_MEDIUM = "o3-mini-medium"
    O3_MINI_HIGH = "o3-mini-high"
    OLLAMA_LLAMA3_1_8B = "ollama:llama3.1:8b"
    OLLAMA_QWQ_32B = "ollama:qwq:32b"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"


class ConfidenceModelEnum(enum.StrEnum):
    Msprt = "msprt"
    Sprt = "sprt"
    Pvalue = "pvalue"
    BayesianPosterior = "bayesian_posterior"
    Vote40 = "vote40"
    Vote1 = "vote1"

class OutputTypeEnum(enum.StrEnum):
    Float = "float"
    Abcdef = "abcdef"
    YesNo = "yesno"
    Abcd = "abcd"

class ConfidentSolverConfig(pydantic.BaseModel):
    llm_model: LlmModelEnum

class ConfidentSolver:
    def __init__(
        self,
        llm_model: LlmModelEnum,
        confidence_model: typing.Union[ConfidenceModelEnum, AbstractConfidenceModel],
        output_schema: typing.Union[OutputTypeEnum, AbstractOutput],
    ):
        self.config = ConfidentSolverConfig(
            llm_model=llm_model,
        )

        if confidence_model == ConfidenceModelEnum.Msprt:
            self.confidence_model = MsprtConfidenceModel()
        elif confidence_model == ConfidenceModelEnum.Sprt:
            self.confidence_model = SprtConfidenceModel()
        elif confidence_model == ConfidenceModelEnum.Pvalue:
            self.confidence_model = PValueConfidenceModel()
        elif confidence_model == ConfidenceModelEnum.BayesianPosterior:
            self.confidence_model = BayesianPosteriorConfidenceModel()
        elif confidence_model == ConfidenceModelEnum.Vote40:
            self.confidence_model = VoteConfidenceModel()
        elif confidence_model == ConfidenceModelEnum.Vote1:
            self.confidence_model = VoteConfidenceModel(max_trials=1)
        elif isinstance(confidence_model, AbstractConfidenceModel):
            self.confidence_model = confidence_model
        else:
            raise ValueError(f"Unknown Confidence Model: {confidence_model}")

        if output_schema == OutputTypeEnum.Float:
            output_schema = FloatOutput
        elif output_schema == OutputTypeEnum.Abcdef:
            output_schema = ABCDEFOutput
        elif output_schema == OutputTypeEnum.YesNo:
            output_schema = YesNoOutput
        elif output_schema == OutputTypeEnum.Abcd:
            output_schema = ABCDOutput
        elif isinstance(output_schema, type) and issubclass(output_schema, AbstractOutput):
            pass
        else:
            raise ValueError(f"Unknown Output Schema: {output_schema}")

        if llm_model in [LlmModelEnum.O3_MINI_LOW, LlmModelEnum.O3_MINI_MEDIUM, LlmModelEnum.O3_MINI_HIGH]:
            llm = langchain_openai.ChatOpenAI(
                model="o3-mini",
                reasoning_effort=llm_model.split("-")[-1],
            )
        elif llm_model in [LlmModelEnum.GPT_4O, LlmModelEnum.GPT_4O_MINI]:
            llm = langchain_openai.ChatOpenAI(
                model=llm_model,
            )
            output_schema = type("ReasonedOutputSchema", (output_schema, ReasonedMixin), {})
        elif llm_model in [LlmModelEnum.OLLAMA_LLAMA3_1_8B]:
            llm = langchain_ollama.ChatOllama(
                model=llm_model.split(":", 1)[-1],
            )
            output_schema = type("ReasonedOutputSchema", (output_schema, ReasonedMixin), {})
        elif llm_model in [LlmModelEnum.OLLAMA_QWQ_32B]:
            llm = langchain_ollama.ChatOllama(
                model=llm_model.split(":", 1)[-1],
                num_ctx=32000,
            )
        elif llm_model in [LlmModelEnum.GEMINI_2_0_FLASH, LlmModelEnum.GEMINI_2_0_FLASH_LITE]:
            llm = langchain_google_genai.ChatGoogleGenerativeAI(
                model=llm_model
            )
            output_schema = type("ReasonedOutputSchema", (output_schema, ReasonedMixin), {})
        else:
            raise ValueError(f"Unknown Model: {llm_model}")

        self.llm_with_structured_output = llm.with_structured_output(output_schema, include_raw=True)


    def invoke(self, input, debug=False, **kwargs):
        messages = self._prepare_messages(input)
        max_trials = self.confidence_model.config.max_trials
        total_raw_outputs = []
        with tqdm.auto.tqdm(total=max_trials) as pbar:
            while True:
                first, second = self._get_top_two_answers(total_raw_outputs)
                trials = self._determine_trials(first, second, max_trials, len(total_raw_outputs))
                if trials == 0:
                    pbar.close()
                    break
                raw_outputs = self._collect_raw_outputs(messages, trials, **kwargs)
                total_raw_outputs += raw_outputs
                pbar.update(trials)
        df = self._create_dataframe(total_raw_outputs)
        if debug:
            return df
        return df['answer'].mode().iloc[0]

    def _prepare_messages(self, input):
        if isinstance(input, str):
            return [langchain_core.messages.HumanMessage(input)]
        return input

    def _get_top_two_answers(self, total_raw_outputs):
        total_ss = pd.Series([x['parsed'].answer for x in total_raw_outputs]).value_counts()
        two = total_ss.sort_values(ascending=False).head(2).to_list()
        while len(two) < 2:
            two += [0]
        return two[0], two[1]

    def _determine_trials(self, first, second, max_trials, current_trials):
        for trials in range(0, max_trials + 1):
            if first + trials == 0:
                continue
            if self.confidence_model.test(first + trials, second):
                break
        if trials >= max_trials - current_trials:
            trials = max_trials - current_trials
        return trials

    def _collect_raw_outputs(self, messages, trials, **kwargs):
        raw_outputs = []
        while len(raw_outputs) < trials:
            try:
                k = trials - len(raw_outputs)
                partial_raw_outputs = self.llm_with_structured_output.batch([messages] * k, **kwargs)
                partial_raw_outputs = [x for x in partial_raw_outputs if x['parsed']]
                raw_outputs += partial_raw_outputs
            except Exception as e:
                print(f"Unknown error during trial {len(raw_outputs)}/{trials} with input: {messages[0].content}", e, file=sys.stderr)
                continue
        return raw_outputs

    def _create_dataframe(self, total_raw_outputs):
        token_usage = [x['raw'].usage_metadata['output_tokens'] for x in total_raw_outputs]

        return pd.DataFrame({
            'answer': [x['parsed'].answer for x in total_raw_outputs],
            'token_usage': token_usage,
        })
