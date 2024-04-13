import grpc
import kmeans_pb2
import kmeans_pb2_grpc
import os
import random
from concurrent import futures
import mapper
import datetime
import time

class ReducerServicer(kmeans_pb2_grpc.KMeansServicer):
    
    def __init__(self, address, port, id):
        self.address = address
        self.port = port
        self.id = id
        
    
    def Reduce(self, request, context):
        centroid_index = request.centroid_id
        points = self.shuffle_and_sort(centroid_index=centroid_index)
        
        sum_x = 0.0
        sum_y = 0.0
        count = 0
        
        for point in points:
            sum_x += point.data_point.x
            sum_y += point.data_point.y
            count += point.count
        
        new_centroid = kmeans_pb2.Point()
        new_centroid.x = sum_x / count
        new_centroid.y = sum_y / count
        
        if os.path.isfile(f"Reducers/R{self.id}.txt") == False:
            file = open(f"Reducers/R{self.id}.txt", "w")
            file.close()
        
        file = open(f"Reducers/R{self.id}.txt", "a+")
        file.write(f"{centroid_index},{new_centroid.x},{new_centroid.y}\n")
        
        return kmeans_pb2.ReduceOutput(centroid_id=centroid_index, updated_centroid=new_centroid, success=True)

    
    def shuffle_and_sort(self, centroid_index):
        shuffled_points = []
        for _, dirs, _ in os.walk("Mappers"):
            for dir in dirs:
                for _, _, files in os.walk(f"Mappers/{dir}"):
                    for file in files:
                        file = open(f"Mappers/{dir}/{file}", "r")
                        for line in file:
                            mapped_point = kmeans_pb2.MappedPoint()
                            mapped_point.centroid_index = int(line.split(",")[0])
                            mapped_point.data_point.x = float(line.split(",")[1])
                            mapped_point.data_point.y = float(line.split(",")[2])
                            mapped_point.count = int(line.split(",")[3])
                            if mapped_point.centroid_index == centroid_index:
                                shuffled_points.append(mapped_point) 
                        file.close()
        return shuffled_points
        

def serve(address, port, id):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reducer = ReducerServicer(str(address), str(port), str(id))
    kmeans_pb2_grpc.add_KMeansServicer_to_server(reducer, server)
    server.add_insecure_port(f'{reducer.address}:{reducer.port}')
    server.start()
    server.wait_for_termination()
    