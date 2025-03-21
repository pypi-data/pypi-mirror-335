from .teamschannels import (
    create_channel as _create_channel,
    create_channel_async as _create_channel_async,
    list_channels as _list_channels,
    list_channels_async as _list_channels_async,
)
from ..models.create_channel_request import CreateChannelRequest
from ..models.create_channel_response import CreateChannelResponse
from ..models.default_error import DefaultError
from typing import cast
from ..models.default_error import DefaultError
from ..models.list_channels import ListChannels
from typing import cast
from .individual_chats_messages_v2 import (
    create_individual_chat_message as _create_individual_chat_message,
    create_individual_chat_message_async as _create_individual_chat_message_async,
)
from ..models.create_individual_chat_message_body import CreateIndividualChatMessageBody
from ..models.create_individual_chat_message_request import CreateIndividualChatMessageRequest
from ..models.create_individual_chat_message_response import CreateIndividualChatMessageResponse
from ..models.default_error import DefaultError
from typing import cast
from .one_on_one_chat import (
    create_one_on_one_chat as _create_one_on_one_chat,
    create_one_on_one_chat_async as _create_one_on_one_chat_async,
)
from ..models.create_one_on_one_chat_request import CreateOneOnOneChatRequest
from ..models.create_one_on_one_chat_response import CreateOneOnOneChatResponse
from ..models.default_error import DefaultError
from typing import cast
from .me_events import (
    create_online_teams_meeting as _create_online_teams_meeting,
    create_online_teams_meeting_async as _create_online_teams_meeting_async,
)
from ..models.create_online_teams_meeting_request import CreateOnlineTeamsMeetingRequest
from ..models.create_online_teams_meeting_response import CreateOnlineTeamsMeetingResponse
from ..models.default_error import DefaultError
from typing import cast
from .download_recording_transcript import (
    download_meeting_transcript_recording as _download_meeting_transcript_recording,
    download_meeting_transcript_recording_async as _download_meeting_transcript_recording_async,
)
from ..models.default_error import DefaultError
from ..models.download_meeting_transcript_recording_response import DownloadMeetingTranscript/RecordingResponse
from ..types import File
from io import BytesIO
from typing import cast
from .normalized_teamschannels import (
    get_channel_by_name as _get_channel_by_name,
    get_channel_by_name_async as _get_channel_by_name_async,
)
from ..models.default_error import DefaultError
from ..models.get_channel_by_name_response import GetChannelByNameResponse
from typing import cast
from .team_by_name import (
    get_team_by_name as _get_team_by_name,
    get_team_by_name_async as _get_team_by_name_async,
)
from ..models.default_error import DefaultError
from ..models.get_team_by_name_response import GetTeamByNameResponse
from typing import cast
from .curated_online_meetings import (
    getonline_meetings as _getonline_meetings,
    getonline_meetings_async as _getonline_meetings_async,
)
from ..models.default_error import DefaultError
from ..models.getonline_meetings_response import GetonlineMeetingsResponse
from typing import cast
from .teamschannelsmembers import (
    invite_channel_member as _invite_channel_member,
    invite_channel_member_async as _invite_channel_member_async,
)
from ..models.default_error import DefaultError
from ..models.invite_channel_member_request import InviteChannelMemberRequest
from ..models.invite_channel_member_response import InviteChannelMemberResponse
from typing import cast
from .normalised_teamsmembers import (
    invite_team_member as _invite_team_member,
    invite_team_member_async as _invite_team_member_async,
)
from ..models.default_error import DefaultError
from ..models.invite_team_member_request import InviteTeamMemberRequest
from ..models.invite_team_member_response import InviteTeamMemberResponse
from typing import cast
from .me_onlinemeetings_recordings import (
    list_all_recordings as _list_all_recordings,
    list_all_recordings_async as _list_all_recordings_async,
)
from ..models.default_error import DefaultError
from ..models.list_all_recordings import ListAllRecordings
from typing import cast
from .me_onlinemeetings_transcripts import (
    list_all_transcripts as _list_all_transcripts,
    list_all_transcripts_async as _list_all_transcripts_async,
)
from ..models.default_error import DefaultError
from ..models.list_all_transcripts import ListAllTranscripts
from typing import cast
from .list_normalised_teamschannelsmessages import (
    list_channel_messages as _list_channel_messages,
    list_channel_messages_async as _list_channel_messages_async,
)
from ..models.default_error import DefaultError
from ..models.list_channel_messages import ListChannelMessages
from typing import cast
from .list_normalised_chatsmessages import (
    list_chat_messages as _list_chat_messages,
    list_chat_messages_async as _list_chat_messages_async,
)
from ..models.default_error import DefaultError
from ..models.list_chat_messages import ListChatMessages
from typing import cast
from .list_normalised_teamsmembers import (
    list_team_members as _list_team_members,
    list_team_members_async as _list_team_members_async,
)
from ..models.default_error import DefaultError
from ..models.list_team_members import ListTeamMembers
from typing import cast
from .normalised_teams_channels_messages_replies_v2 import (
    reply_to_channel_message as _reply_to_channel_message,
    reply_to_channel_message_async as _reply_to_channel_message_async,
)
from ..models.default_error import DefaultError
from ..models.reply_to_channel_message_body import ReplyToChannelMessageBody
from ..models.reply_to_channel_message_request import ReplyToChannelMessageRequest
from ..models.reply_to_channel_message_response import ReplyToChannelMessageResponse
from typing import cast
from .normalised_teams_channels_messages_v2 import (
    send_channel_message as _send_channel_message,
    send_channel_message_async as _send_channel_message_async,
)
from ..models.default_error import DefaultError
from ..models.send_channel_message_body import SendChannelMessageBody
from ..models.send_channel_message_request import SendChannelMessageRequest
from ..models.send_channel_message_response import SendChannelMessageResponse
from typing import cast
from .normalised_chats_messages_v2 import (
    send_chat_message as _send_chat_message,
    send_chat_message_async as _send_chat_message_async,
)
from ..models.default_error import DefaultError
from ..models.send_chat_message_body import SendChatMessageBody
from ..models.send_chat_message_request import SendChatMessageRequest
from ..models.send_chat_message_response import SendChatMessageResponse
from typing import cast
from .bot_conversations import (
    send_message_to_channel_as_bot as _send_message_to_channel_as_bot,
    send_message_to_channel_as_bot_async as _send_message_to_channel_as_bot_async,
)
from ..models.default_error import DefaultError
from ..models.send_message_to_channel_as_bot_request import SendMessageToChannelAsBotRequest
from ..models.send_message_to_channel_as_bot_response import SendMessageToChannelAsBotResponse
from typing import cast

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx

