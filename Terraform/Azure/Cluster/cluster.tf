provider "azurerm" {
  features {
    
  }
}

locals {
  resource_group_name = "demo_cluster_rg"
  vnet_name = "demo_vnet"
  vnet_range = ["10.0.0.0/8"]
  cluster_subnet_name = "demo_subnet"
  cluster_subnet_range = ["10.1.0.0/16"]
  cluster_name = "demo_cluster"
  cluster_dns_label = "demo-cluster"
}

resource "azurerm_resource_group" "demo_cluster" {
    name = local.resource_group_name
    location = "South India" 
}

resource "azurerm_virtual_network" "demo_cluster" {
  name                = local.vnet_name
  address_space       = local.vnet_range
  location            = azurerm_resource_group.closet_server.location
  resource_group_name = azurerm_resource_group.closet_server.name
}

resource "azurerm_subnet" "demo_cluster" {
  name                 = local.cluster_subnet_name
  resource_group_name  = azurerm_resource_group.closet_server.name
  virtual_network_name = azurerm_virtual_network.closet_server.name
  address_prefixes     = local.cluster_subnet_range
}

resource "azurerm_kubernetes_cluster" "demo_cluster" {
  name                = local.cluster_name
  location            = azurerm_resource_group.demo_cluster.location
  resource_group_name = azurerm_resource_group.demo_cluster.name
  http_application_routing_enabled = true
  dns_prefix = local.cluster_dns_label

  default_node_pool {
    enable_auto_scaling = true
    max_count = 5
    min_count = 3
    enable_node_public_ip = true
    name       = "default"
    node_count = 3
    vm_size    = "Standard_B4ms"
    vnet_subnet_id = azurerm_subnet.demo_cluster.id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Production"
  }
}

output "kube_config" {
  value = azurerm_kubernetes_cluster.demo_cluster.kube_config_raw
  sensitive = true
}

provider "helm" {
  kubernetes {
    host = azurerm_kubernetes_cluster.demo_cluster.kube_config[0].host

    client_key             = base64decode(azurerm_kubernetes_cluster.demo_cluster.kube_config[0].client_key)
    client_certificate     = base64decode(azurerm_kubernetes_cluster.demo_cluster.kube_config[0].client_certificate)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.demo_cluster.kube_config[0].cluster_ca_certificate)
  }
}

## Any helm Releases can be added here