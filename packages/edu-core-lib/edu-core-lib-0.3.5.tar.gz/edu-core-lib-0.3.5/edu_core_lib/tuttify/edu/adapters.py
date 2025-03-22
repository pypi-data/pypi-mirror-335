class MongoDataAdapterClass:
    connection: None

    def __init__(self, client):
        self.connection = client

    def get_data(self, collection, payload, **kwargs):
        collection = self.connection.get_collection(collection)
        result = list(collection.aggregate(payload))
        return result
