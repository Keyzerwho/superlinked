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

from beartype.typing import Any
from typing_extensions import override

from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.space.config.embedding.embedding_config import (
    EmbeddingConfig,
)
from superlinked.framework.common.space.config.embedding.embedding_type import (
    EmbeddingType,
)


class CustomEmbeddingConfig(EmbeddingConfig[Vector]):
    def __init__(self, vector_length: int) -> None:
        super().__init__(EmbeddingType.CUSTOM, Vector)
        self.vector_length = vector_length
        if self.vector_length < 1:
            raise ValueError("Vector length must be greater than 0.")

    @property
    @override
    def length(self) -> int:
        return self.vector_length

    @override
    def to_dict(self) -> dict[str, Any]:
        return super().to_dict() | {
            "vector_length": self.vector_length,
        }