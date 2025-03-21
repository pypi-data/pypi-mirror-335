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
from collections.abc import Callable
from typing import Any
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from .document import Document
from .document import UserMeta


class NotificationAction(BaseModel):
  """A class representing an action associated with a notification.

  Attributes:
    label (str): The label or text of the action.
    trigger (Callable[[], None]): The trigger function that will be called when the action is activated.
  """

  label: str
  trigger: Callable[[], None]


class Notification(BaseModel):
  """
  A class representing a notification.

  Attributes:
      summary (str): The summary of the notification.
      body (str): The body text of the notification.
      icon (str): The resolved file path to the icon for the notification.
      sound (str | None): The filename of the notification sound, or None if no sound is specified.
      actions (list[NotificationAction]): The list of actions for the notification.
      timeout (int): The timeout duration for the notification in milliseconds.
                      0: The notification never expires.
                      Positive integer: The timeout time in milliseconds since the display of the notification
                          at which the notification should automatically close.
      urgency (Literal[0, 1, 2]): The urgency level of the notification.
                      0: Low
                      1: Normal
                      2: Critical.
      on_close (Callable[[], Any] | None): The callback function to be called when the notification is closed,
                                            or None if no callback is specified.
  """

  summary: str
  body: str
  icon: str | None = None
  sound: str | None = None
  actions: list[NotificationAction] = Field(default_factory=list)
  timeout: int = 5000  # 5 seconds
  urgency: Literal[0, 1, 2] = 0
  on_close: Callable[[], Any] | None = None

  def __str__(self):
    return self.body


class Announcement(BaseModel):
  """A class representing an announcement.

  Attributes:
    icon (str | None): The icon associated with the announcement, or None if no icon is specified.
    message (str): The announcement message.
    sound (str | None): The filename of the notification sound, or None if no sound is specified.
    repeat (int): The number of times the announcement should be repeated. Default is 1.
  """

  message: str
  icon: str | None = None
  sound: str | None = None
  repeat: int = 1


class Track(BaseModel):
  media_url: str
  title: str | None = None
  artist_name: str | None = None
  album_title: str | None = None
  album_artist: str | None = None
  description: str | None = None
  artwork_url: str | None = None


class PrintTextAction(BaseModel):
  type: Literal['print'] = 'print'
  text: str


class PrintErrorAction(BaseModel):
  type: Literal['error'] = 'error'
  kind: Literal['unexpected:error', 'processing:not-understood', 'skill:disabled']
  data: dict[str, Any] | None = None


class RequestAdditionalInfoAction(BaseModel):
  type: Literal['system:request'] = 'system:request'
  text: str
  context: dict = Field(default_factory=dict)


class PlayAction(BaseModel):
  type: Literal['media:play'] = 'media:play'
  tracks: list[Track]


class PauseAction(BaseModel):
  type: Literal['media:pause'] = 'media:pause'


class ResumeAction(BaseModel):
  type: Literal['media:resume'] = 'media:resume'


class StopAction(BaseModel):
  type: Literal['media:stop'] = 'media:stop'


class MuteAction(BaseModel):
  type: Literal['media:mute'] = 'media:mute'


class UnmuteAction(BaseModel):
  type: Literal['media:unmute'] = 'media:unmute'


class SetVolumeAction(BaseModel):
  type: Literal['media:set-volume'] = 'media:set-volume'
  value: int


class NextAction(BaseModel):
  type: Literal['media:next'] = 'media:next'


class PreviousAction(BaseModel):
  type: Literal['media:previous'] = 'media:previous'


class NotifyAction(BaseModel):
  type: Literal['system:notify'] = 'system:notify'
  notification: Notification


class AnnounceAction(BaseModel):
  type: Literal['system:announcement'] = 'system:announcement'
  announcement: Announcement


class DoneAction(BaseModel):
  type: Literal['request:done'] = 'request:done'


class CancelAction(BaseModel):
  type: Literal['request:cancel'] = 'request:cancel'


UnexpectedErrorType = Literal['error']
InternalProcessingStart = Literal['processing:start']
InternalProcessingEnd = Literal['processing:end']

ActionType = Literal[
  'print',
  'error',
  'system:request',
  'media:play',
  'media:pause',
  'media:resume',
  'media:stop',
  'media:mute',
  'media:unmute',
  'media:set-volume',
  'media:next',
  'media:previous',
  'system:notify',
  'system:announcement',
  'request:done',
  'request:cancel',
]


ProcessingAction = (
  PrintTextAction
  | PrintErrorAction
  | PlayAction
  | PauseAction
  | ResumeAction
  | StopAction
  | MuteAction
  | UnmuteAction
  | SetVolumeAction
  | NextAction
  | PreviousAction
  | NotifyAction
  | AnnounceAction
  | RequestAdditionalInfoAction
  | DoneAction
  | CancelAction
)

Actions = list[ProcessingAction]


class ClassificationPrediction(BaseModel):
  """
  A class representing a prediction for a classification task.

  Attributes:
    label (str): The predicted label.
    accuracy (float): The predicted accuracy.
  """

  label: str
  accuracy: float


class Request(BaseModel):
  type: Literal['request']
  processed_text: str
  prediction: ClassificationPrediction | None
  actions: Actions


DetectionType = Literal['wakeword', 'sound']


class Detection(BaseModel):
  type: DetectionType
  sound: str
  score: float


class ActivityMeta(UserMeta, BaseModel):
  """
  A class representing metadata for an activity.
  """

  device: str


DetectionDocumentType = Document[Detection, ActivityMeta]
DetectionDocument = DetectionDocumentType.create_alias_from_user_meta(
  data_cls=Detection, meta_cls=ActivityMeta
)

RequestDocumentType = Document[Request, ActivityMeta]
RequestDocument = RequestDocumentType.create_alias_from_user_meta(
  data_cls=Request, meta_cls=ActivityMeta
)
