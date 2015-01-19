# -*- coding: utf-8 -*-
# Copyright © 2014 SEE AUTHORS FILE
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
Attempts to get the configuration data from etcd or seeds it if empty.
"""

import argparse
import json
import random
import string

import requests


def make_password(length=32):
    """
    Makes a random password.

    :Parameters:
       - length: The length of the password.
    """
    char_space = string.ascii_letters + string.punctuation
    password = []
    for x in range(0, length):
        password.append(random.choice(char_space))
    return "".join(password)


class SeedManager(object):
    """
    Uses etcd to seed json configuration files.
    """

    def __init__(self, endpoint='http://127.0.0.1:4001'):
        """
        Creates an instance of the SeedManager.

        :Parameters:
           - endpoint: The REST endpoint.
        """
        self._endpoint = endpoint

    def get_key(self, name, default=None, password=False):
        """
        Retrieves a key from etcd and may create one if it does not exist.

        :Parameters:
           - name: The name of the key.
           - default: An optional default if the key doesn't exist.
           - password: Generates a random password if the key is empty.
        """
        return_data = {'name': name, 'value': None}
        result = requests.get(self.keyendpoint + name)
        if result.status_code == 404:
            if not default and not password:
                raise Exception('No default for key ' + name)
            value = default
            if password and not default:
                value = make_password()
            return_data['value'] = self.set_key(name, value)['value']
        else:
            return_data['value'] = json.loads(result.content)['node']['value']
        return return_data

    def set_key(self, name, value):
        """
        Sets a key in etcd.

        :Parameters:
           - name: The keys name.
           - value: The keys value.
        """
        create_result = requests.put(
            self.keyendpoint + name, {'value': value})
        if create_result.status_code != 201:
            raise Exception('Can not create a value for key ' + name)
        return {'name': name, 'value': value}

    def update_content(self, keys, content):
        """
        Updates content in the content variable with fresh information.

        :Parameters:
            - keys: The keys to be looking up.
            - content: The original content structure.
        """
        for k, v in keys.items():
            conf_item = self.get_key(k, **v)
            content[k] = conf_item['value']
        return content

    def templatize(self, keys, template):
        """
        Updates a template with new information.

        :Parameters:
            - keys: The keys to be looking up.
            - template: The templace to write over.
        """
        for k, v in keys.items():
            conf_item = self.get_key(k, **v)
            template = template.replace(
                '{{ %s }}' % k, conf_item['value'])
        return template

    @property
    def keyendpoint(self):
        """
        Endpoint for keys.
        """
        return self._endpoint + '/v2/keys/'


def main():  # pragma: no cover
    """
    Main function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'conf_file', metavar='CONF', type=str, nargs=1,
        help='Path to the configuration file')
    parser.add_argument(
        'out_conf', metavar='OUT', type=str, nargs=1,
        help='Path to the json file to write values to.')
    parser.add_argument(
        '-t', '--template', metavar='TEMPLATE', type=bool,
        default=False,
        help='Fills in {{}}s instead of outputing JSON.')

    args = parser.parse_args()

    with open(args.conf_file[0], 'r') as conf_f:
        seed_conf = json.load(conf_f)

        manager = SeedManager(seed_conf['endpoint'])

        content = manager.update_content(seed_conf['keys'], content)
        if args.template[0]:
            with open(args.out_conf[0], 'r') as out_f:
                content = manager.templatize(content, out_f.read())
        else:
            with open(args.out_conf[0], 'r') as out_f:
                content = json.load(out_f)
            content = json.dumps(content)

        with open(args.out_conf[0], 'w') as new_f:
            new_f.write(content)


if __name__ == '__main__':  # pragma: no cover
    main()
