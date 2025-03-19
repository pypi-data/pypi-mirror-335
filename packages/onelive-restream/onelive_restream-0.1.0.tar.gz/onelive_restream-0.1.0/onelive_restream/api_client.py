#
# (c) 2025, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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
#


from nexium_api import NexiumApiClient, Protocol

from onelive_restream.shared.routers import MainRouter
from onelive_restream.shared import RequestAuth
from onelive_restream.shared import errors


class OneLiveRestream(NexiumApiClient, MainRouter):
    def __init__(
        self,
        token: str,
        is_test: bool = False,
        host: str = None,
        protocol: Protocol = Protocol.HTTPS,
    ):
        if not host:
            host = 'api.restream.nexium.me' if not is_test else 'api.test.restream.nexium.me'
        super().__init__(
            auth=RequestAuth(token=token),
            protocol=protocol,
            host=host,
            errors_module=errors,
        )
