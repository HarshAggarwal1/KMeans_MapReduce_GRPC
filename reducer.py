import grpc
import kmeans_pb2
import kmeans_pb2_grpc
import os
from concurrent import futures
import mapper

class ReducerServicer(kmeans_pb2_grpc.KMeansServicer):
    
    def __init__(self, address, port, id):
        self.address = address
        self.port = port
        self.id = id
        
    
    def Reduce(self, request, context):
        centroid_index = request.centroid_id
        num_mappers = request.num_mappers
        points = self.shuffle_and_sort(num_mappers=num_mappers)
        
        sum_x = 0.0
        sum_y = 0.0
        count = 0
        
        for point in points:
            if point.centroid_index != centroid_index:
                continue
            sum_x += point.data_point.x
            sum_y += point.data_point.y
            count += point.count
        
        if count == 0:
            return kmeans_pb2.ReduceOutput(centroid_id=centroid_index, updated_centroid=point.data_point, success=False)
        
        new_centroid = kmeans_pb2.Point()
        new_centroid.x = sum_x / count
        new_centroid.y = sum_y / count
        
        if os.path.isfile(f"Reducers/R{self.id}.txt") == False:
            file = open(f"Reducers/R{self.id}.txt", "w")
            file.close()
        
        file = open(f"Reducers/R{self.id}.txt", "a+")
        file.write(f"{centroid_index},{new_centroid.x},{new_centroid.y}\n")
        
        return kmeans_pb2.ReduceOutput(centroid_id=centroid_index, updated_centroid=new_centroid, success=True)

    
    def shuffle_and_sort(self, num_mappers):
        shuffled_points = []
        for i in range(num_mappers):
            channel = grpc.insecure_channel(f"localhost:6005{i + 1}")
            stub = kmeans_pb2_grpc.KMeansStub(channel)
            mapper_to_reducer_input = kmeans_pb2.MapperToReducerInput(address=f'{self.address}:{self.port}', id=self.id)
            response = stub.MapperToReducer(mapper_to_reducer_input)
            channel.close()
            shuffled_points.extend(response.mapped_points)
        shuffled_points.sort(key=lambda x: x.centroid_index)
        return shuffled_points
        

def serve(address, port, id):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reducer = ReducerServicer(str(address), str(port), str(id))
    kmeans_pb2_grpc.add_KMeansServicer_to_server(reducer, server)
    server.add_insecure_port(f'{reducer.address}:{reducer.port}')
    server.start()
    server.wait_for_termination()
    