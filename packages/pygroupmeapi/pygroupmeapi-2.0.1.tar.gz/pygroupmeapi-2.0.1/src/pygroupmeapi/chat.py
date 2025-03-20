# Copyright (C) 2025 Preston Buterbaugh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see https://www.gnu.org/licenses/.

"""
@package pygroupmeapi
@brief   Classes to represent different kinds of GroupMe chats

@date    6/1/2024
@updated 3/20/2025

@author Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from typing import List, Dict

from .common_utils import call_api, progress_bar
from .message import Message
from .time_functions import string_to_epoch, epoch_to_string, epoch_to_month_year


class Chat:
    """
    @brief Interface representing a GroupMe chat
    """
    def __init__(self):
        """
        @brief Constructor. Defaults all fields to None, since generic Chat objects are not created
        """
        self.id = None
        self.name = None
        self.description = None
        self.last_used_epoch = None
        self.last_used = None
        self.creation_date_epoch = None
        self.creation_date = None
        self.image_url = None
        self.token = None

    def get_messages(self, sent_before: str = '', sent_after: str = '', keyword: str = '', before: int = 0, after: int = 0, limit: int = -1, timeout: int = 1, verbose: bool = False) -> List:
        """
        @brief  Gets all messages in a chat matching the specified criteria
        @param  sent_before  (int):  The time prior to which all messages returned should have been sent
        @param  sent_after   (int):  The time at or after which all messages returned should have been sent
        @param  keyword      (str):  A string of text which all messages returned should contain
        @param  before       (int):  The number of messages to fetch before each message matching the search criteria
        @param  after        (int):  The number of messages to fetch after each message matching the search criteria
        @param  limit        (int):  The maximum number of messages to return. -1 returns all matching messages
        @param  timeout      (int):  The number of seconds to wait after receiving a 429 (throttled) response from the API,
                                     before trying again. Defaults to 1 second
        @param  verbose      (bool): If output should be displayed indicating progress made in the query
        @return (List) A list of Message objects
        """
        raise NotImplementedError('Cannot call abstract method')


class Group(Chat):
    """
    @brief Represents a GroupMe group
    """
    def __init__(self, data: Dict, token: str):
        """
        @brief Constructor
        @param data (Dict): Dictionary of data representing the group as returned from a query
        @param token (str): The token for fetching group data
        """
        super().__init__()
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.last_used_epoch = data['messages']['last_message_created_at']
        self.last_used = epoch_to_string(self.last_used_epoch)
        self.creation_date_epoch = data['created_at']
        self.creation_date = epoch_to_string(self.creation_date_epoch)
        self.image_url = data['image_url']
        self.token = token

    def owner(self) -> str:
        """
        @brief  Gets the owner of the group
        @return (str) The name of the group owner
        """
        group_data = call_api(f'groups/{self.id}', self.token)
        for user in group_data['members']:
            if 'owner' in user['roles']:
                return user['name']
        return 'Unknown'

    def members(self) -> List:
        """
        @brief  Gets the members of the group
        @return (List) A list containing the names of each member of the group
        """
        group_data = call_api(f'groups/{self.id}', self.token)
        return [user['nickname'] for user in group_data]

    def get_messages(self, sent_before: str = '', sent_after: str = '', keyword: str = '', before: int = 0, after: int = 0, limit: int = -1, timeout: int = 1, verbose: bool = False) -> List:
        """
        @brief  Gets all messages in a group matching the specified criteria (see superclass method parameter documentation)
        """
        return page_through_messages(self.id, self.token, self.name, True, sent_before, sent_after, keyword, before, after, limit, timeout, verbose)


class DirectMessage(Chat):
    """
    @brief Represents a GroupMe direct message thread
    """
    def __init__(self, data: Dict, token: str):
        """
        @brief Constructor
        @param data  (Dict): Dictionary of data representing the direct message chat as returned from a query
        @param token (str):  GroupMe authentication token
        """
        super().__init__()
        self.id = data['other_user']['id']
        self.name = data['other_user']['name']
        self.last_used_epoch = data['last_message']['created_at']
        self.last_used = epoch_to_string(self.last_used_epoch)
        self.creation_date_epoch = data['created_at']
        self.creation_date = epoch_to_string(self.creation_date_epoch)
        self.image_url = data['other_user']['avatar_url']
        self.token = token

    def get_messages(self, sent_before: str = '', sent_after: str = '', keyword: str = '', before: int = 0, after: int = 0, limit: int = -1, timeout: int = 1, verbose: bool = False) -> List:
        """
        @brief  Gets all messages in a direct message matching the specified criteria (see superclass method parameter documentation)
        """
        return page_through_messages(self.id, self.token, self.name, False, sent_before, sent_after, keyword, before, after, limit, timeout, verbose)


def page_through_messages(chat_id: str, token: str, name: str, is_group: bool, sent_before: str, sent_after: str, keyword: str, before: int, after: int, limit: int, timeout: int, verbose: bool) -> List:
    """
    @brief  Pages through messages in a chat and returns the messages matching the specified criteria
    @param  chat_id             (str):  The ID of the chat from which to retrieve the message data
    @param  token               (str):  GroupMe authentication token
    @param  name                (str):  The chat name
    @param  is_group            (bool): If the chat is a group (as opposed to a direct message)
    @param  sent_before         (str):  The time or date at or before which all returned messages should have been sent
    @param  sent_after          (str):  The time or date at or after which all returned messages should have been sent
    @param  keyword             (str):  A string of text which all returned messages should contain
    @param  before              (int):  The number of messages before each selected message to include
    @param  after               (int):  The number of messages after each selected message to include
    @param  limit               (int):  The maximum number of messages to return from this group. -1 for no limit
    @param  timeout             (int):  The number of seconds to wait before retrying an API call if a 429 error is received
    @param  verbose             (bool): If output detailing the progress of the search should be shown
    @return (List) A list of all messages in the group matching the criteria
    """
    if verbose:
        print(f'Fetching messages from {name}...', end='')

    # Calculate before and after times
    if sent_before:
        if len(sent_before.split(' ')) == 1:
            sent_before = f'{sent_before} 23:59:59'
        sent_before = string_to_epoch(sent_before)

    if sent_after:
        if len(sent_after.split(' ')) == 1:
            sent_after = f'{sent_after} 00:00:00'
        sent_after = string_to_epoch(sent_after)

    # Variables for tracking progress
    messages = []
    num_skipped = 0
    in_range = True

    # Determine endpoint
    if is_group:
        endpoint = f'groups/{chat_id}/messages'
    else:
        endpoint = 'direct_messages'

    # Set parameters
    params = {}
    if is_group:
        if limit == -1:
            params['limit'] = 100
        else:
            params['limit'] = min(limit, 100)
    else:
        params['other_user_id'] = chat_id

    # Process message page
    message_page = call_api(endpoint, token, params=params, timeout=timeout, except_message=f'Error fetching messages from {name}')
    total_messages = message_page['count']
    if is_group:
        message_page = message_page['messages']
    else:
        message_page = message_page['direct_messages']

    # Set number of messages after current message to get
    get_next = 0

    # Loop over message pages until no more, or the time bound is reached
    while len(message_page) > 0 and in_range and (limit == -1 or len(messages) < limit):
        for i, message in enumerate(message_page):
            if get_next:
                messages.append(Message(name, is_group, message, token))
                get_next = get_next - 1
            if sent_after and message['created_at'] < sent_after:
                in_range = False
                break
            if (sent_before and message['created_at'] > sent_before) or (keyword and (message['text'] is None or keyword not in message['text'])):
                num_skipped = num_skipped + 1
            else:
                messages.append(Message(name, is_group, message, token))
                get_next = before
                if after:
                    messages = messages + get_messages_after(chat_id, name, message['id'], after, token, is_group, timeout)
            if verbose:
                print(f'\rFetching messages from {name} (searched {len(messages) + num_skipped} of {total_messages}, selected {len(messages)})', end='')
                if sent_after:
                    print(f'... (Reached {epoch_to_month_year(message["created_at"])})', end='')
                else:
                    # Since the search will proceed all the way to the beginning of the group, output progress bar
                    print(progress_bar(len(messages) + num_skipped, total_messages), end='')

            # Check if limit reached
            if limit > -1 and len(messages) == limit:
                break

            # Update limit
            if is_group:
                if limit == -1:
                    params['limit'] = 100
                else:
                    params['limit'] = min(limit - len(messages), 100)

            # Update last message ID if last message on page
            if i == len(message_page) - 1:
                params['before_id'] = message['id']

        message_page = call_api(endpoint, token, params=params, except_message=f'Error fetching messages from {name}')
        if is_group:
            message_page = message_page['messages']
        else:
            message_page = message_page['direct_messages']

    if verbose:
        print(f'\rSelected {len(messages)} of {total_messages} messages from {name}')

    messages.sort(key=lambda fetched_message: fetched_message.time_epoch)
    return messages


def get_messages_after(chat_id: str, chat_name: str, message_id: str, num_messages: int, token: str, is_group: bool, timeout: int) -> List:
    """
    @brief  Gets a certain number of messages after the provided message ID
    @param  chat_id      (str):  The ID of the chat from which to get the messages
    @param  chat_name    (str):  The name of the chat
    @param  message_id   (str):  The ID of the message after which to fetch messages
    @param  num_messages (int):  The number of messages to get
    @param  token        (str):  The GroupMe API token to fetch the messages
    @param  is_group     (bool): If the chat to get messages from is a group, rather than a direct message
    @param  timeout      (int):  The number of seconds to wait before retrying an API call if a 429 error is received
    @return (List) A list of the messages fetched
    """
    # Set parameters
    params = {'after_id': message_id}

    # Determine number of messages to get
    if is_group:
        endpoint = f'groups/{chat_id}/messages'
        limit = min(num_messages, 100)
        params['limit'] = limit
    else:
        endpoint = 'direct_messages'
        params['other_user_id'] = chat_id

    # Call API
    message_page = call_api(endpoint, token, params=params, timeout=timeout, except_message='Unexpected error fetching messages')

    # Parse message page
    if is_group:
        messages = message_page['messages'][0:min(100, num_messages)]
    else:
        messages = message_page['direct_messages'][0:min(20, num_messages)]

    return [Message(chat_name, is_group, message, token) for message in messages]
