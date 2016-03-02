# Metadata Proxy

The metadata proxy is used to allow containers to acquire IAM roles.

## Installation

From inside of the repo run the following commands:

```bash
cd /srv
git clone https://github.com/lyft/metadataproxy
cd metadataproxy
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_wsgi.txt
deactivate
```

## Configuration

### Modes of operation

See [the settings file](https://github.com/lyft/metadataproxy/blob/master/metadataproxy/settings.py)
for specific configuration options.

The metadataproxy has two basic modes of operation:

1. Running in AWS where it simply proxies most routes to the real metadata
   service.
2. Running outside of AWS where it mocks out most routes.

To enable mocking, use the environment variable:

```
export MOCK_API=true
```

### AWS credentials

metadataproxy relies on boto configuration for its AWS credentials. If metadata
IAM credentials are available, it will use this. Otherwise, you'll need to use
.aws/credentials, .boto, or environment variables to specify the IAM
credentials before the service is started.

### Role assumption

For IAM routes, the metadataproxy will use STS to assume roles for containers.
To do so it takes the incoming IP address of metadata requests and finds the
running docker container associated with the IP address. It uses the value of
the container's IAM_ROLE environment variable as the role it will assume. It
then assumes the role and gives back STS credentials in the metadata response.

So, to specify the role of a container, simply launch it with the IAM_ROLE
environment variable set to the IAM role you wish the container to run with.

If you'd like containers to fallback to a default role if no role is specified,
you can use the following configuration option:

```
export DEFAULT_ROLE=my-default-role
```

### Routing container traffic to metadataproxy

Using iptables, we can forward traffic meant to 169.254.169.254 from docker0 to
the metadataproxy. The following example assumes the metadataproxy is run on
the host, and not in a container:

```
/sbin/iptables --wait -t nat -A PREROUTING  -i docker0 -p tcp --dport 80 --destination 169.254.169.254 --jump DNAT --to-destination 127.0.0.1:45001
```

If you'd like to start the metadataproxy in a container, it's recommended to
use host-only networking. Also, it's necessary to volume mount in the docker
socket, as metadataproxy must be able to interact with docker.

## Run metadataproxy

In the following we assume _my\_config_ is a bash file with exports for all of
the necessary settings discussed in the configuration section.

```
source my_config
cd /srv/metadataproxy
source venv/bin/activate
gunicorn wsgi:app --workers=2 -k gevent
```
