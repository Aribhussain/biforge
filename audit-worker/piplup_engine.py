import os
import sys
from pymongo import MongoClient
from opensearchpy import OpenSearch

# 1. Dynamically resolve the absolute path to the local PIPLUP directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'PIPLUP'))
from piplup import PiplupParser 

# Environment Variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://tf_admin:biforge_pass_2026@mongodb:27017/?authSource=admin")
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")

# Initialize Clients
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['biforge']
cluster_collection = db['template_registry']
os_client = OpenSearch([OPENSEARCH_URL])
INDEX_NAME = "biforge-ocsf-logs"

# 2. Restore the expected function name for the main daemon
def run_piplup_reconciliation():
    print("Checking MongoDB for unaudited Drain3 clusters...")
    unaudited_clusters = list(cluster_collection.find({"audited": False}))
    
    if not unaudited_clusters:
        print("No new clusters to audit.")
        return {"status": "success", "refined_clusters": 0}

    parser = PiplupParser()
    count = 0
    
    for cluster in unaudited_clusters:
        cluster_id = cluster['cluster_id']
        drain3_template = cluster['template']
        raw_logs = cluster.get('sample_logs', [])
        
        if not raw_logs:
            continue
            
        # Run PIPLUP statistical analysis
        piplup_result = parser.parse(raw_logs)
        piplup_template = piplup_result.get('template', '')
        
        # Determine parser_confidence
        confidence = "high" if drain3_template == piplup_template else "corrected"
            
        # Update MongoDB state
        cluster_collection.update_one(
            {"_id": cluster["_id"]},
            {"$set": {"audited": True, "piplup_template": piplup_template, "confidence": confidence}}
        )
        
        # Bulk update OpenSearch documents associated with this trace
        update_query = {
            "query": {
                "term": {"drain_cluster_id": cluster_id}
            },
            "script": {
                "source": f"ctx._source.parser_confidence = '{confidence}'",
                "lang": "painless"
            }
        }
        try:
            os_client.update_by_query(index=INDEX_NAME, body=update_query)
        except Exception as e:
            print(f"Failed to update OpenSearch: {e}")
            
        print(f"Audited Cluster {cluster_id}: Tagged as {confidence}.")
        count += 1
        
    return {"status": "success", "refined_clusters": count}