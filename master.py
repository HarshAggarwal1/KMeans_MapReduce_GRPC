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
        
        file = open("Data/Input/points.txt", "r")
        points = []
        for line in file:
            point = kmeans_pb2.Point()
            point.x, point.y = map(float, line.split(sep=","))
            points.append(point)
        file.close()
        
        centroids = []
        for i in range(num_centroids):
            centroids.append(random.choice(points))
            
        ff = open("Dump.txt", "a+")
        ff.write(f"{datetime.datetime.now()} - Initial centroids: {centroids}\n") #
        ff.close()
        
        for i in range(num_iterations):
            ff = open("Dump.txt", "a+")
            ff.write(f"=======================================================================\n") #
            ff.write(f"{datetime.datetime.now()} - Iteration {i + 1}\n") #
            ff.close()
            for _, _, files in os.walk("Data/Reducers"):
                for file in files:
                    os.remove(f"Data/Reducers/{file}")        
            
            new_centroids = self.work(num_mappers, num_reducers, num_centroids, points, centroids)
            
            ff = open("Dump.txt", "a+")
            if self.check_convergence(new_centroids, centroids):
                ff.write(f"{datetime.datetime.now()} - Converged at Iteration: {i + 1}\n") #
                break
            else:
                centroids = new_centroids
                ff.write(f"{datetime.datetime.now()} - Updated centroids: {centroids}\n") #
            ff.close()
            
                
        # write the final centroids to a file
        if os.path.isfile("Data/centroids.txt") == False:
            file = open("Data/centroids.txt", "w")
            file.close()
        
        file = open("Data/centroids.txt", "w")
        for centroid in centroids:
            file.write(f"{centroid.x},{centroid.y}\n")
        file.close()
        
        ff = open("Dump.txt", "a+")
        ff.write(f"=======================================================================\n") #
        ff.write(f"{datetime.datetime.now()} - Final centroids: {centroids}\n") #
        ff.write(f"=======================================================================\n") #
        ff.close()
        
        return kmeans_pb2.CentroidCompilationOutput(centroids=centroids)
    
    
    def check_convergence(self, new_centroids, centroids):
        for i in range(len(new_centroids)):
            if abs(new_centroids[i].x - centroids[i].x) > 0.0001 or abs(new_centroids[i].y - centroids[i].y) > 0.0001:
                return False
        return True
        
        
    def work(self, num_mappers, num_reducers, num_centroids, points, centroids):
        
        ff = open("Dump.txt", "a+") #
       
       # ======================================================================================================================= #
        new_centroids = []
        for i in range(num_centroids):
            new_centroids.append(kmeans_pb2.Point())
            
        # ======================================================================================================================= #
        
        map_tasks = []
        map_tasks_address = []
        for i in range(num_mappers):
            map_task = multiprocessing.Process(target=mapper.serve, args=("localhost", f"6005{i + 1}", i + 1))
            map_tasks_address.append(f"localhost:6005{i + 1}")
            ff.write(f"{datetime.datetime.now()} - Mapper {i + 1} started\n") #
            try:
                map_task.start()
                map_tasks.append(map_task)
            except Exception as e:
                print(e)
        map_tasks_addresses = set(map_tasks_address)
        
        
        num_points = round(len(points) / num_mappers)
        while len(map_tasks_addresses) > 0:
            temp_address = map_tasks_addresses.pop()
            channel = grpc.insecure_channel(temp_address)
            
            try:
                stub = kmeans_pb2_grpc.KMeansStub(channel)
                input_split = kmeans_pb2.InputSplit()
                input_split.start_index = i * num_points
                input_split.end_index = min((i + 1) * num_points - 1, len(points) - 1)
                map_input = kmeans_pb2.MapInput(input_split=input_split, centroids=centroids)
                response = stub.Map(map_input)
                if response.success:
                    ff.write(f"{datetime.datetime.now()} - Mapping by Mapper ({temp_address}) successful\n") #
                
                partition_input = kmeans_pb2.PartitionInput(mapped_points=response.mapped_points, num_reducers=num_reducers)
                response = stub.Partition(partition_input)
                if response.success:
                    ff.write(f"{datetime.datetime.now()} - Partitioning by Mapper ({temp_address}) successful\n") #
                
                if response.success:
                    print(f"Partitioning by Mapper ({temp_address}) successful")
            
            except Exception as e:
                map_tasks_addresses.add(temp_address)
                ff.write(f"{datetime.datetime.now()} - Error in Mapper {i + 1}\n") #
                
            channel.close()
        
        
        # ========================================================================================================================= #
        
        reduce_tasks = []
        reduce_tasks_address = []
        for i in range(num_reducers):
            reduce_task = multiprocessing.Process(target=reducer.serve, args=("localhost", f"7005{i + 1}", i + 1))
            reduce_tasks_address.append(f"localhost:7005{i + 1}")
            ff.write(f"{datetime.datetime.now()} - Reducer {i + 1} started\n") #
            try:
                reduce_task.start()
                reduce_tasks.append(reduce_task)
            except Exception as e:
                print(e)
        reduce_tasks_addresses = set(reduce_tasks_address)
        
        while len(reduce_tasks_addresses) > 0:
            temp_address = reduce_tasks_addresses.pop()
            channel = grpc.insecure_channel(temp_address)
            
            try:
                stub = kmeans_pb2_grpc.KMeansStub(channel)
                
                for j in range(num_centroids):
                    reduce_input = kmeans_pb2.ReduceInput(num_mappers=num_mappers, centroid_id=j)
                    response = stub.Reduce(reduce_input)
                    if response.done:
                        new_centroids[response.centroid_id] = response.updated_centroid
                
                if response.success:
                    ff.write(f"{datetime.datetime.now()} - Reducing by Reducer ({temp_address}) successful\n") #
                    print(f"Reducing by Reducer ({temp_address}) successful")
            except Exception as e:
                reduce_tasks_addresses.add(temp_address)
                ff.write(f"{datetime.datetime.now()} - Error in Reducer ({temp_address})\n")
            
            channel.close()
        
        for i in range(len(map_tasks)):
            ff.write(f"{datetime.datetime.now()} - Mapper {i + 1} terminated\n") #
            map_tasks[i].terminate()
            
        for i in range(len(reduce_tasks)):
            ff.write(f"{datetime.datetime.now()} - Reducer {i + 1} terminated\n")
            reduce_tasks[i].terminate()
                            
        ff.close()    
        return new_centroids

