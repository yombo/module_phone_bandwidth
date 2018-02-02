"""
For details about this module visit:
https://yombo.net/modules/modules-phone-bandwidth

Learn about at: https://yombo.net/
Get started today: https://yg2.in/start

.. moduleauthor:: Mitch Schwenk <mitch-gw@yombo.net>

:copyright: 2018 Yombo
:license: YRPL 1.6
"""
import traceback
from bandwidth import messaging, voice, account

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from yombo.core.log import get_logger
from yombo.core.module import YomboModule
from yombo.utils.maxdict import MaxDict

from yombo.modules.phone_bandwidth.web_routes import module_phone_bandwidth_routes


logger = get_logger('modules.twilio')

class Phone_Bandwidth(YomboModule):
    """
    Send SMS notifications (MMS coming soon)
    """
    def _init_(self, **kwargs):
        self.node = None

    @inlineCallbacks
    def _load_(self, **kwargs):
        self.gwid = self._Gateways.get_local_id()

        user = self._module_variables_cached['user']['values'][0]
        token = self._module_variables_cached['token']['values'][0]
        secret = self._module_variables_cached['secret']['values'][0]

        self.messaging_api = messaging.Client(user, token, secret)
        self.voice_api = voice.Client(user, token, secret)

        nodes = self._Nodes.search({'node_type': 'module_phone_bandwidth'})
        if len(nodes) == 0:
            self.node = yield self._Nodes.create(node_type='module_phone_bandwidth',
                                                 data={'phones': {}, 'config': {}},
                                                 data_content_type='json',
                                                 gateway_id=self.gwid,
                                                 destination='gw')
        elif len(nodes) > 1:
            logger.warn("Too many node instances. Taking the first one and dropping old ones.")

        for node_id, node in nodes.items():
            # print("amazon alex has node: %s - %s" % (node_id, node.data))
            # print("amazon alex has node: %s - %s" % (node_id, type(node.data)))
            self.node = node
            if 'phones' not in self.node.data:
                self.node.data['phones'] = {}
            if 'configs' not in self.node.data:
                self.node.data['configs'] = {}
            break

            # iterate throug modules, build a json list. Then create a node type "module_amazon_alexa". Lists
            # the gateway_id and device_id. Allows for for single or group control.

    def _webinterface_add_routes_(self, **kwargs):
        """
        Add web interface routes.

        :param kwargs:
        :return:
        """
        if self._States['loader.operating_mode'] == 'run':
            return {
                'nav_side': [
                    {
                        'label1': 'Module Settings',
                        'label2': 'Amazon Alexa',
                        'priority1': 3400,  # Even with a value, 'Tools' is already defined and will be ignored.
                        'priority2': 100,
                        'icon': 'fa fa-gear fa-fw',
                        'url': '/modules_settings/phone_bandwidth/index',
                        'tooltip': '',
                        'opmode': 'run',
                    },
                ],
                'routes': [
                    module_phone_bandwidth_routes,
                ],
                'configs': {
                    'settings_link': '/modules_settings/phone_bandwidth/index',
                },
            }


    def phone_bandwidth_phone_target(self, **kwargs):
        print("Bandwidth shouuld send message to: %s" % kwargs['phone'].phone_number)
