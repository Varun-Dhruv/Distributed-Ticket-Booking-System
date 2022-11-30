:load
start cmd /k python LoadBalancer.py 5555
timeout 2
start cmd /k python CriticalResourceServer.py 4000 127.0.0.1 5500
timeout 2
start cmd /k python ServerNode.py node_1
timeout 2
start cmd /k python ServerNode.py node_2
timeout 2
start cmd /k python ServerNode.py node_3
timeout 2
start cmd /k python DBNode.py db_node_1 --is_beacon True
timeout 2
 start cmd /k python DBNode.py db_node_2
timeout 2
start cmd /k python DBNode.py db_node_3
timeout 2
start cmd /k python client.py 5555