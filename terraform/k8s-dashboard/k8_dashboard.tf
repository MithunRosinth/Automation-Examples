resource "helm_release" "kubernetes_dashboard" {
  name       = "kubernetes-dashboard"
  repository = "https://kubernetes.github.io/dashboard/"
  chart      = "kubernetes-dashboard"
  create_namespace = true
  namespace  = "kubernetes-dashboard"
  set {
    name  = "service.type"
    value = "LoadBalancer"
  }
  set {
    name  = "service.externalPort"
    value = "9080"
  }
## Specific to azure dns
##  set {
##    name ="service.annotations.service\\.beta\\.kubernetes\\.io/azure-dns-label-name"
##    value = <Value>
##  }  
  set {
    name  = "protocolHttp"
    value = "true"
  }
  set {
    name  = "enableInsecureLogin"
    value = "true"
  }
  set {
    name  = "rbac.clusterReadOnlyRole"
    value = "true"
  }
  set {
    name  = "metricsScraper.enabled"
    value = "true"
  }
  wait = true
}