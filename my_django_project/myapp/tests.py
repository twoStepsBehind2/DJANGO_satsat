from django.test import TestCase
from .models import RegisAcc

class RegisAccModelTest(TestCase):
    def setUp(self):
        self.regis_acc = RegisAcc.objects.create(
            # Add fields here based on the RegisAcc model definition
        )

    def test_regis_acc_creation(self):
        self.assertIsInstance(self.regis_acc, RegisAcc)

    def test_regis_acc_str(self):
        self.assertEqual(str(self.regis_acc), "Expected String Representation")  # Update with actual expected string representation

    # Add more tests as needed for other methods or properties of the RegisAcc model