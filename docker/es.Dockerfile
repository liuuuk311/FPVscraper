FROM docker.elastic.co/elasticsearch/elasticsearch:7.6.2
ENV bootstrap.memory_lock=true
ENV discovery.type=single-node