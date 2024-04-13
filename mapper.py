import grpc
import kmeans_pb2
import kmeans_pb2_grpc
import os
import random
from concurrent import futures

class MapperServicer(kmeans_pb2_grpc.KMeansServicer):
    
    def __init__(self, address, port, id):
        self.address = address
        self.port = port
        self.id = id
    
    
    def Map(self, request, context):
        input_split = request.input_split
        centroids = request.centroids

        file = open("Input/points.txt", "r")
        points = []
        for line in file:
            point = kmeans_pb2.Point()
            point.x, point.y = map(float, line.split(sep=","))
            points.append(point)
        mapped_points = []
        file.close()

        for i in range(input_split.start_index, input_split.end_index + 1):
            point = kmeans_pb2.Point()
            point.x, point.y = points[i].x, points[i].y
            nearest_centroid_index = self.find_nearest_centroid(point, centroids)
            map_output = kmeans_pb2.MappedPoint()
            map_output.centroid_index = nearest_centroid_index
            map_output.data_point.x, map_output.data_point.y = point.x, point.y
            map_output.count = 1
            mapped_points.append(map_output)
            
        file.close()
        
        return kmeans_pb2.MapOutput(mapped_points=mapped_points)
    
        
    def Partition(self, request, context):
        map_outputs = request.mapped_points
        num_reducers = request.num_reducers
        
        num_points = len(map_outputs)
        partition_size = round(num_points / num_reducers)
        i = 0
        while num_points > 0:
            if os.path.isdir(f"Mappers/M{self.id}") == False:
                os.mkdir(f"Mappers/M{self.id}")
            if os.path.isfile(f"Mappers/M{self.id}/Partition{i}.txt") == False:
                file = open(f"Mappers/M{self.id}/Partition{i}.txt", "w")
                file.close()
            
            file = open(f"Mappers/M{self.id}/Partition{i}.txt", "w")
            
            for j in range(partition_size):
                if num_points == 0:
                    break
                map_output = map_outputs.pop(0)
                file.write(f"{map_output.centroid_index},{map_output.data_point.x},{map_output.data_point.y},{map_output.count}\n")
                num_points -= 1
            file.close()
            i += 1
    
        return kmeans_pb2.PartitionOutput(success=True)
            
        
    def find_nearest_centroid(self, point, centroids):
        min_distance = float('inf')
        nearest_centroid_index = -1
        for i, centroid in enumerate(centroids):
            distance = self.euclidean_distance(point, centroid)
            if distance < min_distance:
                min_distance = distance
                nearest_centroid_index = i
        return nearest_centroid_index


    def euclidean_distance(self, point1, point2):
        return (((point1.x - point2.x) ** 2) + ((point1.y - point2.y) ** 2)) ** 0.5


def serve(address, port, id):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mapper = MapperServicer(str(address), str(port), str(id))
    kmeans_pb2_grpc.add_KMeansServicer_to_server(mapper, server)
    server.add_insecure_port(f'{mapper.address}:{mapper.port}')
    server.start()
    server.wait_for_termination()
