provider "azurerm" {
  features {
    
  }
}

locals {
  resource_group_name = "demo_vm"
  vnet_name = "demo_vm_vnet"
  vnet_range = ["10.0.0.0/8"]
  vm_name = "demo_vm"
  vm_dns_label = "demo-vm"
  vm_pip_name = "demo_vm_pip"
  vm_subnet_name = "demo_vm_subnet"
  vm_subnet_range = ["10.2.0.0/24"]
  vm_ip_interface = "demo_vm_if"
  vm_username = "azureuser"
  vm_password = "autoadminterraform@123"
}

resource "azurerm_resource_group" "demo_vm" {
    name = local.resource_group_name
    location = "South India" 
}

resource "azurerm_virtual_network" "demo_vm" {
  name                = local.vnet_name
  address_space       = local.vnet_range
  location            = azurerm_resource_group.demo_vm.location
  resource_group_name = azurerm_resource_group.demo_vm.name
}

resource "azurerm_subnet" "demo_vm_bastion" {
  name                 = local.vm_subnet_name
  resource_group_name  = azurerm_resource_group.demo_vm.name
  virtual_network_name = azurerm_virtual_network.demo_vm.name
  address_prefixes     = local.vm_subnet_range
}

resource "azurerm_public_ip" "demo_vm" {
  name                    = local.vm_pip_name
  location                = azurerm_resource_group.demo_vm.location
  resource_group_name     = azurerm_resource_group.demo_vm.name
  allocation_method       = "Dynamic"
  idle_timeout_in_minutes = 30
  domain_name_label = local.vm_dns_label

}

resource "azurerm_network_interface" "demo_vm" {
  name                = local.vm_ip_interface
  location            = azurerm_resource_group.demo_vm.location
  resource_group_name = azurerm_resource_group.demo_vm.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.demo_vm.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.demo_vm.id
  }
}

resource "azurerm_linux_virtual_machine" "demo_vm" {
  name                = local.vm_name
  resource_group_name = azurerm_resource_group.demo_vm.name
  location            = azurerm_resource_group.demo_vm.location
  size                = "Standard_B2s"
  admin_username      = local.vm_username
  admin_password      = local.vm_password
  disable_password_authentication = false
  
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }

  source_image_reference {
    publisher = "canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
  
  network_interface_ids = [
    azurerm_network_interface.demo_vm.id,
  ]

  custom_data = filebase64("vm_init.sh")

}