import argparse
from kubernetes import client, config

# Load Kubernetes configuration
config.load_kube_config()

# Create CoreV1Api and AppsV1Api clients
apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

# Define a function to get the ID of the PersistentVolume used by the last Replica instance in a StatefulSet
def get_last_replica_persistent_volume_id(statefulset_name, namespace):
    try:
        # Get the details of the StatefulSet
        statefulset = apps_v1.read_namespaced_stateful_set(statefulset_name, namespace)
        # Get the number of replicas in the StatefulSet
        replicas = statefulset.spec.replicas
        # Construct the name of the last Pod
        last_pod_name = f"{statefulset_name}-{replicas - 1}"
        # Get the status of the last Pod
        pod = core_v1.read_namespaced_pod(last_pod_name, namespace)
        # Get the name of the PersistentVolumeClaim used by the last Pod
        pvc_name = None
        for volume in pod.spec.volumes:
            if volume.persistent_volume_claim:
                pvc_name = volume.persistent_volume_claim.claim_name
                break
        if not pvc_name:
            return None
        # Get the details of the PersistentVolume corresponding to the PersistentVolumeClaim
        pv = core_v1.read_namespaced_persistent_volume_claim(pvc_name, namespace)
        # Get the ID of the PersistentVolume
        pv_id = pv.spec.volume_name
        return pv_id
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Get the PersistentVolume ID for the last replica in a StatefulSet.')
parser.add_argument('statefulset_name', type=str, help='The name of the StatefulSet')
parser.add_argument('namespace', type=str, help='The namespace of the StatefulSet')
args = parser.parse_args()

# Call the function to get the ID of the PersistentVolume used by the last replica in the StatefulSet
pv_id = get_last_replica_persistent_volume_id(args.statefulset_name, args.namespace)

if pv_id:
    print(f"{pv_id}")
else:
    print("No PersistentVolume found for the last replica in StatefulSet.")
    exit(1)
