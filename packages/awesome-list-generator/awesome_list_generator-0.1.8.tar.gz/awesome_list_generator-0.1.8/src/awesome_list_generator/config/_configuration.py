import pydantic

import awesome_list_generator as alg


class Configuration(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_enum_values=True)
    format: alg.Format = alg.Format.MARKDOWN
