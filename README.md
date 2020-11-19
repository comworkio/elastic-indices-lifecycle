# Indices lifecycle utility for ElasticSearch

This project aims to provide a docker image that handle the rollup of elastic indices for you, in a cloud native or gitops way.
## Git repository

* main repo: https://gitlab.comwork.io/oss/elastic-indices-lifecycle
* github mirror backup: https://github.com/idrissneumann/elastic-indices-lifecycle

## Deployment with docker

```shell
docker pull comworkio/elastic-indices-lifecycle
```

You can either mount a [json configuration file](./purge_conf.json) or use environment variable instead.

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
* `ES_LIFECYCLE_slack_url`: slack custom integration url
* `ES_LIFECYCLE_slack_username`: slack username to appear in the channels
* `ES_LIFECYCLE_slack_channel`: the channel
* `ES_LIFECYCLE_slack_emoji`: slack emoji that will be used as an avatar (default `:elastic:`, so you need to have an emoji that 
* `ES_LIFECYCLE_date_format`: the format of date that is used for your indices names (default: `%Y%m%d`, so your indices needs to looks like `{prefix}-20200101`)
* `ES_LIFECYCLE_index_prefixes`: the beginning of your indice names with comma as separator (example: `logs,metrics` will match for all indices that begin with `logs` or `metrics`, like `logs-myapp-20202001` for example).
* `ES_LIFECYCLE_index_suffixes`: the end f your indice names with comma as separator (example: `logs,metrics` will match for all indices that end with `logs` or `metrics` just before the date, like `myapp-logs-20202001` for example).
