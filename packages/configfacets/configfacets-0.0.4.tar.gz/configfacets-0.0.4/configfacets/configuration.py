import time
import yaml
import json
import os
from .base_http import BaseHTTP
from .dict import DictUtils


class Configuration:
    def __init__(self, source, source_type, **kwargs):
        self.source = source
        self.source_type = source_type
        self.api_key = kwargs.get("apiKey")
        self.post_body = kwargs.get("postBody")
        self.resp = None
        self.http_client = BaseHTTP()

    def fetch(self):
        if self.source_type == "file":
            if not os.path.exists(self.source):
                raise ValueError("File not found: {}".format(self.source))

            with open(self.source, "r", encoding="utf-8") as file:
                content = file.read()

            # Try to parse content as JSON or YAML
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                try:
                    result = yaml.safe_load(content)
                except yaml.YAMLError:
                    result = content  # Keep as raw text if neither JSON nor YAML

        elif self.source_type == "url":
            headers = {"X-APIKEY": self.api_key} if self.api_key else {}
            response = self.http_client.post(self.source, self.post_body, headers)

            if response:
                content_type = response.headers.get("Content-Type", "")
                if "json" in content_type:
                    result = response.json()
                elif "yaml" in content_type:
                    result = yaml.safe_load(response.text)
                else:
                    result = response.text
            else:
                result = None

        else:
            raise ValueError("Invalid source_type. Must be 'file' or 'url'")

        self.resp = result
        return result

    def get_resp(self):
        return self.resp

    def get_value(self, key_path):
        if not self.resp:
            print("[ERROR] Response is set as None, did you call fetch()?")
        return DictUtils.get_by_path(self.resp, key_path)
