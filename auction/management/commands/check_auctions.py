from django.core.management.base import BaseCommand
from django.utils import timezone
from auction.models import Product
from auction.views import send_auction_result_emails

class Command(BaseCommand):
    help = 'Check for ended auctions and send result emails'

    def handle(self, *args, **options):
        ended_auctions = Product.objects.filter(
            end_time__lte=timezone.now(),
            is_active=True
        )
        
        for product in ended_auctions:
            if product.bids.exists():
                send_auction_result_emails(product)
                self.stdout.write(
                    self.style.SUCCESS(f'Sent result emails for: {product.title}')
                )
            
            product.is_active = False
            product.save()
        
        if not ended_auctions:
            self.stdout.write('No ended auctions found.')