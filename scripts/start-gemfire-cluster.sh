gfsh -e "start locator --name=locator1 \
--log-level=config \
--http-service-port=5000 \
--initial-heap=500m \
--max-heap=500m"

gfsh -e "connect" -e "start server --name=server1 \
--server-port=50001 \
--http-service-port=5001 \
--start-rest-api=true \
--initial-heap=500m \
--max-heap=500m"

gfsh -e "start server --name=server2 \
--server-port=50002 \
--http-service-port=5002 \
--start-rest-api=true \
--initial-heap=500m \
--max-heap=500m"