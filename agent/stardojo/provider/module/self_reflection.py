from typing import List, Dict, Any
import json
from copy import deepcopy

from stardojo.provider import BaseModuleProvider, BaseProvider
from stardojo.utils.json_utils import parse_semi_formatted_text
from stardojo.log import Logger
from stardojo.config import Config
from stardojo.memory import LocalMemory

config = Config()
logger = Logger()


class SelfReflectionProvider(BaseModuleProvider):

    def __init__(self,
                 *args,
                 template_path: str,
                 llm_provider: Any = None,
                 gm: Any = None,
                 **kwargs):

        super(SelfReflectionProvider, self).__init__(template_path = template_path, **kwargs)

        self.template_path = template_path
        self.llm_provider = llm_provider
        self.gm = gm
        self.memory = LocalMemory()


    @BaseModuleProvider.debug
    @BaseModuleProvider.error
    @BaseModuleProvider.write
    def __call__(self,
                 *args,
                 **kwargs):

        params = deepcopy(self.memory.working_area)

        self._check_input_keys(params)

        message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=params)
        logger.debug(f'{logger.UPSTREAM_MASK}{json.dumps(message_prompts, ensure_ascii=False)}\n')

        response = {}
        try:
            response, info = self.llm_provider.create_completion(message_prompts)
            logger.debug(f'{logger.DOWNSTREAM_MASK}{response}\n')

            # Convert the response to dict
            response = parse_semi_formatted_text(response)

        except Exception as e:
            logger.error(f"Response of image description is not in the correct format: {e}, retrying...")

        self._check_output_keys(response)

        del params

        return response


class RDR2SelfReflectionProvider(BaseProvider):
    def __init__(self,
                 *args,
                 planner,
                 gm,
                 **kwargs):
        super(RDR2SelfReflectionProvider, self).__init__()
        self.planner = planner
        self.gm = gm
        self.memory = LocalMemory()


    def __call__(self, *args, **kwargs):

        params = deepcopy(self.memory.working_area)

        data = self.planner.self_reflection(input=params)

        response = data['res_dict']

        del params

        return response


class StardewSelfReflectionProvider(BaseProvider):

    def __init__(self,
                 *args,
                 planner,
                 gm,
                 **kwargs):

        super(StardewSelfReflectionProvider, self).__init__()

        self.planner = planner
        self.gm = gm
        self.memory = LocalMemory()


    def __call__(self, *args, **kwargs):

        params = deepcopy(self.memory.working_area)

        data = self.planner.self_reflection(input=params)

        response = data['res_dict']

        del params

        return response
