# Netbox VM Context editor

Update the local config contexts of your Netbox VMs as YAML files directly in your file system.

## Usage

Save your netbox URL and API token to the variables `NETBOX_URL` and
`NETBOX_API_TOKEN` respetively. Alternatively they can be entered as CLI
parameters if you don't care about keeping them hidden.

Run `netbox-vm-context pull DIRECTORY`. The given directory will get one file
per virtual machine containing the local configuration context in YAML format.

Edit the files, and once done, run `netbox-vm-context check DIRECTORY` to check
which files would be updated, and finally `netbox-vm-context push` to push them
back to netbox.


## FAQ

### Q: Why?
Well, I was using the context to orchestrate Ansible variables, and I disliked
typing JSON into the webui, so I wrote this to be able to do it in my editor instead.

### Q: Why YAML?
JSON is not really so well-suited for direct editing as YAML is, and TOML is not
really intended to be converted back and forth between JSON, so YAML seemed
natural.

As I am primarily using this for Ansible, YAML seems like a good fit.

However, It's very easy to extend the code to use other formats, if anything
more suited should be required.
