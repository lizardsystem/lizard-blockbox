from django.test import TestCase


from lizard_blockbox import views

from . import factories


class TestSelectedProtectionLevel(TestCase):
    def test_normal_vertex_is_1250(self):
        self.assertEqual(
            views._selected_protection_level(
                factories.VertexFactory.build()),
            "1250")

    def test_other_name_can_give_250(self):
        self.assertEqual(
            views._selected_protection_level(
                factories.VertexFactory.build(name="Maas 1:250 golf")),
            "250")
