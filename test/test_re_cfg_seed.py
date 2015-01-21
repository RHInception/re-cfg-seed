# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Unittests.
"""

import mock
import requests

from . import TestCase

from contextlib import nested

import recfgseed


class TestMakePassword(TestCase):

    def test_make_password(self):
        """
        Verify making passwords works like it should.
        """
        # Default length is 32
        passwd = recfgseed.make_password()
        assert len(passwd) == 32

        # We should be able to specify a length
        passwd = recfgseed.make_password(10)
        assert len(passwd) == 10


class TestReCFGSeed(TestCase):

    def test_create_seed_manager(self):
        """
        Verify creation of SeedManager reacts as it should.
        """
        # The default endpoint should be this
        sm = recfgseed.SeedManager()
        self.assertEquals(sm._endpoint, 'http://127.0.0.1:4001')
        self.assertEquals(sm.keyendpoint, 'http://127.0.0.1:4001')

        # We should be able to override the endpoint
        sm = recfgseed.SeedManager('https://127.0.0.2:6001/')
        self.assertEquals(sm._endpoint, 'https://127.0.0.2:6001/')
        self.assertEquals(sm.keyendpoint, 'https://127.0.0.2:6001/')

    def test_update_content(self):
        """
        Verify the content in update_content is actually updated.
        """
        with mock.patch('requests.get') as _get:
            resp = requests.Response()
            resp.status_code = 200
            resp._content = '{"node": {"value": "test"}}'
            _get.return_value = resp

            sm = recfgseed.SeedManager()
            result = sm.update_content({'akey': {}}, {'akey': '___'})
            assert result['akey'] == 'test'

    def test_set_key(self):
        """
        Verify setting keys works like it should.
        """
        with mock.patch('requests.put') as _put:
            resp = requests.Response()
            resp.status_code = 201
            _put.return_value = resp

            sm = recfgseed.SeedManager()
            result = sm.set_key('key', 'value')

            assert result['name'] == 'key'
            assert result['value'] == 'value'

    def test_set_key_failure(self):
        """
        Verify set_key fails with an exception.
        """
        with mock.patch('requests.put') as _put:
            resp = requests.Response()
            resp.status_code = 404
            _put.return_value = resp

            sm = recfgseed.SeedManager()
            self.assertRaises(Exception, sm.set_key, 'key', 'value')

    def test_get_key_with_value(self):
        """
        Verify get_key returns the value from the server.
        """
        with mock.patch('requests.get') as _get:
            resp = requests.Response()
            resp.status_code = 200
            resp._content = '{"node": {"value": "test"}}'
            _get.return_value = resp

            sm = recfgseed.SeedManager()
            result = sm.get_key('key')
            assert result['name'] == 'key'
            assert result['value'] == 'test'

    def test_get_key_with_default_but_no_value(self):
        """
        Verify get_key returns the default value and creates it on the server.
        """
        with nested(
                mock.patch('requests.get'),
                mock.patch('requests.put')) as (_get, _put):
            resp = requests.Response()
            resp.status_code = 404
            _get.return_value = resp

            presp = requests.Response()
            presp.status_code = 201
            _put.return_value = presp

            sm = recfgseed.SeedManager()
            result = sm.get_key('key', 'default')

            assert result['name'] == 'key'
            assert result['value'] == 'default'
            assert _put.called_once()

    def test_get_key_as_password_with_no_default_or_value(self):
        """
        Verify that the password keys get generated and created on the server.
        """
        with nested(
                mock.patch('requests.get'),
                mock.patch('requests.put'),
                mock.patch('recfgseed.make_password')) as (
                    _get, _put, _make_password):
            resp = requests.Response()
            resp.status_code = 404
            _get.return_value = resp

            presp = requests.Response()
            presp.status_code = 201
            _put.return_value = presp

            _make_password.return_value = 'from_make_password'

            sm = recfgseed.SeedManager()
            result = sm.get_key('key', password=True)

            assert result['name'] == 'key'
            assert result['value'] == 'from_make_password'
            _put.assert_called_once()
            _make_password.assert_called_once()

    def test_get_key_with_no_default_or_value(self):
        """
        Verify get_key fails with an exception when there is no value and no default.
        """
        with mock.patch('requests.get') as _get:
            resp = requests.Response()
            resp.status_code = 404
            _get.return_value = resp

            sm = recfgseed.SeedManager()
            self.assertRaises(Exception, sm.get_key, 'key')

    def test_templatize(self):
        """
        Verify templates can be used.
        """
        with mock.patch('requests.get') as _get:
            resp = requests.Response()
            resp.status_code = 200
            resp._content = '{"node": {"value": "test"}}'
            _get.return_value = resp

            sm = recfgseed.SeedManager()
            result = sm.templatize({'akey': {}}, 'This is a test: {{ akey }}.')
            self.assertEquals(str(result), 'This is a test: test.')

    def test_casting(self):
        """
        Verify casting works.
        """
        with mock.patch('requests.get') as _get:
            resp = requests.Response()
            resp.status_code = 200
            resp._content = '{"node": {"value": "1234"}}'
            _get.return_value = resp

            sm = recfgseed.SeedManager()
            result = sm.update_content({'akey': {'type': 'int'}}, {'akey': '___'})
            assert result['akey'] == 1234

            self.assertRaises(
                KeyError,
                sm.update_content,
                {'newkey': {'type': 'asdasd'}}, {'akey': '___'})
