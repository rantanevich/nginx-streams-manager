Vagrant.configure("2") do |config|
  config.ssh.insert_key = false
  config.vm.synced_folder '.', '/vagrant',
    type: "nfs",
    nfs_version: 4,
    disabled: true

  config.vm.define "node-1" do |machine|
    machine.vm.box = "centos/7"
    machine.vm.hostname = "node-1"
    machine.vm.network :private_network,
      :ip => "192.168.1.10",
      :libvirt__network_name => "vagrant-net-1"

    machine.vm.provider :libvirt do |hv|
      hv.cpus = 2
      hv.memory = 1024
      hv.management_network_name = "vagrant-mgmt"
      hv.management_network_address = "192.168.0.0/24"
    end

    machine.vm.provision :ansible do |ansible|
      ansible.limit = "all"
      ansible.playbook = "deploy/main.yml"
      ansible.config_file = "deploy/ansible.cfg"
    end
  end
end
