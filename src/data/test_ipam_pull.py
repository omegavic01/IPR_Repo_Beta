import unittest


class TestAPIMethods(unittest.TestCase):

    def setUp(self):
        requests.packages.urllib3.disable_warnings()
        self.username = PAYLOAD['username']
        self.password = PAYLOAD['password']
        self.url = PAYLOAD['url']

    def test_working_request_response(self):
        # Send a request to the API Server and store the response.
        """
        Function: test_request_response

        From IE Browser as of 20190415:
        Test URL:
            https://<ip address>/wapi/v2.7/networkview?name=default

        Return:
        [
            {
                "_ref": "networkview/ZG5zLm5ldHdvcmtfdmlldyQw:default/true",
                "is_default": true,
                "name": "default"
            }
        ]
        """
        response = requests.get(self.url +
                                "networkview?"
                                "name=default",
                                auth=(self.username,
                                      self.password),
                                verify=False)

        # Confirm that the request-response cycle completed successfully.
        self.assertTrue(response.ok)

    def test_no_url_request_response(self):
        # Send a request to the API Server and store the response.
        with self.assertRaises(requests.exceptions.MissingSchema):
            response = requests.get("networkview?"
                                    "name=default",
                                    auth=(self.username,
                                          self.password),
                                    verify=False)

    def test_no_username_request_response(self):
        # Send a request to the API Server and store the response.
        with self.assertRaises(TypeError):
            response = requests.get(self.url +
                                    "networkview?"
                                    "name=default",
                                    auth=self.password,
                                    verify=False)

    def test_no_password_request_response(self):
        # Send a request to the API Server and store the response.
        with self.assertRaises(TypeError):
            response = requests.get(self.url +
                                    "networkview?"
                                    "name=default",
                                    auth=self.username,
                                    verify=False)

    def test_verify_true_request_response(self):
        # Send a request to the API Server and store the response.
        with self.assertRaises(requests.exceptions.SSLError):
            response = requests.get(self.url +
                                    "networkview?"
                                    "name=default",
                                    auth=(self.username,
                                          self.password),
                                    verify=True)

    def test_networkview_schema_request_response(self):
        # Send a request to the API Server and store the response.
        response = requests.get(self.url +
                                "networkview?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)

        # Confirm that the request-response cycle completed successfully.
        self.assertTrue(response.ok)

    def test_networkview_schema_check(self):
        # Send a request to the API Server and store the response.
        # Compare to stored schema data.
        response = requests.get(self.url +
                                "networkview?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)

        response_decoded_data = response.content.decode('utf-8')
        response_json_data = json.loads(response_decoded_data)
        networkview_schema_file = os.path.join(raw_data_path,
                                               'networkview_schema.pkl')
        with open(networkview_schema_file, 'rb') as fi:
            raw_test_data = pickle.load(fi)
        # Confirm that the request-response cycle compared to stored data.
        self.assertTrue(response_json_data == raw_test_data)

    def test_network_schema_request_response(self):
        # Send a request to the API Server and store the response.
        response = requests.get(self.url +
                                "network?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)

        # Confirm that the request-response cycle completed successfully.
        self.assertTrue(response.ok)

    def test_network_schema_check(self):
        # Send a request to the API Server and store the response.
        response = requests.get(self.url +
                                "network?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)
        response_decoded_data = response.content.decode('utf-8')
        response_json_data = json.loads(response_decoded_data)
        network_schema_file = os.path.join(raw_data_path, 'network_schema.pkl')
        with open(network_schema_file, 'rb') as fi:
            raw_test_data = pickle.load(fi)
        # Confirm that the request-response cycle completed successfully.
        self.assertTrue(response_json_data == raw_test_data)

    def test_networkcont_schema_request_response(self):
        # Send a request to the API Server and store the response.
        response = requests.get(self.url +
                                "networkcontainer?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)

        # Confirm that the request-response cycle completed successfully.
        self.assertTrue(response.ok)

    def test_networkcont_schema_check(self):
        # Send a request to the API Server and store the response.
        response = requests.get(self.url +
                                "networkcontainer?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)
        response_decoded_data = response.content.decode('utf-8')
        response_json_data = json.loads(response_decoded_data)
        network_schema_file = os.path.join(raw_data_path,
                                           'networkcont_schema.pkl')
        with open(network_schema_file, 'rb') as fi:
            raw_test_data = pickle.load(fi)
        # Confirm that the request-response cycle completed successfully.
        self.assertTrue(response_json_data == raw_test_data)

    def test_extattributes_schema_request_response(self):
        # Send a request to the API Server and store the response.
        response = requests.get(self.url +
                                "extensibleattributedef?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)

        # Confirm that the request-response cycle completed successfully.
        self.assertTrue(response.ok)

    def test_extattributes_schema_check(self):
        # Send a request to the API Server and store the response.
        response = requests.get(self.url +
                                "extensibleattributedef?"
                                "_schema",
                                auth=(self.username,
                                      self.password),
                                verify=False)
        response_decoded_data = response.content.decode('utf-8')
        response_json_data = json.loads(response_decoded_data)
        ea_schema_file = os.path.join(raw_data_path, 'ea_schema.pkl')
        with open(ea_schema_file, 'rb') as fi:
            raw_test_data = pickle.load(fi)
        # Confirm that the request-response cycle completed successfully.
        self.asserttrue(response_json_data == raw_test_data)


if __name__ == '__main__':
    unittest.main()