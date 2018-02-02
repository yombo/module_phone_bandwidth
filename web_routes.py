import json

from twisted.internet.defer import inlineCallbacks

from yombo.core.exceptions import YomboWarning
from yombo.lib.webinterface.routes.api_v1.__init__ import return_good, return_not_found, return_error, return_unauthorized
from yombo.core.log import get_logger
from yombo.lib.webinterface.auth import require_auth

logger = get_logger("modules.phone_bandwidth.web_routes")

def module_phone_bandwidth_routes(webapp):
    """
    Adds routes to the webinterface module.

    :param webapp: A pointer to the webapp, it's used to setup routes.
    :return:
    """
    with webapp.subroute("/modules_settings") as webapp:

        def root_breadcrumb(webinterface, request):
            webinterface.add_breadcrumb(request, "/?", "Home")
            webinterface.add_breadcrumb(request, "/modules/index", "Modules")
            webinterface.add_breadcrumb(request, "/modules_settings/phone_bandwidth/index", "Phone Bandwidth")

        @webapp.route("/phone_bandwidth", methods=['GET'])
        @require_auth()
        def page_module_phone_bandwidth_get(webinterface, request, session):
            return webinterface.redirect(request, '/modules/phone_bandwidth/index')

        @webapp.route("/phone_bandwidth/index", methods=['GET'])
        @require_auth()
        def page_module_phone_bandwidth_index_get(webinterface, request, session):
            phonemodule = webinterface._Modules['Phone']
            phone_bandwidth = webinterface._Modules['Phone_Bandwidth']
            if phone_bandwidth.node is None:
                page = webinterface.webapp.templates.get_template(webinterface._dir + '/pages/misc/stillbooting.html')
                root_breadcrumb(webinterface, request)
                return page.render(alerts=webinterface.get_alerts())

            page = webinterface.webapp.templates.get_template('modules/phone_bandwidth/web/index.html')
            root_breadcrumb(webinterface, request)

            return page.render(alerts=webinterface.get_alerts(),
                               phonemodule=phonemodule,
                               phone_bandwidth=phone_bandwidth,
                               )

        @webapp.route("/phone_bandwidth/index", methods=['POST'])
        @require_auth()
        def page_module_phone_bandwidth_index_post(webinterface, request, session):
            phonemodule = webinterface._Modules['Phone']
            phone_bandwidth = webinterface._Modules['Phone_Bandwidth']
            if phone_bandwidth.node is None:
                page = webinterface.webapp.templates.get_template(webinterface._dir + '/pages/misc/stillbooting.html')
                root_breadcrumb(webinterface, request)
                return page.render(alerts=webinterface.get_alerts())

            if 'json_output' in request.args:
                json_output = request.args.get('json_output', [{}])[0]
                json_output = json.loads(json_output)
                # print("json_out: %s" % json_output)
                allowed = []
                for device_id, value in json_output.items():
                    if value == '1':
                        if device_id.startswith("devid_"):
                            parts = device_id.split('_')
                            device_id = parts[1]
                            if device_id in phone_bandwidth._Devices:
                                allowed.append(parts[1])

                if 'devices' not in phone_bandwidth.node.data:
                    phone_bandwidth.node.data['devices'] = {}
                # if 'allowed' not in phone_bandwidth.node.data:
                #     phone_bandwidth.node.data['devices']['allowed'] = {}
                phone_bandwidth.node.data['devices']['allowed'] = allowed
                phone_bandwidth.discovery(save=False)

            page = webinterface.webapp.templates.get_template('modules/phone_bandwidth/web/index.html')
            root_breadcrumb(webinterface, request)

            return page.render(alerts=webinterface.get_alerts(),
                               phonemodule=phonemodule,
                               phone_bandwidth=phone_bandwidth,
                               )

    with webapp.subroute("/api/v1/extended") as webapp:

        @webapp.route("/phonebandwidth/control", methods=['POST'])
        @require_auth(api=True)
        @inlineCallbacks
        def page_module_phone_bandwidth_control_post(webinterface, request, session):
            phonemodule = webinterface._Modules['Phone']
            phone_bandwidth = webinterface._Modules['Phone_Bandwidth']
            try:
                data = json.loads(request.content.read())
            except:
                return return_error(message="invalid JSON sent", code=400)

            enc = yield webinterface._GPG.encrypt(data['request'])
            results = "testing: %s" % enc
            return results
