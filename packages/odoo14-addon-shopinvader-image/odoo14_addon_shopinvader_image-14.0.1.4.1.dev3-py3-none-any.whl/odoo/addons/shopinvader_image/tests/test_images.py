# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest import mock

from odoo import fields

from .common import TestShopinvaderImageCase


class TestShopinvaderImage(TestShopinvaderImageCase):
    # TODO: test permission explicitely if needed

    def test_basic_images_compute(self):
        storage_backend = self.shopinvader_variant.image_ids.image_id.backend_id
        storage_backend.write(
            {
                "served_by": "external",
                "base_url": "https://foo.com",
            }
        )
        images = self.shopinvader_variant.images
        self.assertEqual(len(images), 2)
        for image in images:
            for scale in self.backend.shopinvader_variant_resize_ids:
                img = image[scale.key]
                self.assertEqual(img["alt"], self.shopinvader_variant.name)
                src = img["src"].replace("-_", "_")
                self.assertTrue(
                    src.startswith(
                        "https://foo.com/customizable-desk-config_{0.size_x}_{0.size_y}".format(
                            scale
                        )
                    )
                )

    def test_basic_images_compute_no_cdn_url(self):
        storage_backend = self.shopinvader_variant.image_ids.image_id.backend_id
        storage_backend.write(
            {
                "served_by": "external",
                "base_url": "https://foo.com",
            }
        )
        self.backend.image_data_include_cdn_url = False
        images = self.shopinvader_variant.images
        self.assertEqual(len(images), 2)
        for image in images:
            for scale in self.backend.shopinvader_variant_resize_ids:
                img = image[scale.key]
                self.assertEqual(img["alt"], self.shopinvader_variant.name)
                src = img["src"].replace("-_", "_")
                self.assertTrue(
                    src.startswith(
                        "/customizable-desk-config_{0.size_x}_{0.size_y}".format(scale)
                    )
                )

    def test_image_metadata(self):
        self.shopinvader_variant.invalidate_cache(["images"])
        self.shopinvader_variant[0].image_ids[0].image_id.alt_name = "Test Alt Name"
        images = self.shopinvader_variant.images
        for scale in self.backend.shopinvader_variant_resize_ids:
            img = images[0][scale.key]
            self.assertEqual(img["alt"], "Test Alt Name")
            self.assertNotIn("tag", img)
        for scale in self.backend.shopinvader_variant_resize_ids:
            img = images[1][scale.key]
            # Fallback to product name
            self.assertEqual(img["alt"], self.shopinvader_variant.name)
            self.assertNotIn("tag", img)
        # allow empty alt
        self.shopinvader_variant.backend_id.image_data_empty_alt_name_allowed = True
        self.shopinvader_variant.invalidate_cache(["images"])
        images = self.shopinvader_variant.images
        for scale in self.backend.shopinvader_variant_resize_ids:
            img = images[1][scale.key]
            # NO Fallback to product name
            self.assertNotIn("alt", img)
        self.shopinvader_variant.invalidate_cache(["images"])
        # value tags
        with mock.patch.object(
            type(self.shopinvader_variant), "_get_image_tag"
        ) as mocked:
            mocked.return_value = "Test Tag"
            # enforce compute to get the tag
            # because the field is not there and the hash won't change
            self.shopinvader_variant._compute_images_stored()
            self.shopinvader_variant.invalidate_cache(["images"])
            images = self.shopinvader_variant.images
            for scale in self.backend.shopinvader_variant_resize_ids:
                img = images[0][scale.key]
                self.assertEqual(img["tag"], "Test Tag")
                img = images[1][scale.key]
                self.assertEqual(img["tag"], "Test Tag")

    def test_hash_and_compute_flag(self):
        variant = self.shopinvader_variant
        self.assertFalse(variant.images_store_hash)
        self.assertTrue(variant._images_must_recompute())
        variant.images_store_hash = variant._get_images_store_hash()
        self.assertFalse(variant._images_must_recompute())
        # change hash by changing scale
        self.backend.shopinvader_variant_resize_ids[0].key = "very-small"
        self.assertTrue(variant._images_must_recompute())
        variant.images_store_hash = variant._get_images_store_hash()
        # NOTE: write_date, used to compute the hash, uses sql NOW() to recompute
        #       and it always corresponds to the time the transaction started.
        #       To overcome this, we manually overwrite write_date
        now = fields.Datetime.now()
        with mock.patch.object(
            type(variant.image_ids), "write_date", new_callable=mock.PropertyMock
        ) as mocked:
            mocked.return_value = now
            variant.images_store_hash = variant._get_images_store_hash()
            # Change hash when relation is updated
            mocked.return_value = now + timedelta(seconds=100)
            # variant.image_ids[0].write_date = now + timedelta(seconds=1)
            self.assertTrue(variant._images_must_recompute())
            variant.images_store_hash = variant._get_images_store_hash()
        with mock.patch.object(
            type(variant.image_ids.image_id),
            "write_date",
            new_callable=mock.PropertyMock,
        ) as mocked:
            mocked.return_value = now + timedelta(seconds=2)
            self.assertTrue(variant._images_must_recompute())
            variant.images_store_hash = variant._get_images_store_hash()
            # Change hash when tag is updated
        tag = self.env.ref("shopinvader_image.image_tag_1")
        variant.image_ids[0].tag_id = tag
        variant.images_store_hash = variant._get_images_store_hash()
        with mock.patch.object(
            type(variant.image_ids.tag_id), "write_date", new_callable=mock.PropertyMock
        ) as mocked:
            mocked.return_value = now + timedelta(seconds=3)
            self.assertTrue(variant._images_must_recompute())
            variant.images_store_hash = variant._get_images_store_hash()

    def test_images_recompute(self):
        variant = self.shopinvader_variant
        self.assertTrue(variant._images_must_recompute())
        with mock.patch.object(type(variant), "_get_image_data_for_record") as mocked:
            mocked.return_value = [{"a": 1, "b": 2}]
            self.assertEqual(variant.images, [{"a": 1, "b": 2}])
            mocked.assert_called()

        variant.invalidate_cache(["images"])
        self.assertFalse(variant._images_must_recompute())
        with mock.patch.object(type(variant), "_get_image_data_for_record") as mocked:
            mocked.return_value = [{"c": 3, "d": 4}]
            # same value as before
            self.assertEqual(variant.images, [{"a": 1, "b": 2}])
            mocked.assert_not_called()

        # simulate change in image scale
        self.backend.shopinvader_variant_resize_ids[0].key = "very-small"
        variant.invalidate_cache(["images"])
        self.assertTrue(variant._images_must_recompute())
        with mock.patch.object(type(variant), "_get_image_data_for_record") as mocked:
            mocked.return_value = [{"c": 3, "d": 4}]
            # recomputed
            self.assertEqual(variant.images, [{"c": 3, "d": 4}])
            mocked.assert_called()

        # Simulate base URL change
        self.assertFalse(variant._images_must_recompute())
        random_image = variant.variant_image_ids[0].image_id
        # test backend serves images via odoo base url
        self.env["ir.config_parameter"].sudo().set_param(
            "web.base.url", "https://foo.com"
        )
        random_image.invalidate_cache()
        self.assertTrue(variant._images_must_recompute())
