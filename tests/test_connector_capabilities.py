import unittest

from connectors.capabilities import capability_manifest, capability_support, validate_capability_manifest


class CapabilityManifestTests(unittest.TestCase):
    def test_versioned_manifest_preserves_explicit_support(self):
        manifest = capability_manifest("example", {
            "products.read": "supported",
            "prices.write": "unsupported",
        })
        self.assertEqual(manifest["manifest_version"], "1")
        self.assertEqual(capability_support(manifest, "products.read"), "supported")
        self.assertEqual(capability_support(manifest, "prices.write"), "unsupported")

    def test_absent_capability_is_unknown_not_unsupported(self):
        manifest = capability_manifest("example", {"products.read": "supported"})
        self.assertIsNone(capability_support(manifest, "inventory.read"))

    def test_invalid_support_and_extra_fields_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "invalid_capability_support"):
            capability_manifest("example", {"products.read": "maybe"})
        with self.assertRaisesRegex(ValueError, "invalid_capability_declaration"):
            validate_capability_manifest({
                "manifest_version": "1",
                "provider": "example",
                "capabilities": {"products.read": {"support": "supported", "note": "ambiguous"}},
            })

    def test_manifest_version_and_provider_are_not_inferred(self):
        with self.assertRaisesRegex(ValueError, "unsupported_capability_manifest_version"):
            validate_capability_manifest({"manifest_version": "2", "provider": "example", "capabilities": {"products.read": {"support": "supported"}}})
        with self.assertRaisesRegex(ValueError, "invalid_capability_provider"):
            capability_manifest("Example", {"products.read": "supported"})


if __name__ == "__main__":
    unittest.main()
