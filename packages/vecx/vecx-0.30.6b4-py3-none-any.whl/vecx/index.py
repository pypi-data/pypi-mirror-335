import requests, json, zlib
import numpy as np
from google.protobuf.json_format import Parse, MessageToJson
from .libvx import LibVectorX as Vxlib
from .crypto import get_checksum,json_zip,json_unzip
from .exceptions import raise_exception
from .vecx_pb2 import VectorObject, VectorBatch, ResultSet, VectorResult

class Index:
    def __init__(self, name:str, key:str, token:str, url:str, version:int=1, params=None):
        self.name = name
        self.key = key
        self.token = token
        self.url = url
        self.version = version
        self.checksum = get_checksum(self.key)
        self.lib_token = params["lib_token"]
        self.count = params["total_elements"]
        self.space_type = params["space_type"]
        self.dimension = params["dimension"]
        self.precision = "float16" if params["use_fp16"] else "float32"
        self.M = params["M"]

        if key:
            self.vxlib = Vxlib(key=key, lib_token=self.lib_token, space_type=self.space_type, version=version, dimension=self.dimension)
        else:
            self.vxlib = None

    def __str__(self):
        return self.name
    
    def _normalize_vector(self, vector):
        # Normalize only if using cosine distance
        if self.space_type != "cosine":
            return vector, 1.0
        vector = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector, 1.0
        normalized_vector = vector / norm
        return normalized_vector, float(norm)

    def upsert(self, input_array):
        if len(input_array) > 1000:
            raise ValueError("Cannot insert more than 1000 vectors at a time")
        
        # Process all vectors in a single batch
        vector_batch = VectorBatch()
        
        for item in input_array:
            # Prepare vector object
            vector_obj = VectorObject()
            vector_obj.id = str(item.get('id', ''))
            vector_obj.filter = json.dumps(item.get('filter', ""))
            # Meta is zipped
            meta = json_zip(dict=item.get('meta', ""))
            vector, norm = self._normalize_vector(item['vector'])
            vector_obj.norm = norm
            # Encrypt vector and meta only if checksum is valid
            if self.vxlib:
                vector = self.vxlib.encrypt_vector(vector)
                meta = self.vxlib.encrypt_meta(meta)
            vector_obj.meta = meta
            vector_obj.vector.extend(vector)

            # Add to batch
            vector_batch.vectors.append(vector_obj)
        
        # Serialize batch
        serialized_data = vector_batch.SerializeToString()
        
        # Prepare headers
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/x-protobuf'
        }

        # Send request
        response = requests.post(
            f'{self.url}/index/{self.name}/vector/insert', 
            headers=headers, 
            data=serialized_data
        )

        if response.status_code != 200:
            raise_exception(response.status_code, response.text)

        return "Vectors inserted successfully"
    
    def query(self, vector, top_k=10, filter=None, include_vectors=False, log=False):
        if top_k > 100:
            raise ValueError("top_k cannot be greater than 100")
        checksum = get_checksum(self.key)

        # Normalize query vector if using cosine distance
        norm=1.0
        if self.space_type == "cosine":
            vector, norm = self._normalize_vector(vector)

        original_vector = vector
        if self.vxlib:
            vector = self.vxlib.encrypt_vector(vector)
            top_k += 5  # Add some extra results for over-fetching and re-scoring
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'vector': vector.tolist(),
            'k': top_k,
            'include_vectors': include_vectors
        }
        if filter:
            data['filter'] = json.dumps(filter)
        response = requests.post(f'{self.url}/index/{self.name}/search', headers=headers, json=data)
        if response.status_code != 200:
            raise_exception(response.status_code, response.text)

        # Parse protobuf ResultSet
        result_set = ResultSet()
        result_set.ParseFromString(response.content)

        # Convert to a more Pythonic list of dictionaries
        vectors = []
        processed_results = []
        for result in result_set.results:
            processed_result = {
                'id': result.id,
                'distance': result.distance,
                'similarity': 1 - result.distance,
                'meta': json_unzip(self.vxlib.decrypt_meta(result.meta)) if self.vxlib else json_unzip(result.meta),
            }
            # Filter will come as "" - default value in protobuf
            if filter != "":
                processed_result['filter'] = json.loads(result.filter)

            # Include vector if requested and available
            if include_vectors or self.vxlib:
                processed_result['vector'] = list(self.vxlib.decrypt_vector(result.vector)) if self.vxlib else list(result.vector)
                vectors.append(np.array(processed_result['vector'],dtype=np.float32))

            processed_results.append(processed_result)
        
        # If using encryption, rescore the results
        top_k -= 5
        if self.vxlib:
            distances = self.vxlib.calculate_distances(query_vector=original_vector,vectors=vectors)
            # Set distace and similarity in processed results
            for i, result in enumerate(processed_results):
                result['distance'] = distances[i]
                result['similarity'] = 1 - distances[i]
            # Now sort processed results by distance inside processed result
            processed_results = sorted(processed_results, key=lambda x: x['distance'])
            # Return only top_k results
            processed_results = processed_results[:top_k]
            #print(distances)
            # If include_vectors is False then remove the vectors from the result
            if not include_vectors:
                for result in processed_results:
                    result.pop('vector', None)

        return processed_results

    def delete_vector(self, id):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
            }
        response = requests.delete(f'{self.url}/index/{self.name}/vector/{id}/delete', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        return response.text + " rows deleted"
    
    # Delete multiple vectors based on a filter
    def delete_with_filter(self, filter):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
            }
        data = {"filter": filter}
        print(filter)
        response = requests.delete(f'{self.url}/index/{self.name}/vectors/delete', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        return response.text
    
    # Get a single vector by id
    def get_vector(self, id):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
            }
        response = requests.get(f'{self.url}/index/{self.name}/vector/{id}', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        # Parse the protobuf response
        vector_obj = VectorObject()
        vector_obj.ParseFromString(response.content)
        response = {
                'id': vector_obj.id,
                'filter': vector_obj.filter,
                'norm': vector_obj.norm,
                'meta': json_unzip(self.vxlib.decrypt_meta(vector_obj.meta)) if self.vxlib else json_unzip(vector_obj.meta),
                'vector': list(self.vxlib.decrypt_vector(vector_obj.vector)) if self.vxlib else list(vector_obj.vector)
            }

        return response
        
    def describe(self):
        data = {
            "name": self.name,
            "space_type": self.space_type,
            "dimension": self.dimension,
            "count": self.count,
            "precision": self.precision,
            "M": self.M,
        }
        return data
    

