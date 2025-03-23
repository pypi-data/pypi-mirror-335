# Copyright 2024-2025 Sébastien Demanou. All Rights Reserved.
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
# ==============================================================================
from typing import Any
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel

from .document import Document
from .document import UserMeta

SettingValue = TypeVar('SettingValue')


class Setting(BaseModel, Generic[SettingValue]):
  value: SettingValue


class SettingMeta(UserMeta):
  property: str
  device: str | None = None


GenericSetting = Setting[Any]
SettingDocumentType = Document[GenericSetting, SettingMeta]
SettingDocument = SettingDocumentType.create_alias_from_base_meta(
  data_cls=Setting, meta_cls=SettingMeta
)
