import json
import os
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from ftpkit import AppManifest, Capability, ChangeAction, ChangeItem, ChangePlan, FileLock, IntegrityError, Registry, RegistryEntry, RegistryStore, RiskLevel, ValidationError, atomic_write_json, format_fingerprint, instance_path, new_instance_uuid, safe_path, sha256_bytes, utc_now, validate_app_id, validate_domain, validate_ip, validate_port, validate_url_path, validate_uuid

class FtpkitTest(unittest.TestCase):
    def test_validators_and_paths(self):
        uid = new_instance_uuid(); self.assertTrue(validate_uuid(uid)); self.assertFalse(validate_uuid("bad"))
        self.assertEqual(validate_app_id("csv-reporting"), "csv-reporting")
        self.assertEqual(validate_domain("Example.COM."), "example.com")
        self.assertEqual(validate_ip("2001:0db8::1"), "2001:db8::1")
        self.assertEqual(validate_port("443"), 443)
        self.assertEqual(validate_url_path("/csv-reporting/"), "/csv-reporting")
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); child=root/"a"; self.assertEqual(safe_path(child, roots=[root]), child.resolve())
            with self.assertRaises(ValidationError): safe_path(root.parent, roots=[root])
            self.assertEqual(instance_path(root, "demo-app", uid).name, f"demo-app-{uid}")

    def test_atomic_io_and_lock(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"v.json"; atomic_write_json(path,{"a":1}); atomic_write_json(path,{"a":2},backup=True)
            self.assertEqual(json.loads(path.read_text()),{"a":2}); self.assertEqual(json.loads(path.with_suffix('.json.bak').read_text()),{"a":1})
            self.assertEqual(os.stat(path).st_mode & 0o777,0o600)
            lock=FileLock(Path(d)/"lock"); self.assertIs(lock.acquire(),lock); self.assertIs(lock.acquire(),lock); lock.release()

    def test_manifest_and_plan(self):
        manifest=AppManifest("demo-app","Demo App","1.2.3",1,1,"python",("python","-m","demo"),"/health",("data","frontend","backend","srv"),("data",),frozenset({Capability.STATUS,Capability.HEALTH}))
        self.assertEqual(AppManifest.from_dict(manifest.to_dict()),manifest)
        plan=ChangePlan(uuid4(),"demo-app",uuid4(),"install",RiskLevel.HIGH,(ChangeItem(ChangeAction.INSTALL,"service","demo.service","install",True),))
        self.assertTrue(plan.confirmation_required)

    def test_registry(self):
        now=utc_now(); uid=uuid4(); base=f"/sites/demo-app-{uid}"
        entry=RegistryEntry("demo-app",uid,"Demo App","1.0.0",1,base,base+"/data",base+"/frontend",base+"/backend",base+"/srv","/sites/backend/data/backups",f"demo-{uid}.service","demo-user","127.0.0.1",None,base+"/srv/app.sock",8443,"https://example.test:8443/","/","internal",frozenset({Capability.STATUS,Capability.HEALTH}),now,now,{})
        with tempfile.TemporaryDirectory() as d:
            store=RegistryStore(Path(d)/"registry.json"); registry=Registry.empty().with_entry(entry); store.save(registry)
            self.assertEqual(store.load().to_dict(),registry.to_dict())
            with self.assertRaises(IntegrityError): store.save(registry,expected_revision=99)

    def test_crypto(self):
        digest=sha256_bytes(b"abc"); self.assertEqual(digest,"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(len(format_fingerprint(digest).split(":")),32)

if __name__ == "__main__": unittest.main()
