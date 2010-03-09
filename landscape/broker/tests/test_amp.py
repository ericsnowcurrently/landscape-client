from landscape.lib.amp import MethodCall, MethodCallError
from landscape.tests.helpers import LandscapeTest, DEFAULT_ACCEPTED_TYPES
from landscape.broker.tests.helpers import RemoteBrokerHelper


class RemoteBrokerTest(LandscapeTest):

    helpers = [RemoteBrokerHelper]

    def test_ping(self):
        """
        The L{RemoteBroker.ping} method calls the C{ping} method of the
        remote L{BrokerServer} instance and returns its result with a
        L{Deferred}.
        """
        result = self.remote.ping()
        return self.assertSuccess(result, True)

    def test_register_client(self):
        """
        The L{RemoteBroker.register_client} method forwards a registration
        request to the remote L{BrokerServer} object.
        """

        def assert_result(result):
            self.assertEquals(result, None)
            [client] = self.broker.get_clients()
            self.assertEquals(client.name, "client")

        sent = self.remote.register_client("client")
        return sent.addCallback(assert_result)

    def test_send_message(self):
        """
        The L{RemoteBroker.send_message} method calls the C{send_message}
        method of the remote L{BrokerServer} instance and returns its result
        with a L{Deferred}.
        """
        message = {"type": "test"}
        self.mstore.set_accepted_types(["test"])

        def assert_response(message_id):
            self.assertTrue(isinstance(message_id, int))
            self.assertTrue(self.mstore.is_pending(message_id))
            self.assertFalse(self.exchanger.is_urgent())
            self.assertMessages(self.mstore.get_pending_messages(),
                                [message])

        result = self.remote.send_message(message)
        return result.addCallback(assert_response)

    def test_send_message_with_urgent(self):
        """
        The L{RemoteBroker.send_message} method honors the urgent argument.
        """
        message = {"type": "test"}
        self.mstore.set_accepted_types(["test"])

        def assert_response(message_id):
            self.assertTrue(self.exchanger.is_urgent())

        result = self.remote.send_message(message, urgent=True)
        return result.addCallback(assert_response)

    def test_is_message_pending(self):
        """
        The L{RemoteBroker.is_message_pending} method calls the
        C{is_message_pending} method of the remote L{BrokerServer} instance
        and returns its result with a L{Deferred}.
        """
        result = self.remote.is_message_pending(1234)
        return self.assertSuccess(result, False)

    def test_stop_clients(self):
        """
        The L{RemoteBroker.stop_clients} method calls the C{stop_clients}
        method of the remote L{BrokerServer} instance and returns its result
        with a L{Deferred}.
        """
        result = self.remote.stop_clients()
        return self.assertSuccess(result, None)

    def test_reload_configuration(self):
        """
        The L{RemoteBroker.reload_configuration} method calls the
        C{reload_configuration} method of the remote L{BrokerServer}
        instance and returns its result with a L{Deferred}.
        """
        result = self.remote.reload_configuration()
        return self.assertSuccess(result, None)

    def test_register(self):
        """
        The L{RemoteBroker.register} method calls the C{register} method
        of the remote L{BrokerServer} instance and returns its result with
        a L{Deferred}.
        """
        # This should make the registration succeed
        self.transport.responses.append([{"type": "set-id", "id": "abc",
                                          "insecure-id": "def"}])
        result = self.remote.register()
        return self.assertSuccess(result, None)

    def test_get_accepted_message_types(self):
        """
        The L{RemoteBroker.get_accepted_message_types} method calls the
        C{get_accepted_message_types} method of the remote L{BrokerServer}
        instance and returns its result with a L{Deferred}.
        """
        result = self.remote.get_accepted_message_types()
        return self.assertSuccess(result, self.mstore.get_accepted_types())

    def test_get_server_uuid(self):
        """
        The L{RemoteBroker.get_server_uuid} method calls the C{get_server_uuid}
        method of the remote L{BrokerServer} instance and returns its result
        with a L{Deferred}.
        """
        self.mstore.set_server_uuid("abcde")
        result = self.remote.get_server_uuid()
        return self.assertSuccess(result, "abcde")

    def test_register_client_accepted_message_type(self):
        """
        The L{RemoteBroker.register_client_accepted_message_type} method calls
        the C{register_client_accepted_message_type} method of the remote
        L{BrokerServer} instance and returns its result with a L{Deferred}.
        """

        def assert_response(response):
            self.assertEquals(response, None)
            self.assertEquals(
                self.exchanger.get_client_accepted_message_types(),
                sorted(["type"] + DEFAULT_ACCEPTED_TYPES))

        result = self.remote.register_client_accepted_message_type("type")
        return result.addCallback(assert_response)

    def test_exit(self):
        """
        The L{RemoteBroker.exit} method calls the C{exit} method of the remote
        L{BrokerServer} instance and returns its result with a L{Deferred}.
        """
        result = self.remote.exit()
        return self.assertSuccess(result, None)

    def test_call_if_accepted(self):
        """
        The L{RemoteBroker.call_if_accepted} method calls a function if the
        given message type is accepted.
        """
        self.mstore.set_accepted_types(["test"])
        function = self.mocker.mock()
        self.expect(function(123)).result("cool")
        self.mocker.replay()
        result = self.remote.call_if_accepted("test", function, 123)
        return self.assertSuccess(result, "cool")

    def test_call_if_accepted_with_not_accepted(self):
        """
        The L{RemoteBroker.call_if_accepted} method doesn't do anything if the
        given message type is not accepted.
        """
        function = lambda: 1 / 0
        result = self.remote.call_if_accepted("test", function)
        return self.assertSuccess(result, None)

    def test_method_call_error(self):
        """
        Trying to call an non-exposed broker method results in a failure.
        """
        result = self.remote._protocol.callRemote(MethodCall,
                                                  method="get_clients",
                                                  args=[],
                                                  kwargs={})
        return self.assertFailure(result, MethodCallError)