def serve():
    if os.path.isfile("Data/Input/points.txt") == False:
        print("Data/Input/points.txt does not exist")
        return
    if os.path.isfile("Dump.txt"):
        os.remove("Dump.txt")
    if os.path.isfile("Dump.txt") == False:
        file = open("Dump.txt", "w")
        file.close()
    
    file = open("Dump.txt", "a+")
    file.write(f"{datetime.datetime.now()} - Server started at: localhost:50051\n") #
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    master = MasterServicer()
    kmeans_pb2_grpc.add_KMeansServicer_to_server(master, server)
    server.add_insecure_port('localhost:50051')
    server.start()
    channel = grpc.insecure_channel("localhost:50051")
    stub = kmeans_pb2_grpc.KMeansStub(channel)
    
    num_mappers = int(input("Enter the number of mappers: "))
    num_reducers = int(input("Enter the number of reducers: "))
    num_iterations = int(input("Enter the number of iterations: "))
    num_centroids = int(input("Enter the number of centroids: "))
    
    file.write(f"{datetime.datetime.now()} - Master started with {num_mappers} mappers, {num_reducers} reducers, {num_iterations} iterations, and {num_centroids} centroids\n") #
    file.close()
    
    stub.Run(kmeans_pb2.MasterInput(num_mappers=num_mappers, num_reducers=num_reducers, num_iterations=num_iterations, num_centroids=num_centroids))


if __name__ == "__main__":
    serve()
        
        