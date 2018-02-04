import json

from twisted.internet.defer import inlineCallbacks

from yombo.core.exceptions import YomboWarning
from yombo.lib.webinterface.routes.api_v1.__init__ import return_good, return_not_found, return_error, return_unauthorized
from yombo.core.log import get_logger
from yombo.lib.webinterface.auth import require_auth, run_first

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
                print("json_out: %s" % json_output)
                if 'active_phones' not in phone_bandwidth.node.data:
                    phone_bandwidth.node.data['active_phones'] = {}

                for device_id, values in json_output['phones'].items():
                    print("%s values: %s" % (device_id, values))
                    phone = {
                        'send': 0,
                        'receive': 0,
                        'pin': '',
                    }
                    if 'send' in values and str(values['send']) == '1':
                        phone['send'] = 1
                    if 'receive' in values and str(values['receive']) == '1':
                        phone['receive'] = 1
                    if 'pin' in values:
                        phone['pin'] = values['pin']

                phone_bandwidth.node.data['active_phones'][device_id] = phone
                webinterface.add_alert('Bandwidth phones saved.')
                phone_bandwidth.node.save()

            page = webinterface.webapp.templates.get_template('modules/phone_bandwidth/web/index.html')
            root_breadcrumb(webinterface, request)

            return page.render(alerts=webinterface.get_alerts(),
                               phonemodule=phonemodule,
                               phone_bandwidth=phone_bandwidth,
                               )

    with webapp.subroute("/api/v1/extended") as webapp:

        @webapp.route("/phonebandwidth/<string:apiauth>/sms", methods=['POST'])
        @run_first()
        def page_module_phone_bandwidth_control_post(webinterface, request, session, apiauth):
            phonemodule = webinterface._Modules['Phone']
            phone_bandwidth = webinterface._Modules['Phone_Bandwidth']
            print("got apiauth: %s" % apiauth)
            if apiauth != phone_bandwidth.apiauth.auth_id:
                return return_error(request, message="invalid API Auth", code=400)

            try:
                data = json.loads(request.content.read())
            except:
                return return_error(request, message="invalid JSON sent", code=400)
            results = "PHONE Bandwidth incoming request: %s" % data
            print(results)
            return results
