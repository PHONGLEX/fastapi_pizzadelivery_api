import base64
import pulumi
import pulumi_aws as aws
import pulumi_docker as docker
import pulumi_eks as eks
import pulumi_kubernetes as k8s

cluster = eks.Cluster('my-cluster');


repo = aws.ecr.Repository('fastapi-repo')
image_name = repo.repository_url

def get_registry_info(rid):
    """Get registry info (creds and endpoint)."""
    creds = aws.ecr.get_credentails(registry_id=rid)
    decoded = base64.b64decode(creds.authorization_token).decode()
    parts = decoded.split(':')
    if len(parts) != 2:
        raise Exception('Invalid credentials')
    return docker.ImageRegistry(creds.proxy_endpoint, parts[0], parts[1])
registry_info = repo.registry_id.apply(get_registry_info)

image = docker.Image('my-app-image',
    build='../app',
    image_name=image_name,
    registry=registry_info
)

app_name = 'fastapi-app'
app_labels = { 'app': app_name }
deployment = k8s.apps.v1.Deployment(f'{app_name}-dep',
    spec = k8s.apps.v1.DeploymentSpecArgs(
        selector = k8s.meta.v1.LabelSelectorArgs(match_labels = app_labels),
        replicas = 2,
        template = k8s.core.v1.PodTemplateSpecArgs(
            metadata = k8s.meta.v1.ObjectMetaArgs(labels = app_labels),
            spec = k8s.core.v1.PodSpecArgs(containers = [
                k8s.core.v1.ContainerArgs(
                    name = app_name,
                    image = image.image_name
                )
            ]),
        ),
    ), opts = pulumi.ResourceOptions(provider = cluster.provider)
)
service = k8s.core.v1.Service(f'{app_name}-svc',
    spec = k8s.core.v1.ServiceSpecArgs(
        type = 'LoadBalancer',
        selector = app_labels,
        ports = [ k8s.core.v1.ServicePortArgs(port = 80) ],
    ), opts = pulumi.ResourceOptions(provider = cluster.provider)
)

pulumi.export('ingress_ip', service.status.load_balancer.ingress[0].ip)

pulumi.export('kubeconfig', cluster.kubeconfig)