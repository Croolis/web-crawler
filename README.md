# web-crawler

1. Изменить в web-crawler/scheduler/etc/supervisord.conf.d/tasktiger.conf и web-crawler/scheduler/etc/worker.sh IP-адреса на адрес хоста, на котором будет развораичваться приложение.
2. `cd scheduler`
3. `docker build -f master.dockerfile -t scheduler . && docker build -f worker.dockerfile -t scheduler_worker .`
4. `docker run --rm -d -p 80:80 -p 6379:6379 scheduler && sleep 2 && docker run --rm -d scheduler_worker`