resource "helm_release" "sonarqube" {
  name = "sonarqube"
  repository = "https://SonarSource.github.io/helm-chart-sonarqube"
  chart = "sonarqube"
  namespace = "sonarqube"
  create_namespace = true

  set {
    name = "service.type"
    value = "LoadBalancer"
  }
## Specific to azure dns
##  set {
##    name ="service.annotations.service\\.beta\\.kubernetes\\.io/azure-dns-label-name"
##    value = <Value>
##  }  
  set {
    name = "account.adminPassword"
    value = local.sonar_password
  }
}