class MicrosoftTeams:
    def __init__(self, *, instance_id:str, client: httpx.Client):
        base_url = str(client.base_url).rstrip('/')
        new_headers = {k: v for k, v in client.headers.items() if k not in ['content-type']}
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = Client(
            base_url="", # this will be overridden by the base_url in the Client constructor
        ).set_httpx_client(new_client).set_async_httpx_client(new_client_async)

    def create_channel(self, team_id: str,team_id_lookup: Any,*,
body: CreateChannelRequest,
) -> Optional[Union[CreateChannelResponse, DefaultError]]:
        return _create_channel(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,body=body,
)

    async def create_channel_async(self, team_id: str,team_id_lookup: Any,*,
body: CreateChannelRequest,
) -> Optional[Union[CreateChannelResponse, DefaultError]]:
        return await _create_channel_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,body=body,
)
    def list_channels(self, team_id: str,team_id_lookup: Any,*,
expand: Optional[str] = None,where: Optional[str] = None,filter_: Optional[str] = None,select: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListChannels']]]:
        return _list_channels(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,expand=expand,where=where,filter_=filter_,select=select,)

    async def list_channels_async(self, team_id: str,team_id_lookup: Any,*,
expand: Optional[str] = None,where: Optional[str] = None,filter_: Optional[str] = None,select: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListChannels']]]:
        return await _list_channels_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,expand=expand,where=where,filter_=filter_,select=select,)
    def create_individual_chat_message(self, *,
body: CreateIndividualChatMessageBody,
) -> Optional[Union[CreateIndividualChatMessageResponse, DefaultError]]:
        return _create_individual_chat_message(client=self.client, body=body,
)

    async def create_individual_chat_message_async(self, *,
body: CreateIndividualChatMessageBody,
) -> Optional[Union[CreateIndividualChatMessageResponse, DefaultError]]:
        return await _create_individual_chat_message_async(client=self.client, body=body,
)
    def create_one_on_one_chat(self, *,
body: CreateOneOnOneChatRequest,
) -> Optional[Union[CreateOneOnOneChatResponse, DefaultError]]:
        return _create_one_on_one_chat(client=self.client, body=body,
)

    async def create_one_on_one_chat_async(self, *,
body: CreateOneOnOneChatRequest,
) -> Optional[Union[CreateOneOnOneChatResponse, DefaultError]]:
        return await _create_one_on_one_chat_async(client=self.client, body=body,
)
    def create_online_teams_meeting(self, *,
body: CreateOnlineTeamsMeetingRequest,
) -> Optional[Union[CreateOnlineTeamsMeetingResponse, DefaultError]]:
        return _create_online_teams_meeting(client=self.client, body=body,
)

    async def create_online_teams_meeting_async(self, *,
body: CreateOnlineTeamsMeetingRequest,
) -> Optional[Union[CreateOnlineTeamsMeetingResponse, DefaultError]]:
        return await _create_online_teams_meeting_async(client=self.client, body=body,
)
    def download_meeting_transcript_recording(self, *,
type_: str,download_by: str,recording_url: Optional[str] = None,recording_id: Optional[str] = None,meeting_id: Optional[str] = None,transcript_id: Optional[str] = None,transcript_url: Optional[str] = None,) -> Optional[Union[DefaultError, File]]:
        return _download_meeting_transcript_recording(client=self.client, type_=type_,download_by=download_by,recording_url=recording_url,recording_id=recording_id,meeting_id=meeting_id,transcript_id=transcript_id,transcript_url=transcript_url,)

    async def download_meeting_transcript_recording_async(self, *,
type_: str,download_by: str,recording_url: Optional[str] = None,recording_id: Optional[str] = None,meeting_id: Optional[str] = None,transcript_id: Optional[str] = None,transcript_url: Optional[str] = None,) -> Optional[Union[DefaultError, File]]:
        return await _download_meeting_transcript_recording_async(client=self.client, type_=type_,download_by=download_by,recording_url=recording_url,recording_id=recording_id,meeting_id=meeting_id,transcript_id=transcript_id,transcript_url=transcript_url,)
    def get_channel_by_name(self, team_id: str,team_id_lookup: Any,*,
name: str,) -> Optional[Union[DefaultError, GetChannelByNameResponse]]:
        return _get_channel_by_name(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,name=name,)

    async def get_channel_by_name_async(self, team_id: str,team_id_lookup: Any,*,
name: str,) -> Optional[Union[DefaultError, GetChannelByNameResponse]]:
        return await _get_channel_by_name_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,name=name,)
    def get_team_by_name(self, *,
name: str,name_lookup: Any,) -> Optional[Union[DefaultError, GetTeamByNameResponse]]:
        return _get_team_by_name(client=self.client, name=name,name_lookup=name_lookup,)

    async def get_team_by_name_async(self, *,
name: str,name_lookup: Any,) -> Optional[Union[DefaultError, GetTeamByNameResponse]]:
        return await _get_team_by_name_async(client=self.client, name=name,name_lookup=name_lookup,)
    def getonline_meetings(self, *,
get_by: str,join_meeting_id: Optional[str] = None,join_meeting_url: Optional[str] = None,) -> Optional[Union[DefaultError, GetonlineMeetingsResponse]]:
        return _getonline_meetings(client=self.client, get_by=get_by,join_meeting_id=join_meeting_id,join_meeting_url=join_meeting_url,)

    async def getonline_meetings_async(self, *,
get_by: str,join_meeting_id: Optional[str] = None,join_meeting_url: Optional[str] = None,) -> Optional[Union[DefaultError, GetonlineMeetingsResponse]]:
        return await _getonline_meetings_async(client=self.client, get_by=get_by,join_meeting_id=join_meeting_id,join_meeting_url=join_meeting_url,)
    def invite_channel_member(self, team_id: str,team_id_lookup: Any,channel_id: str,*,
body: InviteChannelMemberRequest,
) -> Optional[Union[DefaultError, InviteChannelMemberResponse]]:
        return _invite_channel_member(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,body=body,
)

    async def invite_channel_member_async(self, team_id: str,team_id_lookup: Any,channel_id: str,*,
body: InviteChannelMemberRequest,
) -> Optional[Union[DefaultError, InviteChannelMemberResponse]]:
        return await _invite_channel_member_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,body=body,
)
    def invite_team_member(self, team_id: str,team_id_lookup: Any,*,
body: InviteTeamMemberRequest,
) -> Optional[Union[DefaultError, InviteTeamMemberResponse]]:
        return _invite_team_member(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,body=body,
)

    async def invite_team_member_async(self, team_id: str,team_id_lookup: Any,*,
body: InviteTeamMemberRequest,
) -> Optional[Union[DefaultError, InviteTeamMemberResponse]]:
        return await _invite_team_member_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,body=body,
)
    def list_all_recordings(self, online_meeting_id: str,) -> Optional[Union[DefaultError, list['ListAllRecordings']]]:
        return _list_all_recordings(client=self.client, online_meeting_id=online_meeting_id,)

    async def list_all_recordings_async(self, online_meeting_id: str,) -> Optional[Union[DefaultError, list['ListAllRecordings']]]:
        return await _list_all_recordings_async(client=self.client, online_meeting_id=online_meeting_id,)
    def list_all_transcripts(self, online_meeting_id: str,) -> Optional[Union[DefaultError, list['ListAllTranscripts']]]:
        return _list_all_transcripts(client=self.client, online_meeting_id=online_meeting_id,)

    async def list_all_transcripts_async(self, online_meeting_id: str,) -> Optional[Union[DefaultError, list['ListAllTranscripts']]]:
        return await _list_all_transcripts_async(client=self.client, online_meeting_id=online_meeting_id,)
    def list_channel_messages(self, team_id: str,team_id_lookup: Any,channel_id: str,*,
page_size: Optional[int] = None,next_page: Optional[str] = None,expand: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListChannelMessages']]]:
        return _list_channel_messages(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,page_size=page_size,next_page=next_page,expand=expand,)

    async def list_channel_messages_async(self, team_id: str,team_id_lookup: Any,channel_id: str,*,
page_size: Optional[int] = None,next_page: Optional[str] = None,expand: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListChannelMessages']]]:
        return await _list_channel_messages_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,page_size=page_size,next_page=next_page,expand=expand,)
    def list_chat_messages(self, chat_id: str,chat_id_lookup: Any,*,
page_size: Optional[int] = None,next_page: Optional[str] = None,where: Optional[str] = None,order_by: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListChatMessages']]]:
        return _list_chat_messages(client=self.client, chat_id=chat_id,chat_id_lookup=chat_id_lookup,page_size=page_size,next_page=next_page,where=where,order_by=order_by,)

    async def list_chat_messages_async(self, chat_id: str,chat_id_lookup: Any,*,
page_size: Optional[int] = None,next_page: Optional[str] = None,where: Optional[str] = None,order_by: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListChatMessages']]]:
        return await _list_chat_messages_async(client=self.client, chat_id=chat_id,chat_id_lookup=chat_id_lookup,page_size=page_size,next_page=next_page,where=where,order_by=order_by,)
    def list_team_members(self, team_id: str,team_id_lookup: Any,*,
page_size: Optional[int] = None,select: Optional[str] = None,next_page: Optional[str] = None,where: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListTeamMembers']]]:
        return _list_team_members(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,page_size=page_size,select=select,next_page=next_page,where=where,)

    async def list_team_members_async(self, team_id: str,team_id_lookup: Any,*,
page_size: Optional[int] = None,select: Optional[str] = None,next_page: Optional[str] = None,where: Optional[str] = None,) -> Optional[Union[DefaultError, list['ListTeamMembers']]]:
        return await _list_team_members_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,page_size=page_size,select=select,next_page=next_page,where=where,)
    def reply_to_channel_message(self, team_id: str,team_id_lookup: Any,channel_id: str,message_id: str,*,
body: ReplyToChannelMessageBody,
) -> Optional[Union[DefaultError, ReplyToChannelMessageResponse]]:
        return _reply_to_channel_message(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,message_id=message_id,body=body,
)

    async def reply_to_channel_message_async(self, team_id: str,team_id_lookup: Any,channel_id: str,message_id: str,*,
body: ReplyToChannelMessageBody,
) -> Optional[Union[DefaultError, ReplyToChannelMessageResponse]]:
        return await _reply_to_channel_message_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,message_id=message_id,body=body,
)
    def send_channel_message(self, team_id: str,team_id_lookup: Any,channel_id: str,*,
body: SendChannelMessageBody,
) -> Optional[Union[DefaultError, SendChannelMessageResponse]]:
        return _send_channel_message(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,body=body,
)

    async def send_channel_message_async(self, team_id: str,team_id_lookup: Any,channel_id: str,*,
body: SendChannelMessageBody,
) -> Optional[Union[DefaultError, SendChannelMessageResponse]]:
        return await _send_channel_message_async(client=self.client, team_id=team_id,team_id_lookup=team_id_lookup,channel_id=channel_id,body=body,
)
    def send_chat_message(self, chat_id: str,chat_id_lookup: Any,*,
body: SendChatMessageBody,
) -> Optional[Union[DefaultError, SendChatMessageResponse]]:
        return _send_chat_message(client=self.client, chat_id=chat_id,chat_id_lookup=chat_id_lookup,body=body,
)

    async def send_chat_message_async(self, chat_id: str,chat_id_lookup: Any,*,
body: SendChatMessageBody,
) -> Optional[Union[DefaultError, SendChatMessageResponse]]:
        return await _send_chat_message_async(client=self.client, chat_id=chat_id,chat_id_lookup=chat_id_lookup,body=body,
)
    def send_message_to_channel_as_bot(self, *,
body: SendMessageToChannelAsBotRequest,
) -> Optional[Union[DefaultError, SendMessageToChannelAsBotResponse]]:
        return _send_message_to_channel_as_bot(client=self.client, body=body,
)

    async def send_message_to_channel_as_bot_async(self, *,
body: SendMessageToChannelAsBotRequest,
) -> Optional[Union[DefaultError, SendMessageToChannelAsBotResponse]]:
        return await _send_message_to_channel_as_bot_async(client=self.client, body=body,
)
