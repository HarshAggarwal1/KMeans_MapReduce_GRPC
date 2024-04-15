import grpc
import kmeans_pb2
import kmeans_pb2_grpc
import os
import random
import multiprocessing
from concurrent import futures
import mapper
import reducer
import datetime
import time

class MasterServicer(kmeans_pb2_grpc.KMeansServicer):
    def Run(self, request, context):
        
        num_mappers = request.num_mappers
        num_reducers = request.num_reducers
        num_iterations = request.num_iterations
        num_centroids = request.num_centroids
        
        file = open("Input/points.txt", "r")
        points = []
        for line in file:
            point = kmeans_pb2.Point()
            point.x, point.y = map(float, line.split(sep=","))
            points.append(point)
        file.close()
        
        centroids = []
        for i in range(num_centroids):
            centroids.append(random.choice(points))
        
        for i in range(num_iterations):
            
            for _, _, files in os.walk("Reducers"):
                for file in files:
                    os.remove(f"Reducers/{file}")
            
            new_centroids = self.work(num_mappers, num_reducers, num_iterations, num_centroids, points, centroids)
            
            if self.check_convergence(new_centroids, centroids):
                break
            else:
                centroids = new_centroids
                
        # write the final centroids to a file
        if os.path.isfile("centroids.txt") == False:
            file = open("centroids.txt", "w")
            file.close()
        
        file = open("centroids.txt", "w")
        for centroid in centroids:
            file.write(f"{centroid.x},{centroid.y}\n")
        file.close()
        
        return kmeans_pb2.CentroidCompilationOutput(centroids=centroids)
    
    
    def check_convergence(self, new_centroids, centroids):
        for i in range(len(new_centroids)):
            if new_centroids[i].x != centroids[i].x or new_centroids[i].y != centroids[i].y:
                return False
        return True
        
        
    def work(self, num_mappers, num_reducers, num_iterations, num_centroids, points, centroids):
       
       # ======================================================================================================================= #
       
        new_centroids = []
        for i in range(num_centroids):
            new_centroids.append(kmeans_pb2.Point())
            
        # ======================================================================================================================= #
        
        map_tasks = []
        for i in range(num_mappers):
            map_task = multiprocessing.Process(target=mapper.serve, args=("localhost", f"6005{i + 1}", i + 1))
            try:
                map_task.start()
                map_tasks.append(map_task)
            except Exception as e:
                print(e)
        
        num_points = round(len(points) / num_mappers)
        for i in range(num_mappers):
            channel = grpc.insecure_channel(f"localhost:6005{i + 1}")
            stub = kmeans_pb2_grpc.KMeansStub(channel)
            
            input_split = kmeans_pb2.InputSplit()
            input_split.start_index = i * num_points
            input_split.end_index = min((i + 1) * num_points - 1, len(points) - 1)
            map_input = kmeans_pb2.MapInput(input_split=input_split, centroids=centroids)
            response = stub.Map(map_input)
            
            partition_input = kmeans_pb2.PartitionInput(mapped_points=response.mapped_points, num_reducers=num_reducers)
            response = stub.Partition(partition_input)
            
            if response.success:
                print(f"Partitioning by Mapper {i + 1} successful")
            
            channel.close()
        
        for task in map_tasks:
            task.terminate()
        
        # ========================================================================================================================= #
        
        reduce_tasks = []
        for i in range(num_reducers):
            reduce_task = multiprocessing.Process(target=reducer.serve, args=("localhost", f"7005{i + 1}", i + 1))
            try:
                reduce_task.start()
                reduce_tasks.append(reduce_task)
            except Exception as e:
                print(e)
        
        num_centroids_per_reducer = round(num_centroids / num_reducers)
        num_centroids_remaining = num_centroids
        index = 0
        for i in range(num_reducers):
            channel = grpc.insecure_channel(f"localhost:7005{i + 1}")
            stub = kmeans_pb2_grpc.KMeansStub(channel)
            
            for j in range(min(num_centroids_per_reducer, num_centroids_remaining)):
                reduce_input = kmeans_pb2.ReduceInput(centroid_id=index)
                response = stub.Reduce(reduce_input)
                new_centroids[response.centroid_id] = response.updated_centroid
                index += 1
            
            num_centroids_remaining -= num_centroids_per_reducer
            
            if response.success:
                print(f"Reducing by Reducer {i + 1} successful")
            
            channel.close()
        
        for task in reduce_tasks:
            task.terminate()
                                
        return new_centroids

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    master = MasterServicer()
    kmeans_pb2_grpc.add_KMeansServicer_to_server(master, server)
    server.add_insecure_port('localhost:50051')
    server.start()
    channel = grpc.insecure_channel("localhost:50051")
    stub = kmeans_pb2_grpc.KMeansStub(channel)
    stub.Run(kmeans_pb2.MasterInput(num_mappers=5, num_reducers=2, num_iterations=50, num_centroids=8))


if __name__ == "__main__":
    serve()
        
        