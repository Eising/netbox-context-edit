# Netbox Configuration Context editor

This script allows you to manage your netbox device's context directly in your
file system.

Instead of using the netbox UI to clumsily manage JSON in an HTML textfile, this
script will pull the local-context data for each of your nodes, convert it to
YAML and store it in a directory of your choosing.

Once done editing, you can then push the context back to netbox.

## Usage

``` 
$ netbox-manage-context --help
Usage: netbox-manage-context [OPTIONS] COMMAND [ARGS]...

  Manage netbox configuration contexts in your file system.

Options:
  -u, --url TEXT    Netbox URL
  -t, --token TEXT  Netbox API token
  --debug           Enable debugging.
  --help            Show this message and exit.

Commands:
  vm  Virtual machines
```

``` 
$ netbox-manage-context vm --help
Usage: netbox-manage-context vm [OPTIONS] COMMAND [ARGS]...

  Virtual machines

Options:
  --help  Show this message and exit.

Commands:
  check  Check for changes in the specified directory.
  pull   Pull config into the specified directory.
  push   Pull config into the specified directory.

```

### CLI command

The CLI command `netbox-manage-context` supports the verbs `pull`, `check` and
`push`.

At the time of writing, only virtual machines are supported, but the code is
implemented with simple strategy and factory methods that allows this to be
extended to any type of object in Netbox that has a `local-context-data`
attribute.

The verb `pull` populates the file system with the one file per node containing
the context data, `check` will give you a list of modified files, and `push`
will update netbox.

Note that `pull` will blindly overwrite any local file, so be careful not to
accidentally overwrite any files you may have edited and forgotten to push.

### Logging in to Netbox

You can save your netbox URL and API token in your environment by using the
variables `NETBOX_URL` and `NETBOX_API_TOKEN` respetively.

Alternatively you can pass them directly the command, if you don't care about
keeping them hidden.


Run `netbox-vm-context pull DIRECTORY`. The given directory will get one file
per virtual machine containing the local configuration context in YAML format.

Edit the files, and once done, run `netbox-vm-context check DIRECTORY` to check
which files would be updated, and finally `netbox-vm-context push` to push them
back to netbox.


## FAQ

### Q: Why do I need this?
This script can be part of a very simple GitOps like pipeline. If you check the
files created by this script into git, you can use it in a workflow to both
update netbox with changes, but also run for example an ansible playbook on
updates.

This is my own reason for creating it.

You may also just find the config context textfield in Netbox quite painful to
use, as it does nothing to help you write the JSON.

### Q: Why YAML?
JSON is not really so well-suited for direct editing as YAML is, and TOML is not
really intended to be converted back and forth between JSON, so YAML seemed
natural.

As I am primarily using this for Ansible, YAML seems like a good fit.

However, It's very easy to extend the code to use other formats, if anything
more suited should be required.


## TODO
I haven't written any tests yet. That's the first item on the agenda.

Since I have laid the groundwork for extending to any object with a
`local-context-data` attribute, I will add more types soon.
