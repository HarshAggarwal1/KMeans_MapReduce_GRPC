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
        self.num_centroids = 0
    
    
    def Map(self, request, context):
        input_split = request.input_split
        centroids = request.centroids
        
        self.num_centroids = len(centroids)

        file = open("Data/Input/points.txt", "r")
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
        
        return kmeans_pb2.MapOutput(mapped_points=mapped_points, success=True)
    
        
    def Partition(self, request, context):
        map_outputs = request.mapped_points
        num_reducers = request.num_reducers
        
        centroids_list = []
        for i in range(self.num_centroids):
            centroids_list.append(i)
            
        centroids = set(centroids_list)
        
        num_points = len(map_outputs)
        num_centroid_per_reducer = round(len(centroids) / num_reducers)
        reducers_left = num_reducers
        i = 0
        while reducers_left > 0:
            if os.path.isdir(f"Data/Mappers/M{self.id}") == False:
                os.mkdir(f"Data/Mappers/M{self.id}")
            if os.path.isfile(f"Data/Mappers/M{self.id}/Partition{i}.txt") == False:
                file = open(f"Data/Mappers/M{self.id}/Partition{i}.txt", "w")
                file.close()
            
            file = open(f"Data/Mappers/M{self.id}/Partition{i}.txt", "w")
            
            times = num_centroid_per_reducer
            
            if (reducers_left == 1):
                times = len(centroids)
            
            for _ in range(times):
                c_ind = centroids.pop()
                for map_output in map_outputs:
                    if map_output.centroid_index == c_ind and num_points > 0:
                        file.write(f"{map_output.centroid_index},{map_output.data_point.x},{map_output.data_point.y},{map_output.count}\n")
                        num_points -= 1
            
            file.close()
            reducers_left -= 1
            i += 1
    
        return kmeans_pb2.PartitionOutput(success=True)

    
    def MapperToReducer(self, request, context):
        reducer_id = int(request.id)
        mapped_points = []
        
        if os.path.isfile(f"Data/Mappers/M{self.id}/Partition{reducer_id - 1}.txt") == False:
            return kmeans_pb2.MapperToReducerOutput(mapped_points=mapped_points, success=True)
        
        file = open(f"Data/Mappers/M{self.id}/Partition{reducer_id - 1}.txt", "r")
        
        
        for line in file:
            mapped_point = kmeans_pb2.MappedPoint()
            mapped_point.centroid_index = int(line.split(sep=",")[0])
            mapped_point.data_point.x = float(line.split(sep=",")[1])
            mapped_point.data_point.y = float(line.split(sep=",")[2])
            mapped_point.count = int(line.split(sep=",")[3])
            mapped_points.append(mapped_point)
            
        file.close()
        
        return kmeans_pb2.MapperToReducerOutput(mapped_points=mapped_points, success=True)
            
        
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
