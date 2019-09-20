import pulumi
from pulumi_gcp import compute

network = compute.Network("network")
firewall = compute.Firewall(
    "firewall",
    network=network.id,
    allows=[dict(protocol="tcp", ports=["22", "80", "443"])],
)

addr = compute.address.Address("moria", region="us-west1")

startupScript = """#!/bin/bash
apt-get update
apt-get install -y docker.io
"""

instance = compute.Instance(
    "moria",
    machine_type="f1-micro",
    metadata_startup_script=startupScript,
    boot_disk=dict(
        initialize_params=dict(image="ubuntu-minimal-1804-bionic-v20190814")
    ),
    network_interfaces=[
        dict(network=network.id, access_configs=[dict(nat_ip=addr.address)])
    ],
    zone="us-west1-a",
    # By default, Pulumi tries to create a replacement instance *before*
    # tearing down the instance it's replacing. This is nice to avoid downtime,
    # but gets weird with static IPs. See
    # https://github.com/pulumi/pulumi-gcp/issues/114 for more information.
    opts=pulumi.resource.ResourceOptions(delete_before_replace=True),
)

pulumi.export("external_ip", addr.address)
