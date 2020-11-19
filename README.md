# Indices lifecycle utility for ElasticSearch

This project aims to provide a docker image that handle the rollup of elastic indices for you, in a cloud native or gitops way.
## Git repository

* main repo: https://gitlab.comwork.io/oss/elastic-indices-lifecycle
* github mirror backup: https://github.com/idrissneumann/elastic-indices-lifecycle

## Docker repository

The docker hub repository is here: https://hub.docker.com/repository/docker/comworkio/elastic-indices-lifecycle

The image is built either for ARM and x86 architecture. 

You can use the following tags for x86:

```shell
docker pull comworkio/elastic-indices-lifecycle:latest # x86
docker pull comworkio/elastic-indices-lifecycle:1.0 # x86
docker pull comworkio/elastic-indices-lifecycle:1.0-{sha} # x86
docker pull comworkio/elastic-indices-lifecycle:1.0-x86 # x86
docker pull comworkio/elastic-indices-lifecycle:1.0-{sha}-x86 # x86
```

You can use the following tags for arm:

```shell
docker pull comworkio/elastic-indices-lifecycle:latest-arm # x86
docker pull comworkio/elastic-indices-lifecycle:1.0-arm # x86
docker pull comworkio/elastic-indices-lifecycle:1.0-{sha}-arm # x86
```

## Deployment with docker

You can either mount a [json configuration file](https://gitlab.comwork.io/oss/elastic-indices-lifecycle/-/blob/master/rollup_conf.json) or use environment variable instead.

Here the environment variable you can use with your container :

* `ES_LIFECYCLE_elastic_hosts`: elastic domain name or host
* `ES_LIFECYCLE_elastic_port`: elastic port
* `ES_LIFECYCLE_elastic_scheme`: elastic scheme (`http` or `https`)
* `ES_LIFECYCLE_elastic_username`: username (need to have all rights on the cluster)
* `ES_LIFECYCLE_elastic_password`: password
* `ES_LIFECYCLE_wait_time`: wait time in seconds to perform the rollup jobs (default: 12h)
* `ES_LIFECYCLE_retention`: retention in days to remove the old indices (default: 30 days)
* `ES_LIFECYCLE_log_level`: log level (default: info)
* `ES_LIFECYCLE_should_slack`: `on` in order to enable Slack notification (default: `off`)
* `ES_LIFECYCLE_slack_token`: slack token
* `ES_LIFECYCLE_slack_username`: slack username to appear in the channels
* `ES_LIFECYCLE_slack_channel`: the channel
* `ES_LIFECYCLE_slack_emoji`: slack emoji that will be used as an avatar (default `:elastic:`, so you need to have an emoji that 
* `ES_LIFECYCLE_date_format`: the format of date that is used for your indices names (default: `%Y%m%d`, so your indices needs to looks like `{prefix}-20200101`)
* `ES_LIFECYCLE_index_prefixes`: the beginning of your indice names with comma as separator (example: `logs,metrics` will match for all indices that begin with `logs` or `metrics`, like `logs-myapp-20202001` for example).
* `ES_LIFECYCLE_index_suffixes`: the end f your indice names with comma as separator (example: `logs,metrics` will match for all indices that end with `logs` or `metrics` just before the date, like `myapp-logs-20202001` for example).

## Deployment with kubernetes

There will be a nice helm chart some days.

For now, you'll find an example of kubernetes yaml [here](https://gitlab.comwork.io/oss/elastic-indices-lifecycle/-/tree/master/kubernetes) files using kustomize in order to deploy two environments in a gitops way.

You'll see that you'll also need to create the missing secrets (using SealedSecret if you want to stay completly gitops).