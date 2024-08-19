sops_encrypt:
	sops encrypt -i playbooks/group_vars/all/config.sops.yml
sops_decrypt:
	sops decrypt -i playbooks/group_vars/all/config.sops.yml
sops_edit:
	sops edit playbooks/group_vars/all/config.sops.yml
