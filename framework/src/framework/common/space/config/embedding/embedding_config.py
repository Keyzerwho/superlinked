# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass

from beartype.typing import Any, Generic, TypeVar

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.interface.has_default_vector import HasDefaultVector
from superlinked.framework.common.space.config.embedding.embedding_type import (
    EmbeddingType,
)

EmbeddingInputT = TypeVar("EmbeddingInputT", bound=PythonTypes)


@dataclass(frozen=True)
class EmbeddingConfig(HasDefaultVector, Generic[EmbeddingInputT]):
    embedding_type: EmbeddingType
    embedding_input_type: type[EmbeddingInputT]

    def should_return_default(self, context: ExecutionContext) -> bool:
        return context.should_load_default_node_input

    def to_dict(self) -> dict[str, Any]:
        return {
            "embedding_type": self.embedding_type.value,
            "embedding_input_type": self.embedding_input_type.__name__,
        }


EmbeddingConfigT = TypeVar("EmbeddingConfigT", bound=EmbeddingConfig)