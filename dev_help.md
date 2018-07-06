DEBUG:
import ipdb; ipdb.set_trace()

---

http://libcloud.readthedocs.io/en/latest/apidocs/libcloud.compute.drivers.html#libcloud.compute.drivers.gce.GCESnapshot
class libcloud.compute.drivers.gce.GCESnapshot(id, name, size, status, driver, extra=None, created=None)

http://libcloud.readthedocs.io/en/latest/compute/api.html#libcloud.compute.base.VolumeSnapshot
class libcloud.compute.base.VolumeSnapshot(id, driver, size=None, extra=None, created=None, state=None, name=None)

id (str) – Snapshot ID.
driver (NodeDriver) – The driver that represents a connection to the provider
size (int) – A snapshot size in GB.
extra (dict) – Provider depends parameters for snapshot.
created (datetime.datetime) – A datetime object that represents when the snapshot was created
state (str) – A string representing the state the snapshot is in. See libcloud.compute.types.StorageVolumeState.
name (str) – A string representing the name of the snapshot

---

http://libcloud.readthedocs.io/en/latest/compute/api.html#libcloud.compute.base.StorageVolume
class libcloud.compute.base.StorageVolume(id, name, size, driver, state=None, extra=None)

id (str) – Storage volume ID.
name (str) – Storage volume name.
size (int) – Size of this volume (in GB).
driver (NodeDriver) – Driver this image belongs to.
state (StorageVolumeState) – Optional state of the StorageVolume. If not provided, will default to UNKNOWN.
extra (dict) – Optional provider specific attributes.

attach(node, device=None)
destroy()
detach()
list_snapshots()
snapshot(name)

---

https://docs.python.org/2/library/argparse.html
https://docs.python.org/2/library/logging.html
