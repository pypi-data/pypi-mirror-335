# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Tuple
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.process_utils import RuntimeRequirements
from ovos_bus_client.message import dig_for_message
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills.common_query_skill import CommonQuerySkill, CQSMatchLevel
from lingua_franca.parse import normalize
from neon_utils.user_utils import get_message_user, get_user_prefs
from neon_utils.hana_utils import request_backend


class WolframAlphaSkill(CommonQuerySkill):
    def __init__(self, **kwargs):
        CommonQuerySkill.__init__(self, **kwargs)
        self.queries = {}

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(network_before_load=False,
                                   internet_before_load=False,
                                   gui_before_load=False,
                                   requires_internet=True,
                                   requires_network=True,
                                   requires_gui=False,
                                   no_internet_fallback=False,
                                   no_network_fallback=False,
                                   no_gui_fallback=True)

    def initialize(self):
        sources_intent = IntentBuilder("WolframSource").require("Give").require("Source").build()
        self.register_intent(sources_intent, self.handle_get_sources)

        ask_wolfram_intent = IntentBuilder("AskWolfram").require("Request").build()
        self.register_intent(ask_wolfram_intent, self.handle_ask_wolfram)

    def handle_ask_wolfram(self, message):
        utterance = message.data.get("utterance")\
            .replace(message.data.get("Request"), "")
        user = get_message_user(message)
        result, _ = self._query_wolfram(utterance, message)
        if result:
            self.speak_dialog("response", {"response": result.rstrip('.')})
            self.queries[user] = utterance
            url = 'https://www.wolframalpha.com/input?i=' + \
                  utterance.replace(' ', '+')
            self.gui.show_url(url)

    def CQS_match_query_phrase(self, phrase: str):
        message = dig_for_message()
        LOG.info(phrase)
        result, key = self._query_wolfram(phrase, message)
        if result:
            to_speak = self.dialog_renderer.render(
                "response", {"response": result.rstrip(".")})
            user = get_message_user(message)
            return phrase, CQSMatchLevel.GENERAL, to_speak,\
                {"query": phrase, "answer": result, "user": user, "key": key}
        else:
            return None

    def CQS_action(self, phrase, data):
        """ If selected prepare to send sources. """
        if data:
            LOG.info('Setting information for source')
            user = data['user']
            self.queries[user] = data["query"]
            url = 'https://www.wolframalpha.com/input?i=' + \
                  data["query"].replace(' ', '+')
            self.gui.show_url(url)

    def handle_get_sources(self, message):
        user = get_message_user(message)
        if user in self.queries.keys():
            last_query = self.queries[user]
            preference_user = get_user_prefs(message)["user"]
            email_addr = preference_user["email"]

            if email_addr:
                title = "Wolfram|Alpha Source"
                body = f"\nHere is the answer to your question: " \
                       f"{last_query}\nView result on Wolfram|Alpha: " \
                       f"https://www.wolframalpha.com/input/?i=" \
                       f"{last_query.replace(' ', '+')}\n\n" \
                       f"-Neon"
                # Send Email
                self.send_email(title, body, message, email_addr)
                self.speak_dialog("sent.email", {"email": email_addr},
                                  private=True)
            else:
                self.speak_dialog("no.email", private=True)
        else:
            self.speak_dialog("no.info.to.send", private=True)

    def _query_wolfram(self, utterance, message) -> Tuple[str, str]:
        query = normalize(utterance, remove_articles=False)
        # parsed_question = self.question_parser.parse(utterance)
        # LOG.debug(parsed_question)
        # if not parsed_question:
        #     LOG.warning(f"No question pared from '{utterance}'")
        #     return None, None

        # Try to store pieces of utterance (None if not parsed_question)
        # utt_word = parsed_question.get('QuestionWord')
        # utt_verb = parsed_question.get('QuestionVerb')
        # utt_query = parsed_question.get('Query')
        # LOG.debug(len(str(utt_query).split()))
        # query = "%s %s %s" % (utt_word, utt_verb, utt_query)
        LOG.info(f"Querying WolframAlpha: {query}")

        preference_location = get_user_prefs(message)["location"]
        lat = str(preference_location['lat'])
        lng = str(preference_location['lng'])
        units = str(get_user_prefs(message)["units"]["measure"])
        query_type = "short" if message.context.get("klat_data") else "spoken"
        key = (utterance, lat, lng, units, repr(query_type))

        # if "convert" in query:
        #     to_convert = utt_query[:utt_query.index(utt_query.split(" ")[-1])]
        #     query = f'convert {to_convert} to {query.split("to")[1].split(" ")[-1]}'
        # LOG.info(f"query={query}")

        kwargs = {"lat": lat, "lon": lng, "api": query_type, "units": units,
                  "query": query}

        try:
            result = request_backend("proxy/wolframalpha",
                                     kwargs).get("answer")
        except Exception as e:
            LOG.error(e)
            result = None
        LOG.info(f"result={result}")
        return result, key
