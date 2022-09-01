# Copyright 2019 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.9-slim
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    make \
    gcc \
    locales
ADD . /app
WORKDIR /app
RUN pip install -U setuptools
RUN pip install ."[api, datadog, dynatrace, prometheus, elasticsearch, pubsub, cloud_monitoring, cloud_service_monitoring, cloud_storage, bigquery, cloudevent, dev, pyzabbix]"
RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Paris /etc/localtime
ENTRYPOINT [ "slo-generator" ]
CMD ["-v"]
