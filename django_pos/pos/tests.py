from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

from products.models import Product, Category, Supplier, InventoryMovement
from customers.models import Customer
from sales.models import Sale, Payment
from core.models import ExchangeRate, PaymentMethod

# Import the function to be tested
from .views import _process_sale_data

class ProcessSaleTestCase(TestCase):

    def setUp(self):
        """
        Set up the necessary objects for testing the sale processing logic.
        This method runs before each test.
        """
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.exchange_rate = ExchangeRate.objects.create(date=timezone.now().date(), rate_usd_ves=Decimal('38.5'))
        self.payment_method = PaymentMethod.objects.create(name='Cash', is_foreign_currency=True)
        
        self.category = Category.objects.create(name='Test Category', description='Desc', status='ACTIVE', prefix='TC')
        self.supplier = Supplier.objects.create(name='Test Supplier')

        self.customer = Customer.objects.create(
            first_name='Test',
            last_name='Customer',
            outstanding_balance=Decimal('0.00')
        )

        self.product = Product.objects.create(
            name='Test Product',
            description='A product for testing',
            status='ACTIVE',
            category=self.category,
            supplier=self.supplier,
            price_usd=Decimal('100.00'),
            stock=10
        )

    def test_credit_sale_deducts_stock_and_updates_balance(self):
        """
        Verify that a credit sale correctly deducts product stock and
        updates the customer's outstanding balance.
        """
        # 1. Define the sale data, mimicking the JSON from the frontend
        sale_quantity = 2
        grand_total = self.product.price_usd * sale_quantity

        sale_data = {
            'customer': self.customer.id,
            'sub_total': str(grand_total),
            'grand_total': str(grand_total),
            'tax_amount': '0',
            'tax_percentage': '0',
            'amount_change': '0',
            'total_ves': '0',
            'igtf_amount': '0',
            'is_credit': True,
            'payments': [],
            'products': [
                {
                    'id': self.product.id,
                    'quantity': sale_quantity,
                    'price': str(self.product.price_usd),
                    'total_product': str(grand_total)
                }
            ]
        }

        # 2. Create a mock request object
        request = self.factory.post('/pos/')
        request.user = self.user

        # 3. Call the function to process the sale
        _process_sale_data(request, sale_data)

        # 4. Refresh the objects from the database to get the updated values
        self.product.refresh_from_db()
        self.customer.refresh_from_db()

        # 5. Assert the results
        self.assertEqual(self.product.stock, 8, "Stock should be deducted by 2")
        self.assertEqual(self.customer.outstanding_balance, grand_total, "Customer balance should be increased")
        created_sale = Sale.objects.first()
        self.assertEqual(created_sale.status, 'pending_credit')
        self.assertEqual(created_sale.customer, self.customer)

    def test_completed_sale_deducts_stock_and_creates_payment(self):
        """
        Verify that a completed sale correctly deducts stock, creates payment
        records, and creates an inventory movement.
        """
        # 1. Define sale data
        sale_quantity = 1
        grand_total = self.product.price_usd * sale_quantity
        sale_data = {
            'customer': self.customer.id,
            'sub_total': str(grand_total),
            'grand_total': str(grand_total),
            'tax_amount': '0',
            'tax_percentage': '0',
            'amount_change': '0',
            'total_ves': '0',
            'igtf_amount': '0',
            'is_credit': False,
            'payments': [
                {
                    'payment_method_id': self.payment_method.id,
                    'amount': str(grand_total),
                    'reference': 'test-ref-123'
                }
            ],
            'products': [
                {
                    'id': self.product.id,
                    'quantity': sale_quantity,
                    'price': str(self.product.price_usd),
                    'total_product': str(grand_total)
                }
            ]
        }

        # 2. Create mock request
        request = self.factory.post('/pos/')
        request.user = self.user

        # 3. Call the function
        _process_sale_data(request, sale_data)

        # 4. Refresh objects
        self.product.refresh_from_db()
        self.customer.refresh_from_db()

        # 5. Assertions
        self.assertEqual(self.product.stock, 9, "Stock should be deducted by 1")
        self.assertEqual(self.customer.outstanding_balance, 0, "Customer balance should not change")
        
        self.assertEqual(Sale.objects.count(), 1)
        sale = Sale.objects.first()
        self.assertEqual(sale.status, 'completed')

        self.assertTrue(Payment.objects.filter(sale=sale).exists(), "Payment record should be created")
        payment = Payment.objects.first()
        self.assertEqual(payment.amount, grand_total)

        self.assertTrue(InventoryMovement.objects.filter(product=self.product, movement_type='out').exists(), "InventoryMovement should be created")
